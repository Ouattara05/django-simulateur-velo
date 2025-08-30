# CODE FINAL v3.1 (période réduite) pour gestion/management/commands/generate_files_v3.py

import os
import json
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from gestion.models import Velo, TicketSupport


class Command(BaseCommand):
    help = "Génère les données IoT avec un fichier JSON par point de données, pour une période réduite."

    def _interpolate_coords(self, start, end, ratio):
        lat = start['lat'] + (end['lat'] - start['lat']) * ratio
        lon = start['lon'] + (end['lon'] - start['lon']) * ratio
        return lat, lon

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Début de la génération des fichiers (v3.1 - hiérarchique, période réduite)..."))

        # --- Préparation ---
        output_dir = os.path.join(settings.BASE_DIR, 'output_data_v3')
        os.makedirs(output_dir, exist_ok=True)
        TicketSupport.objects.all().delete()

        # MODIFICATION : Date de début changée au 1er août 2025
        start_sim = timezone.make_aware(datetime(2025, 8, 1))
        end_sim = timezone.now()
        time_step = timedelta(seconds=30)

        all_velos = Velo.objects.all().prefetch_related('locations')
        total_velos = all_velos.count()

        if total_velos == 0:
            self.stdout.write(self.style.ERROR("Aucun vélo trouvé. Lancez 'generate_history'."))
            return

        all_tickets = []

        # --- Boucle par vélo ---
        for i, velo in enumerate(all_velos):
            self.stdout.write(f"--- Traitement vélo {velo.id} ({i + 1}/{total_velos}) ---")

            locations = list(velo.locations.order_by('date_debut'))

            current_station = velo.station_origine
            if not current_station: current_station = velo.station_actuelle
            if locations: current_station = locations[0].station_depart
            if not current_station:
                self.stdout.write(self.style.WARNING(f"Vélo {velo.id} ignoré car sans station de référence."))
                continue

            current_time, batterie, loc_idx = start_sim, 100.0, 0

            # --- Boucle temporelle ---
            while current_time <= end_sim:
                day_str = current_time.strftime('%Y-%m-%d')
                day_folder = os.path.join(output_dir, day_str)
                velo_folder = os.path.join(day_folder, f"velo_{velo.id}")
                os.makedirs(velo_folder, exist_ok=True)

                status, lat, lon = "disponible", current_station.latitude, current_station.longitude

                if loc_idx < len(locations):
                    loc = locations[loc_idx]
                    if loc.date_debut <= current_time < loc.date_fin:
                        status = "en_location"
                        trip_duration = (loc.date_fin - loc.date_debut).total_seconds()
                        time_into_trip = (current_time - loc.date_debut).total_seconds()
                        ratio = time_into_trip / trip_duration if trip_duration > 0 else 0

                        start_coords = {'lat': loc.station_depart.latitude, 'lon': loc.station_depart.longitude}
                        end_coords = {'lat': loc.station_arrivee.latitude, 'lon': loc.station_arrivee.longitude}
                        lat, lon = self._interpolate_coords(start_coords, end_coords, ratio)

                        drain_per_step = (random.uniform(10, 25) / (trip_duration / 30)) if trip_duration > 0 else 0
                        batterie = max(0, batterie - drain_per_step)
                    elif current_time >= loc.date_fin:
                        if batterie < 10.0 and random.random() < 0.8:
                            all_tickets.append(TicketSupport(velo=velo, utilisateur=loc.utilisateur,
                                                             type_probleme=TicketSupport.TypeProbleme.BATTERIE_FAIBLE,
                                                             description=f"Batterie à {batterie:.1f}%"));
                            batterie = 100.0

                        current_station = loc.station_arrivee;
                        loc_idx += 1
                        lat, lon = current_station.latitude, current_station.longitude

                data_point = {
                    'timestamp': current_time.isoformat(), 'velo_id': velo.id,
                    'statut': status, 'batterie': round(batterie, 2),
                    'position': {'latitude': lat, 'longitude': lon}
                }

                filename = f"{current_time.strftime('%H-%M-%S')}.json"
                file_path = os.path.join(velo_folder, filename)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_point, f, indent=2)

                current_time += time_step

        # --- Création et Exportation des tickets de support ---
        self.stdout.write("Création & Exportation des tickets de support...")
        TicketSupport.objects.bulk_create(all_tickets)
        csv_path = os.path.join(output_dir, "support_tickets.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'velo_id', 'utilisateur', 'type_probleme', 'description', 'date_creation'])
            for ticket in TicketSupport.objects.all():
                writer.writerow([
                    ticket.id, ticket.velo_id, ticket.utilisateur.username if ticket.utilisateur else '',
                    ticket.get_type_probleme_display(), ticket.description, ticket.date_creation.isoformat()
                ])

        self.stdout.write(self.style.SUCCESS("Génération des fichiers (v3.1) terminée !"))