# CODE FINAL v2.2 (500 utilisateurs, période complète) pour gestion/management/commands/generate_history.py

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from faker import Faker

from gestion.models import Velo, Station, Location, Utilisateur, Ville, TicketSupport
from gestion.weather_service import MockWeatherService


class Command(BaseCommand):
    help = "Génère 500 utilisateurs de test et un historique de locations complet."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Début de la simulation complète (v2.2 - 500 utilisateurs, période complète)..."))

        # --- ÉTAPE 1 : Nettoyage des anciennes données de simulation ---
        self.stdout.write("Nettoyage des anciennes données de simulation (Locations, Vélos, Tickets)...")
        Location.objects.all().delete()
        Velo.objects.all().delete()
        TicketSupport.objects.all().delete()

        # --- ÉTAPE 2 : Création d'un pool de 500 utilisateurs de test ---
        self.stdout.write("Nettoyage et création de 500 utilisateurs de test...")
        Utilisateur.objects.filter(is_superuser=False).delete()

        faker = Faker('fr_FR')
        utilisateurs_a_creer = []
        noms_utilisateurs_existants = set(Utilisateur.objects.values_list('username', flat=True))

        while len(utilisateurs_a_creer) < 500:  # Rétablissement du nombre d'utilisateurs à 500
            profil = faker.simple_profile()
            username = profil['username']
            if username not in noms_utilisateurs_existants:
                noms_utilisateurs_existants.add(username)
                utilisateurs_a_creer.append(
                    Utilisateur(
                        username=username, email=profil['mail'],
                        first_name=faker.first_name(), last_name=faker.last_name(),
                        password=make_password('password123')
                    )
                )
        Utilisateur.objects.bulk_create(utilisateurs_a_creer)
        self.stdout.write(self.style.SUCCESS("500 utilisateurs de test créés."))

        # --- ÉTAPE 3 : Création des vélos (basée sur les stations existantes) ---
        stations = list(Station.objects.all())
        if not stations:
            self.stdout.write(self.style.ERROR("Aucune station trouvée. Veuillez les créer via l'interface d'admin."))
            return

        self.stdout.write("Création de 20 vélos par station...")
        for station in stations:
            for _ in range(20):
                Velo.objects.create(station_origine=station, station_actuelle=station)

        # --- ÉTAPE 4 : Génération de l'historique de locations ---
        utilisateurs = list(Utilisateur.objects.filter(is_superuser=False))
        weather_service = MockWeatherService()

        # Rétablissement de la date de début au 1er juin 2025
        start_date = timezone.make_aware(datetime(2025, 6, 1))
        end_date = timezone.now()

        all_velos = Velo.objects.all().select_related('station_origine__ville')
        total_velos = all_velos.count()

        self.stdout.write(
            f"Génération de l'historique pour {total_velos} vélos du {start_date.date()} à aujourd'hui...")

        for i, velo in enumerate(all_velos):
            if i % 50 == 0: self.stdout.write(f"  Traitement du vélo {i}/{total_velos}...")

            velo_ville = velo.station_origine.ville
            stations_de_la_ville = list(Station.objects.filter(ville=velo_ville))
            current_time = start_date
            current_station = velo.station_actuelle

            while current_time < end_date:
                temps_repos_heures = random.uniform(1, 48)
                potential_start_time = current_time + timedelta(hours=temps_repos_heures)
                if potential_start_time >= end_date: break

                weather = weather_service.get_weather(velo_ville.nom, potential_start_time)
                if weather['condition'] == 'pluie':
                    current_time = potential_start_time + timedelta(hours=1);
                    continue

                heure_depart = potential_start_time
                station_depart = current_station

                stations_possibles = [s for s in stations_de_la_ville if s.id != station_depart.id]
                if not stations_possibles:
                    current_time = heure_depart + timedelta(days=1);
                    continue

                station_arrivee = random.choice(stations_possibles)
                duree_location_minutes = random.randint(10, 120)
                heure_fin = heure_depart + timedelta(minutes=duree_location_minutes)
                if heure_fin >= end_date: break

                Location.objects.create(
                    velo=velo, utilisateur=random.choice(utilisateurs),
                    station_depart=station_depart, station_arrivee=station_arrivee,
                    date_debut=heure_depart, date_fin=heure_fin,
                )

                current_time = heure_fin
                current_station = station_arrivee

            velo.station_actuelle = current_station
            velo.save()

        self.stdout.write(self.style.SUCCESS("Historique complet (v2.2) généré avec succès !"))