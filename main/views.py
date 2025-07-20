from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from .models import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def EventsView(request):
    events_list = Event.objects.all()
    return render(request, 'main/show-events.html')

def EventView(request):
    return render(request, 'main/event.html')

def LoginView(request):
    return render(request, 'login.html')

def EventConfigView(request):
    return render(request, 'main/event-config.html')

def EventDashboardView(request):
    return render(request, 'main/dashboard.html')