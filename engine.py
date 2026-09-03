from script1 import *
from script2 import *
from script3 import *


def simuler_achille(pos_A, pos_T, vitesse_A, vitesse_T, seuil=0.001):

    position_Achille = pos_A
    position_Tortue = pos_T

    ecart = position_Tortue - position_Achille
    compteur = 0
    historique = []

    while ecart > seuil:

        ecart = position_Tortue - position_Achille
        temps = ecart / vitesse_A
        position_Achille = position_Tortue
        position_Tortue += vitesse_T * temps
        compteur += 1

        etape = {
            "iteration": compteur,
            "position_Achille": position_Achille,
            "position_Tortue": position_Tortue,
            "ecart": ecart,
            "temps": temps,
        }
        historique.append(etape)

    return historique


def simuler_dochotomie(pos_arbre_init, pos_pierre_init, seuil=0.001):

    position_Arbre = pos_arbre_init
    position_Pierre = pos_pierre_init

    ecart = position_Arbre - position_Pierre
    distance_initiale = ecart
    compteur = 0
    historique = []

    while ecart > seuil:
        pas = ecart / 2
        position_Pierre += pas
        ecart = position_Arbre - position_Pierre
        compteur += 1

        etape = {
            "Itération": compteur,
            "position Arbre": position_Arbre,
            "position Pierre": position_Pierre,
            "ecart": ecart,
            "distance_initiale": distance_initiale,
            "pas": pas,
        }
        historique.append(etape)

    return historique


def simuler_fleche(pos_fleche_init, target_init, temps_total=1.0, instant=0.1):

    pos_fleche = pos_fleche_init
    target = target_init
    speed = target / temps_total
    compteur = 0
    historique = []

    while pos_fleche < target:
        distance_instant = speed * instant
        pos_fleche += distance_instant
        ecart = target - pos_fleche
        compteur += 1

        etape = {
            "Itération": compteur,
            "position_fleche": pos_fleche,
            "reste": ecart,
            "distance_instant": distance_instant,
        }

        historique.append(etape)
    return historique
