# CODE v2.0 pour gestion/admin.py

from django.contrib import admin
from .models import Ville, Station, Velo, Location, Utilisateur, TicketSupport

admin.site.register(Ville)
admin.site.register(Station)
admin.site.register(Velo)
admin.site.register(Location)
admin.site.register(Utilisateur)
admin.site.register(TicketSupport)