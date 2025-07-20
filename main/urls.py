from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    #visão admin
    path('', EventsListView.as_view(), name='events_list'),
    path('event/create/', EventCreateView.as_view(), name='create_event'),
    path('event/<int:event_id>/edit/', EventUpdateView.as_view(), name='edit_event'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='delete_event'),

    path('event/<int:event_id>/sector/add/', SectorCreateView.as_view(), name='create_sector'),
    path('sector/<int:sector_id>/edit/', SectorUpdateView.as_view(), name='edit_sector'),
    path('sector/<int:pk>/delete/', SectorDeleteView.as_view(), name='delete_sector'),


    
    
    path('event/', views.EventView, name='event'),
    path('login/', views.LoginView, name='login'),
    path('dashboard/', views.EventDashboardView, name='dashboard'),

]

#configuração para trabalhar com imagens
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)