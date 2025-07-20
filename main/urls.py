from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventsView, name='events-list'),
    path('event/', views.EventView, name='event'),
    path('login/', views.LoginView, name='login'),
    path('event-config/', views.EventConfigView, name='event-config'),
    path('dashboard/', views.EventDashboardView, name='dashboard')
]
