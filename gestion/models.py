# CODE v2.0 SPÉCIAL MIGRATION pour gestion/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Ville(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nom

class Station(models.Model):
    nom = models.CharField(max_length=200)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='stations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self): return f"{self.nom} ({self.ville.nom})"

class Velo(models.Model):
    station_origine = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='velos_originaires', null=True)
    station_actuelle = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name='velos_actuels')
    batterie = models.FloatField(default=100.0)
    class StatutVelo(models.TextChoices):
        DISPONIBLE = 'DISPO', 'Disponible'
        EN_LOCATION = 'LOC', 'En location'
        MAINTENANCE = 'MAINT', 'En maintenance'
    statut = models.CharField(max_length=5, choices=StatutVelo.choices, default=StatutVelo.DISPONIBLE)
    def __str__(self): return f"Vélo ID_{self.id}"

class Location(models.Model):
    velo = models.ForeignKey(Velo, on_delete=models.CASCADE, related_name='locations')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    station_depart = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='departs_location')
    station_arrivee = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='arrivees_location')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    def __str__(self): return f"Vélo {self.velo.id} de {self.station_depart.nom} à {self.station_arrivee.nom}"

class TicketSupport(models.Model):
    class TypeProbleme(models.TextChoices):
        BATTERIE_FAIBLE = 'BATTERIE', 'Batterie faible'
        FREINAGE = 'FREIN', 'Problème de freinage'
        STATIONNEMENT = 'STATION', 'Vélo mal stationné'
        AUTRE = 'AUTRE', 'Autre'
    velo = models.ForeignKey(Velo, on_delete=models.SET_NULL, null=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    type_probleme = models.CharField(max_length=10, choices=TypeProbleme.choices)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Ticket {self.id} - {self.get_type_probleme_display()}"

class Utilisateur(AbstractUser):
    pass