from django.urls import path
from . import views  # Importe le fichier views.py du même dossier

# Le 'namespacing' d'URL est une bonne pratique.
# Il permet d'éviter les conflits de noms d'URL entre différentes applications.
app_name = 'gestion'

urlpatterns = [
    # Itinéraire pour la liste des vélos
    # Lorsque l'URL est vide (la racine de cette application), on appelle la vue 'liste_velos'.
    # Le 'name' est un nom unique pour cet itinéraire, très utile pour y faire référence plus tard.
    path('', views.liste_velos, name='liste_velos'),

    # Itinéraire pour le détail d'un vélo
    # '<int:pk>/' est un motif de chemin.
    # - Il capture une partie de l'URL (ex: /5/).
    # - 'int:' garantit que ce qui est capturé est un entier.
    # - 'pk' est le nom de la variable qui sera passée en argument à la vue.
    # Django appellera donc views.detail_velo(request, pk=5)
    path('<int:pk>/', views.detail_velo, name='detail_velo'),
]