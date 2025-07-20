from django.shortcuts import render, get_object_or_404
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
            return redirect('events_list')
    else:
        event_form = EventForm()
        address_form = EventAdressForm()

    return render(request, 'main/event_form.html', {
        'event_form': event_form,
        'address_form': address_form
    })


def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    address = getattr(event, 'eventadress', None)

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)
        address_form = EventAdressForm(request.POST, instance=address)

        if event_form.is_valid() and address_form.is_valid():
            event = event_form.save()
            address = address_form.save(commit=False)
            address.event = event
            address.save()
            return redirect('events_list')
    else:
        event_form = EventForm(instance=event)
        address_form = EventAdressForm(instance=address)

    return render(request, 'main/event_form.html', {
        'event_form': event_form,
        'address_form': address_form
    })


def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('/')




#---------------------------------


def EventView(request):
    return render(request, 'main/event.html')

def LoginView(request):
    return render(request, 'login.html')


def EventDashboardView(request):
    return render(request, 'main/dashboard.html')