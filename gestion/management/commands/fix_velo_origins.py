# gestion/management/commands/fix_velo_origins.py
from django.core.management.base import BaseCommand
from gestion.models import Velo, Station


class Command(BaseCommand):
    help = "Corrige la station d'origine pour les vélos qui n'en ont pas."

    def handle(self, *args, **options):
        # On prend la première station comme station par défaut si tout le reste échoue
        default_station = Station.objects.first()
        if not default_station:
            self.stdout.write(self.style.ERROR("Aucune station n'existe, impossible de corriger."))
            return

        # On cherche tous les vélos dont la station_origine est encore vide (NULL)
        velos_a_corriger = Velo.objects.filter(station_origine__isnull=True)

        self.stdout.write(f"Trouvé {velos_a_corriger.count()} vélos à corriger...")

        for velo in velos_a_corriger:
            # On assigne la station actuelle comme station d'origine
            # C'est la meilleure estimation qu'on puisse faire
            if velo.station_actuelle:
                velo.station_origine = velo.station_actuelle
            else:
                velo.station_origine = default_station
            velo.save()

        self.stdout.write(self.style.SUCCESS("Correction terminée !"))