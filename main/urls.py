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
    path('event/<int:event_id>/', event_router_view, name='event_router'),
    path('event/<int:event_id>/sector/add/', SectorCreateView.as_view(), name='create_sector'),
    path('sector/<int:sector_id>/edit/', SectorUpdateView.as_view(), name='edit_sector'),
    path('sector/<int:pk>/delete/', SectorDeleteView.as_view(), name='delete_sector'),
    path('event/<int:event_id>/acesso/', event_router_view, name='event_access'),
    path('event/<int:event_id>/dashboard/', views.EventDashboardView.as_view(), name='event_dashboard'),
    path('event/<int:event_id>/validar-ingresso/', TicketValidationView.as_view(), name='validar_ingresso'),

    #visão vendedor
    path('event/<int:event_id>/venda/', VendaIngressosView.as_view(), name='venda_ingressos'),

]

#configuração para trabalhar com imagens
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)