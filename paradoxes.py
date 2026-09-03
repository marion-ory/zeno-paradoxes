from random import randint

# -----------------------------------------------------------------------
# Ce fichier ne contient QUE des calculs (aucun print(), aucun input(),
# aucun affichage Pygame). Ce sont les mêmes formules que dans tortue.py,
# dichotomie.py et menu_fleche.py, simplement isolées dans des fonctions
# pour pouvoir être rejouées pas à pas dans l'animation.
# -----------------------------------------------------------------------


def etape_tortue(position_achille, position_tortue, vitesse_achille, vitesse_tortue, ecart):
    """
    Une itération du paradoxe d'Achille et la Tortue (identique à tortue.py).
    """
    temps_achille = ecart / vitesse_achille
    position_achille = position_achille + ecart
    position_tortue = position_tortue + vitesse_tortue * temps_achille
    nouvel_ecart = position_tortue - position_achille
    return position_achille, position_tortue, nouvel_ecart


def etape_dichotomie(position_fleche, ecart):
    """
    Une itération du paradoxe de la Dichotomie.

    Correction par rapport à dichotomie.py : dans le script original,
    "position_fleche" n'était jamais réellement mise à jour (seul "ecart"
    changeait). Ici la position avance réellement de la moitié de l'écart
    restant à chaque étape, sinon il n'y a rien à animer à l'écran.
    """
    avancee = ecart / 2
    position_fleche = position_fleche + avancee
    nouvel_ecart = ecart - avancee
    return position_fleche, nouvel_ecart


def position_instant_fleche(i, nombre_de_pas, distance):
    """Mode 1 de menu_fleche.py : position de la flèche à l'instant i."""
    taille_du_pas = distance / nombre_de_pas
    return i * taille_du_pas


def position_a_instant(temps_ecoule, duree_totale, nombre_de_pas, distance):
    """Mode 2 de menu_fleche.py : position correspondant à l'instant figé."""
    instant_i = round((temps_ecoule / duree_totale) * nombre_de_pas)
    instant_i = max(0, min(instant_i, nombre_de_pas))
    position = instant_i / nombre_de_pas * distance
    return instant_i, position


def fleche_stat(distance, indice_doute, nombre_de_pas, largeur_par_doute=1):
    """Mode 3 de menu_fleche.py : indice de doute (fonction identique à l'originale)."""
    max_doute = distance
    min_doute = max(0, distance - indice_doute * largeur_par_doute)
    taille_pas = (max_doute - min_doute) / nombre_de_pas
    random_pas = randint(0, nombre_de_pas)
    position = min_doute + random_pas * taille_pas
    return min_doute, max_doute, position
