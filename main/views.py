from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, EventAdress, Sector
from .forms import EventForm, EventAdressForm, SectorForm, TicketValidationForm
from django.views import View
import uuid
from django.contrib.auth.decorators import login_required
from .models import Event, Sector, Ticket
from datetime import date


@login_required
@login_required
def event_router_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.groups.filter(name__iexact='validador').exists():
        return redirect('validar_ingresso', event_id=event.id)

    if request.user.groups.filter(name__iexact='vendedor').exists():
        return redirect('venda_ingressos', event_id=event.id)

    return redirect('edit_event', event_id=event.id)



# CRUD de Eventos

class EventsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'main/show-events.html'
    context_object_name = 'events_list'
    ordering = ['-date']


class EventCreateView(LoginRequiredMixin, View):
    def get(self, request):
        event_form = EventForm()
        address_form = EventAdressForm()
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'creating': True
        })

    def post(self, request):
        event_form = EventForm(request.POST, request.FILES)
        address_form = EventAdressForm(request.POST)
        if event_form.is_valid() and address_form.is_valid():
            event = event_form.save()
            address = address_form.save(commit=False)
            address.event = event
            address.save()
            return redirect('create_sector', event_id=event.id)
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'creating': True
        })


class EventUpdateView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        address = EventAdress.objects.filter(event_id=event).first()
        event_form = EventForm(instance=event)
        address_form = EventAdressForm(instance=address)
        sectors = Sector.objects.filter(Event_id=event)
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'sectors': sectors
        })

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        address = EventAdress.objects.filter(event_id=event).first()
        event_form = EventForm(request.POST, request.FILES, instance=event)
        address_form = EventAdressForm(request.POST, instance=address)
        if event_form.is_valid() and address_form.is_valid():
            event_form.save()
            address_instance = address_form.save(commit=False)
            address_instance.event = event
            address_instance.save()
            return redirect('events_list')
        sectors = Sector.objects.filter(Event_id=event)
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'sectors': sectors
        })


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('events_list')


# CRUD de Setores

class SectorCreateView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        form = SectorForm()
        return render(request, 'main/sector_form.html', {
            'form': form,
            'event': event
        })

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        form = SectorForm(request.POST)
        if form.is_valid():
            sector = form.save(commit=False)
            sector.Event_id = event
            sector.save()
            return redirect('edit_event', event_id=event.id)
        return render(request, 'main/sector_form.html', {
            'form': form,
            'event': event
        })


class SectorUpdateView(LoginRequiredMixin, View):
    def get(self, request, sector_id):
        sector = get_object_or_404(Sector, pk=sector_id)
        form = SectorForm(instance=sector)
        return render(request, 'main/sector_form.html', {
            'form': form,
            'event': sector.Event_id
        })

    def post(self, request, sector_id):
        sector = get_object_or_404(Sector, pk=sector_id)
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            updated_sector = form.save(commit=False)
            total_capacity = sum(s.max_capacity for s in Sector.objects.filter(Event_id=sector.Event_id).exclude(id=sector.id))
            if total_capacity + updated_sector.max_capacity > sector.Event_id.max_capacity:
                form.add_error('max_capacity', 'Capacidade total dos setores excede a capacidade do evento.')
            else:
                updated_sector.save()
                return redirect('edit_event', event_id=sector.Event_id.id)
        return render(request, 'main/sector_form.html', {
            'form': form,
            'event': sector.Event_id
        })


class SectorDeleteView(LoginRequiredMixin, DeleteView):
    model = Sector

    def get_success_url(self):
        return reverse_lazy('edit_event', kwargs={'event_id': self.object.Event_id.id})


class VendaIngressosView(LoginRequiredMixin, View):
    template_name = 'main/event.html'

    def get_event_and_setores(self, event_id):
        event = get_object_or_404(Event, id=event_id)
        setores = Sector.objects.filter(Event_id=event)

        vendidos_por_setor = {
            setor.id: Ticket.objects.filter(Event_id=event, sector_id=setor.id).count()
            for setor in setores
        }

        capacidade_disponivel = {
            setor.id: setor.max_capacity - vendidos_por_setor.get(setor.id, 0)
            for setor in setores
        }

        return event, setores, capacidade_disponivel

    def get(self, request, event_id):
        event, setores, capacidade_disponivel = self.get_event_and_setores(event_id)

        context = {
            'event': event,
            'setores': setores,
            'disponibilidades': capacidade_disponivel
        }
        return render(request, self.template_name, context)

    def post(self, request, event_id):
        event, setores, capacidade_disponivel = self.get_event_and_setores(event_id)

        for setor in setores:
            quantidade = int(request.POST.get(f'setor_{setor.id}', 0))
            capacidade = capacidade_disponivel[setor.id]

            if quantidade > capacidade:
                continue  # aqui você pode adicionar mensagens de erro com messages.error

            for _ in range(quantidade):
                Ticket.objects.create(
                    ticket_code=uuid.uuid4(),
                    Event_id=event,
                    User_cpf=request.user.username,
                    sector_id=setor.id
                )

        return redirect('venda_ingressos', event_id=event.id)


class TicketValidationView(LoginRequiredMixin, View):
    template_name = 'main/ticket_validation.html'
    form_class = TicketValidationForm

    def get(self, request, event_id):
        if not request.user.groups.filter(name__iexact='validador').exists():
            return redirect('events_list')

        form = self.form_class()
        event = get_object_or_404(Event, id=event_id)
        return render(request, self.template_name, {
            'form': form,
            'event': event
        })

    def post(self, request, event_id):
        if not request.user.groups.filter(name__iexact='validador').exists():
            return redirect('events_list')

        form = self.form_class(request.POST)
        validation_result = None
        event = get_object_or_404(Event, id=event_id)

        if form.is_valid():
            ticket_code = form.cleaned_data['ticket_code']
            ticket = Ticket.objects.filter(ticket_code=ticket_code, Event_id=event).first()

            if not ticket:
                validation_result = "Ingresso não encontrado para este evento."
            elif ticket.status == 'realizado':
                validation_result = "Ingresso já foi validado."
            elif ticket.Event_id.date != date.today():
                validation_result = "O ingresso não é válido para hoje."
            else:
                ticket.status = 'realizado'
                ticket.save()
                validation_result = "✅ Ingresso validado com sucesso."

        return render(request, self.template_name, {
            'form': form,
            'validation_result': validation_result,
            'event': event
        })


class EventDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)

        # Filtros GET
        setor_id = request.GET.get('setor')

        setores = Sector.objects.filter(Event_id=event)
        tickets_qs = Ticket.objects.filter(Event_id=event)

        # Filtro por setor
        if setor_id:
            tickets_qs = tickets_qs.filter(sector_id=setor_id)
            setores = setores.filter(id=setor_id)  # reduz visual dos gráficos

        total_maximo = sum(s.max_capacity for s in setores)
        total_emitidos = tickets_qs.count()
        total_validados = tickets_qs.filter(status='realizado').count()
        total_disponiveis = total_maximo - total_emitidos

        # Disponibilidades por setor
        disponibilidades = {}
        labels = []
        percentuais_pendentes = []
        percentuais_realizados = []

        for setor in setores:
            vendidos = tickets_qs.filter(sector_id=setor.id).count()
            pendentes = tickets_qs.filter(sector_id=setor.id, status='pendente').count()
            realizados = tickets_qs.filter(sector_id=setor.id, status='realizado').count()
            capacidade = setor.max_capacity or 1

            labels.append(setor.title)
            percentuais_pendentes.append(round((pendentes / capacidade) * 100, 2))
            percentuais_realizados.append(round((realizados / capacidade) * 100, 2))
            total_pendentes = tickets_qs.filter(status='pendente').count()
            total_realizados = tickets_qs.filter(status='realizado').count()


            context.update({
                'event': event,
                'labels': labels,
                'setores': Sector.objects.filter(Event_id=event),
                'eventos': Event.objects.all(),
                'disponibilidades': disponibilidades,
                'emitidos': total_emitidos,
                'validados': total_validados,
                'disponiveis': total_disponiveis,
                'percent_disponiveis': round((total_disponiveis / total_maximo) * 100, 2) if total_maximo else 0,
                'percent_emitidos': round((total_emitidos / total_maximo) * 100, 2) if total_maximo else 0,
                'percentuais_pendentes': percentuais_pendentes,
                'percentuais_realizados': percentuais_realizados,
                'total_pendentes': total_pendentes,
                'total_realizados': total_realizados,
            })

        return context



class EventTicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'main/event_tickets_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Ticket.objects.filter(Event_id=event_id).select_related('sector')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(pk=self.kwargs['event_id'])
        return context
    


def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    return render(request, 'main/ticket_detail.html', {'ticket': ticket})
