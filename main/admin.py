from django.contrib import admin
from .models import *

admin.site.register(Event)
admin.site.register(EventAdress)
admin.site.register(Sector)
admin.site.register(Seat)
admin.site.register(Ticket)