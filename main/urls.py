from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    #visão admin
    path('', EventsView, name='events_list'), #ver todos os eventos
    path('event/create/', create_event, name='create_event'), #criar eventos
    path('event/<int:event_id>/edit/', edit_event, name='edit_event'), #editar eventos
    path('event/<int:event_id>/delete/', delete_event, name='delete_event'), #deletar eventos
    
    path('event/<int:event_id>/sector/add/', create_sector, name='create_sector'),
    path('sector/<int:sector_id>/edit/', edit_sector, name='edit_sector'),
    path('sector/<int:sector_id>/delete/', delete_sector, name='delete_sector'),

    
    
    path('event/', views.EventView, name='event'),
    path('login/', views.LoginView, name='login'),
    path('dashboard/', views.EventDashboardView, name='dashboard'),

]

#configuração para trabalhar com imagens
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)