# CODE FINAL v2.1 (plus robuste) pour gestion/management/commands/generate_files.py

import os
import csv
import json
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from gestion.models import Velo, TicketSupport


class Command(BaseCommand):
    help = "Génère les fichiers de position JSON, simule la batterie et crée les tickets de support."

    def _interpolate_coords(self, start, end, ratio):
        lat = start['lat'] + (end['lat'] - start['lat']) * ratio
        lon = start['lon'] + (end['lon'] - start['lon']) * ratio
        return lat, lon

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de la génération des fichiers (v2.1)..."))

        output_dir = os.path.join(settings.BASE_DIR, 'output_data_v2')
        os.makedirs(output_dir, exist_ok=True)
        TicketSupport.objects.all().delete()

        start_sim = timezone.make_aware(datetime(2025, 6, 1))
        end_sim = timezone.now()
        time_step = timedelta(seconds=30)

        all_velos = Velo.objects.all().prefetch_related('locations')
        total_velos = all_velos.count()

        if total_velos == 0:
            self.stdout.write(self.style.ERROR("Aucun vélo trouvé. Lancez 'generate_history'."))
            return

        all_tickets = []

        for i, velo in enumerate(all_velos):
            self.stdout.write(f"--- Traitement vélo {velo.id} ({i + 1}/{total_velos}) ---")

            locations = list(velo.locations.order_by('date_debut'))
            json_file_path = os.path.join(output_dir, f"velo_{velo.id}_iot.json")

            # --- BLOC DE CORRECTION : Initialisation robuste de la station ---
            current_station = velo.station_origine
            if not current_station:
                current_station = velo.station_actuelle
            if locations:
                current_station = locations[0].station_depart

            if not current_station:
                self.stdout.write(self.style.WARNING(f"Vélo {velo.id} n'a aucune station de référence et sera ignoré."))
                continue  # On passe au vélo suivant
            # --- FIN DU BLOC DE CORRECTION ---

            velo_data_points = []
            current_time = start_sim
            batterie = 100.0
            loc_idx = 0

            while current_time <= end_sim:
                status = "disponible"
                lat, lon = current_station.latitude, current_station.longitude

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
                            ticket = TicketSupport(
                                velo=velo, utilisateur=loc.utilisateur,
                                type_probleme=TicketSupport.TypeProbleme.BATTERIE_FAIBLE,
                                description=f"Batterie à {batterie:.1f}% à la fin de la location."
                            )
                            all_tickets.append(ticket)
                            batterie = 100.0

                        current_station = loc.station_arrivee
                        loc_idx += 1
                        lat, lon = current_station.latitude, current_station.longitude

                velo_data_points.append({
                    'timestamp': current_time.isoformat(),
                    'velo_id': velo.id,
                    'statut': status,
                    'batterie': round(batterie, 2),
                    'position': {'latitude': lat, 'longitude': lon}
                })
                current_time += time_step

            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(velo_data_points, f, indent=2)

        self.stdout.write("Création des tickets de support dans la base de données...")
        TicketSupport.objects.bulk_create(all_tickets)

        self.stdout.write("Exportation des tickets en fichier CSV...")
        csv_path = os.path.join(output_dir, "support_tickets.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'velo_id', 'utilisateur', 'type_probleme', 'description', 'date_creation'])
            for ticket in TicketSupport.objects.all():
                writer.writerow([
                    ticket.id, ticket.velo_id, ticket.utilisateur.username if ticket.utilisateur else '',
                    ticket.get_type_probleme_display(), ticket.description, ticket.date_creation.isoformat()
                ])

        self.stdout.write(self.style.SUCCESS("Génération des fichiers (v2.1) terminée !"))