from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import *

def EventsView(request):
    events_list = Event.objects.all().order_by('-date')
    return render(request, 'main/show-events.html', {'events_list': events_list})

def create_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        address_form = EventAdressForm(request.POST)

        if event_form.is_valid() and address_form.is_valid():
            event = event_form.save()
            address = address_form.save(commit=False)
            address.event = event
            address.save()

            # Redireciona para adicionar o primeiro setor
            return redirect('create_sector', event_id=event.id)
    else:
        event_form = EventForm()
        address_form = EventAdressForm()

    return render(request, 'main/event_form.html', {
        'event_form': event_form,
        'address_form': address_form,
        'creating': True  # 🔑 Passa variável para template
    })



def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    address = EventAdress.objects.filter(event_id=event).first()
    address_form = EventAdressForm(instance=address)
    event_form = EventForm(instance=event)

    if request.method == "POST":
        event_form = EventForm(request.POST, request.FILES, instance=event)
        address_form = EventAdressForm(request.POST, instance=address)
        if event_form.is_valid() and address_form.is_valid():
            event_form.save()
            address_instance = address_form.save(commit=False)
            address_instance.Event_id = event
            address_instance.save()
            return redirect('events_list')

    sectors = Sector.objects.filter(Event_id=event)

    return render(request, 'main/event_form.html', {
        'event_form': event_form,
        'address_form': address_form,
        'sectors': sectors
    })


def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('/')














def create_sector(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = SectorForm(request.POST, event=event)
        if form.is_valid():
            sector = form.save(commit=False)
            sector.Event_id = event  # ✅ Correção aqui
            #sector.full_clean()
            sector.save()
            return redirect('edit_event', event_id=event.id)
    else:
        form = SectorForm()

    return render(request, 'main/sector_form.html', {
        'form': form,
        'event': event
    })




def edit_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    event = sector.Event_id

    if request.method == "POST":
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            updated_sector = form.save(commit=False)
            total_capacity = sum(s.max_capacity for s in Sector.objects.filter(Event_id=event).exclude(id=sector.id))
            if total_capacity + updated_sector.max_capacity > event.max_capacity:
                form.add_error('max_capacity', 'Capacidade total dos setores excede a capacidade do evento.')
            else:
                updated_sector.save()
                return redirect('edit_event', event_id=event.id)
    else:
        form = SectorForm(instance=sector)

    return render(request, 'main/sector_form.html', {'form': form, 'event': event})


def delete_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    event_id = sector.Event_id.id
    sector.delete()
    return redirect('edit_event', event_id=event_id)



#---------------------------------


def EventView(request):
    return render(request, 'main/event.html')

def LoginView(request):
    return render(request, 'login.html')


def EventDashboardView(request):
    return render(request, 'main/dashboard.html')