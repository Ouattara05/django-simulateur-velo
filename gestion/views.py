from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Velo

# --- Vue 1 : Liste des vélos disponibles ---
# Cette vue récupère tous les vélos qui ont le statut 'Disponible'
# et les envoie à un template pour affichage.

def liste_velos(request):
    """
    Affiche la liste de tous les vélos disponibles.
    """
    # 1. Logique métier : Interroger la base de données
    # On utilise le Manager de modèle (.objects) pour filtrer les vélos.
    # On ne prend que ceux dont le statut est 'DISPO'.
    velos_disponibles = Velo.objects.filter(statut='DISPO').order_by('marque')

    # 2. Préparer le contexte
    # Le "contexte" est un dictionnaire qui transmet les données au template.
    # La clé ('velos') sera le nom de la variable dans le template.
    context = {
        'velos': velos_disponibles
    }

    # 3. Renvoyer la réponse
    # La fonction render() prend la requête, le chemin du template
    # et le contexte, puis génère la réponse HTTP.
    # Nous devrons créer le fichier 'gestion/liste_velos.html' juste après.
    return render(request, 'gestion/liste_velos.html', context)


# --- Vue 2 : Détails d'un vélo spécifique ---
# Cette vue prend un identifiant (pk, pour Primary Key) de vélo en plus de la requête.
# Elle récupère ce vélo unique et affiche ses informations.

def detail_velo(request, pk):
    """
    Affiche les détails d'un seul vélo identifié par sa clé primaire (pk).
    """
    # 1. Logique métier : Récupérer un objet unique
    # get_object_or_404 est un raccourci très pratique :
    # - Il essaie de récupérer l'objet Velo avec l'id = pk.
    # - S'il ne le trouve pas, il lève automatiquement une erreur 404 (Page non trouvée).
    velo = get_object_or_404(Velo, pk=pk)

    # 2. Préparer le contexte
    context = {
        'velo': velo
    }

    # 3. Renvoyer la réponse
    # Nous devrons créer le fichier 'gestion/detail_velo.html'.
    return render(request, 'gestion/detail_velo.html', context)