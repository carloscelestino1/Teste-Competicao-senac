from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, EventAdress, Sector
from .forms import EventForm, EventAdressForm, SectorForm
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
import uuid



from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from .models import Event, Sector, Ticket

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Event

@login_required
def event_router_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

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



#---------------------------------


def EventDashboardView(request):
    return render(request, 'main/dashboard.html')