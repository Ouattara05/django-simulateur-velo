# gestion/management/commands/seed_data.py

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from faker import Faker
from gestion.models import Utilisateur, Velo


class Command(BaseCommand):
    help = 'Génère 200 vélos et 1000 utilisateurs de test dans la base de données.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de la création des données de test..."))

        if Velo.objects.exists() or Utilisateur.objects.count() > 1:
            self.stdout.write(
                self.style.WARNING("La base de données semble déjà contenir des données. Opération annulée."))
            return

        faker = Faker('fr_FR')

        # --- CRÉATION DES 1000 UTILISATEURS (VERSION CORRIGÉE) ---
        self.stdout.write("Création de 1000 utilisateurs uniques...")

        utilisateurs_a_creer = []
        # On utilise un "set" pour vérifier l'unicité des noms d'utilisateurs, c'est très rapide.
        noms_utilisateurs_uniques = set()

        # On utilise une boucle "while" pour s'assurer d'avoir EXACTEMENT 1000 utilisateurs.
        while len(utilisateurs_a_creer) < 1000:
            profil = faker.simple_profile()
            username = profil['username']

            # Si le nom d'utilisateur n'a pas déjà été généré...
            if username not in noms_utilisateurs_uniques:
                # ... on l'ajoute au set pour les futures vérifications
                noms_utilisateurs_uniques.add(username)

                password_crypte = make_password('password123')
                user = Utilisateur(
                    username=username,
                    email=profil['mail'],
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    password=password_crypte
                )
                utilisateurs_a_creer.append(user)

        Utilisateur.objects.bulk_create(utilisateurs_a_creer)
        self.stdout.write(self.style.SUCCESS("1000 utilisateurs créés."))

        # --- CRÉATION DES 200 VÉLOS (inchangé) ---
        self.stdout.write("Création de 200 vélos...")

        marques_de_velo = ['Peugeot', 'B\'Twin', 'Gitane', 'Lapierre', 'Cannondale', 'Trek', 'Specialized']
        velos_a_creer = []
        for _ in range(200):
            velo = Velo(
                marque=random.choice(marques_de_velo),
                modele=faker.word().capitalize() + " " + str(random.randint(100, 900)),
                statut=random.choice([s[0] for s in Velo.StatutVelo.choices]),
                tarif_horaire=round(random.uniform(3.0, 10.0), 2)
            )
            velos_a_creer.append(velo)

        Velo.objects.bulk_create(velos_a_creer)
        self.stdout.write(self.style.SUCCESS("200 vélos créés."))

        self.stdout.write(self.style.SUCCESS("Opération terminée avec succès !"))