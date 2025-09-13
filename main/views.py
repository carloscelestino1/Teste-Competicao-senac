from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
import uuid
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from datetime import date
from django.views.generic import TemplateView, ListView, DeleteView


@login_required
def event_router_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.is_supersuper():
        return redirect('edit_event', event_id=event.id)
    if request.user.groups.filter(name__iexact='validadores').exists():
        return redirect('validar_ingressos', event_id=event.id)
    if request.user.groups.filter(name__iexact='vendedores').exists():
        return redirect('venda_ingressos', event_id=event.id)
    else:
        return redirect('/', event_id=event.id)


#CRUD EVENTO:
class EventsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'main/show-event.html'
    context_object_name = 'events_list'
    ordering = ['-date']


class EventDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        setores_associados = Sector.objects.filter(Event_id=event)
        return render(request, 'main/event_confirm_delete.html',{
            'event': event,
            'setores': setores_associados
        })
    
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return redirect('events_list')
    

class EventCreateView(LoginRequiredMixin, View):
    def get(self, request):
        event_form = EventForm()
        address_form = EventAddressForm()
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'creating': True
        })
    
    
    def post(self, request):
        event_form = EventForm(request.POST, request.FILES)
        address_form = EventAddressForm(request.POST)
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
        address = EventAddress.objects.filter(event_id=event).first()
        event_form = EventForm(instance=event)
        address_form = EventAddressForm(instance=address)
        sectors = Sector.objects.filter(Event_id=event)
        return render(request, 'main/event_form.html', {
            'event_form': event_form,
            'address_form': address_form,
            'sectors': sectors
        })
    

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        address = EventAddress.objects.filter(event_id=event).first()
        event_form = EventForm(request.POST, request.FILES, instance=event)
        address_form = EventAddressForm(request.POST, instance=address)
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
    

class SectorDeleteView(LoginRequiredMixin, DeleteView):
    model = Sector

    def get_success_url(self):
        return reverse_lazy('edit_event', kwargs={'event_id': self.object.Event_id.id})
    


class SectorCreateView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        form = SectorForm()
        return render(request, 'main/sector_form.html', {
            'event': event,
            'form': form
        })
    
    
    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        form = SectorForm(request.POST)
        
        if form.is_valid():
            sector = form.save(commit=False)
            sector.Event_id = event

            total_capacity = sum(
                s.max_capacity for s in Sector.objects.filter(Event_id=event)
            )

            if total_capacity + sector.max_capacity > event.max_capacity:
                form.add_error('max_capacity', f'A capacidade total dos setores {total_capacity + sector.max_capacity} excede a capacidade máxima do evento')

            else:
                sector.save()
                return redirect('edit_event', event_id=event.id)
        return render(request, 'main/sector_form.html', {
            'event': event,
            'form': form
        })   
    


class SectorUpdateView(LoginRequiredMixin, View):
    def get(self, request, sector_id):
        sector = get_object_or_404(Sector, pk=sector_id)
        form = SectorForm(instance=sector)
        return render(request, 'main/sector_form.html', {
            'event': sector.Event_id,
            'form': form
        })
    

    def post(self, request, sector_id):
        sector = get_object_or_404(Sector, pk=sector_id)
        form = SectorForm(request.POST, instance=sector)

        if form.is_valid():
            updated_sector = form.save(commit=False)

            total_capacity = sum(
                s.max_capacity for s in Sector.objects.filter(Event_id=sector.Event_id).exclude(id=sector.id)
            )

            if total_capacity + updated_sector.max_capacity > sector.Event_id.max_capacity:
                form.add_error('max_capacity', f'A capacidade total dos Setores Excede a capacidade máxima do Evento')
            else:
                updated_sector.save()
                return redirect('edit_event', event_id=sector.Event_id.id)
        return render(request, 'main/sector_form.html', {
            'event': sector.Event_id,
            'form': form
        })
    


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

        nome_cliente = request.POST.get('nome_cliente')
        cpf_cliente = request.POST.get('cpf_cliente')
        email_cliente = request.POST.get('email_cliente')

        for setor in setores:
            quantidade = int(request.POST.get(f'setor_{setor.id}', 0))
            capacidade = capacidade_disponivel[setor.id]

            if quantidade > capacidade:
                continue

            for _ in range(quantidade):
                Ticket.objects.create(
                    ticket_code = uuid.uuid4(),
                    Event_id = event,
                    User_cpf = request.user.username,
                    sector_id=setor.id,
                    nome_cliente = nome_cliente,
                    cpf_cliente = cpf_cliente,
                    email_cliente = email_cliente
                )



class TicketValidationView(LoginRequiredMixin, View):
    template_name = 'main/ticket_validation.html'
    form_class = TicketValidationForm

    def get(self, request, event_id):
        if not request.user.groups.filter(name__iexact='validadores').exists():
            return redirect('events_list')
        
        form = self.form_class()
        event = get_object_or_404(Event, id=event_id)
        return render(request, self.template_name, {
            'event': event,
            'form': form
        })


    def post(self, request, event_id):
        if not request.user.groups.filter(name__iexact='validadores').exists():
            return redirect('events_list')
        
        form = self.form_class(request.POST)
        event = get_object_or_404(Event, id=event_id)
        validation_resutl = None

        if form.is_valid:
            ticket_code = form.cleaned_data['ticket_code']
            ticket = Ticket.objects.filter(ticket_code=ticket_code, Event_id=event).first()

            if not ticket:
                validation_resutl = 'O ingresso não foi encontrado no Evento'
            elif ticket.status == 'realizado':
                validation_resutl = 'O ingresso já foi validado'
            elif ticket.date() != date.today():
                validation_resutl =  'O ingresso Não é validado para hoje'
            else:
                ticket.save()
                ticket.status = 'realizado'
                validation_resutl = 'Ingresso validado com sucesso'
        event = get_object_or_404(Event, id=event_id)
        return render(request, self.template_name, {
            'event': event,
            'form': form,
            'validation_result': validation_resutl
        })
    


class EventTicketsListView(LoginRequiredMixin, ListView):
    model =  Ticket
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



class EventDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)

        setor_id = request.GET.get('setor')

        setores = Sector.objects.filter(Event_id=event)
        tickets_qs = Ticket.objects.filter(Event_id=event)

        # Se filtrar por setor
        if setor_id:
            setores = setores.filter(id=setor_id)
            tickets_qs = tickets_qs.filter(sector_id=setor_id)

        
        total_maximo = sum(s.max_capacity for s in setores)
        total_emitidos = tickets_qs.count()
        total_realizados = tickets_qs.filter(status='realizado').count()
        total_disponveis = total_maximo - total_emitidos
        total_pendentes = tickets_qs.filter(status='pendente').count()

       
        labels_setor = []
        data_setor = []

        percentuais_pendentes = []
        percentuais_realizados = []

        for setor in setores:
            vendidos = tickets_qs.filter(sector_id=setor.id).count()
            pendentes = tickets_qs.filter(sector_id=setor.id, status='pendente').count()
            realizados = tickets_qs.filter(sector_id=setor.id, status='realizado').count()
            capacidade = setor.max_capacity or 1

            labels_setor.append(setor.title)
            data_setor.append(vendidos)
            percentuais_pendentes.append(round((pendentes / capacidade) * 100, 2))
            percentuais_realizados.append(round((realizados / capacidade) * 100, 2))

        context.update({
            'event': event,
            'setores': setores,
            'eventos': Event.objects.all(),
            'total_pendentes': total_pendentes,
            'total_realizados': total_realizados,
            'emitidos': total_emitidos,
            'disponiveis': total_disponveis,
            'realizados': total_realizados,
            'percent_emitidos': round((total_emitidos / total_maximo) * 100, 2) if total_maximo else 0,
            'percent_disponiveis': round((total_disponveis / total_maximo) * 100, 2) if total_maximo else 0,
            'labels_setor': labels_setor,
            'data_setor': data_setor,
            'percentuais_pendentes': percentuais_pendentes,
            'percentuais_realizados': percentuais_realizados,
        })

        return context
