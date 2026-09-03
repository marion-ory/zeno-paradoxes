import sys
import pygame

from paradoxes import (
    etape_tortue,
    etape_dichotomie,
    position_instant_fleche,
    position_a_instant,
    fleche_stat,
)
from ui import (
    creer_bouton,
    dessiner_bouton,
    bouton_clique,
    creer_champ_texte,
    gerer_champ_texte,
    dessiner_champ_texte,
    valeur_champ,
    valeur_vers_pixel,
    dessiner_piste,
)

# =========================================================================
# CONFIGURATION GENERALE
# =========================================================================
LARGEUR, HAUTEUR = 1000, 650
DELAI_AUTO_MS = 700  # délai entre deux étapes en mode "lecture automatique"

BLANC = (250, 250, 248)
NOIR = (25, 25, 25)
GRIS = (150, 150, 150)
GRIS_CLAIR = (215, 215, 215)
ROUGE = (195, 70, 70)
VERT = (60, 150, 95)
BLEU = (60, 105, 195)
OR = (200, 150, 40)

pygame.init()
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Les Paradoxes de Zénon")
horloge = pygame.time.Clock()

police_titre = pygame.font.SysFont("arial", 34, bold=True)
police_texte = pygame.font.SysFont("arial", 22)
police_petite = pygame.font.SysFont("arial", 17)

etat = "menu"      # écran actuellement affiché
contexte = {}      # variables propres à l'écran actif (remises à zéro à chaque changement d'écran)

# Bouton "retour" commun à tous les écrans (sauf le menu)
bouton_retour = creer_bouton(20, 20, 110, 40, "< Retour")


# =========================================================================
# GESTION DES ETATS (changement d'écran)
# =========================================================================
def entrer_etat(nouvel_etat):
    """Change d'écran et réinitialise le contexte propre à ce nouvel écran."""
    global etat, contexte
    etat = nouvel_etat
    contexte = {}

    if nouvel_etat == "tortue":
        contexte.update({
            "position_achille": 0,
            "position_tortue": 10,
            "vitesse_achille": 2,
            "vitesse_tortue": 1,
            "ecart": 10,
            "limite": 0.001,
            "etape": 0,
            "termine": False,
            "auto": False,
            "dernier_pas_ms": 0,
        })

    elif nouvel_etat == "dichotomie":
        contexte.update({
            "position_fleche": 0,
            "position_arbre": 20,
            "ecart": 20,
            "limite": 0.001,
            "etape": 0,
            "termine": False,
            "auto": False,
            "dernier_pas_ms": 0,
        })

    elif nouvel_etat == "fleche_menu":
        contexte["boutons"] = [
            creer_bouton(150, 220, 700, 60, "1 - Nombre d'instants en fonction de la distance"),
            creer_bouton(150, 310, 700, 60, "2 - Figer la flèche à un instant (barre ESPACE)"),
            creer_bouton(150, 400, 700, 60, "3 - Indice de doute (positions reconstruites)"),
        ]

    elif nouvel_etat == "fleche_mode1":
        contexte.update({
            "champ_pas": creer_champ_texte(150, 140, 150, 36, "Nombre de pas"),
            "champ_distance": creer_champ_texte(400, 140, 150, 36, "Distance (m)"),
            "bouton_lancer": creer_bouton(650, 130, 150, 46, "Lancer"),
            "lance": False,
            "i": 0,
            "nombre_de_pas": 0,
            "distance": 0,
            "auto": False,
            "dernier_pas_ms": 0,
            "termine": False,
        })

    elif nouvel_etat == "fleche_mode2":
        contexte.update({
            "champ_distance": creer_champ_texte(150, 140, 150, 36, "Distance (m)"),
            "bouton_lancer": creer_bouton(400, 130, 150, 46, "Lancer"),
            "lance": False,
            "debut_ms": 0,
            "duree_totale": 10,
            "nombre_de_pas": 1_000_000,
            "distance": 0,
            "fige": False,
            "resultat": None,
        })

    elif nouvel_etat == "fleche_mode3":
        contexte.update({
            "champ_pas": creer_champ_texte(150, 140, 150, 36, "Nombre de pas"),
            "champ_distance": creer_champ_texte(400, 140, 150, 36, "Distance (m)"),
            "champ_doute": creer_champ_texte(650, 140, 150, 36, "Indice de doute"),
            "bouton_lancer": creer_bouton(150, 210, 150, 46, "Tirer au sort"),
            "resultat": None,
        })


# =========================================================================
# ECRAN : MENU PRINCIPAL
# =========================================================================
def initialiser_menu():
    contexte["boutons"] = [
        creer_bouton(300, 220, 400, 60, "Achille et la Tortue"),
        creer_bouton(300, 310, 400, 60, "La Dichotomie"),
        creer_bouton(300, 400, 400, 60, "La Flèche"),
    ]


def gerer_menu(evenement):
    b_tortue, b_dicho, b_fleche = contexte["boutons"]
    if bouton_clique(b_tortue, evenement):
        entrer_etat("tortue")
    elif bouton_clique(b_dicho, evenement):
        entrer_etat("dichotomie")
    elif bouton_clique(b_fleche, evenement):
        entrer_etat("fleche_menu")


def dessiner_menu():
    ecran.fill(BLANC)
    titre = police_titre.render("Les Paradoxes de Zénon", True, NOIR)
    ecran.blit(titre, titre.get_rect(center=(LARGEUR // 2, 120)))
    souris_pos = pygame.mouse.get_pos()
    for bouton in contexte["boutons"]:
        dessiner_bouton(ecran, bouton, police_texte, BLEU, BLANC, souris_pos)


# =========================================================================
# ECRAN : ACHILLE ET LA TORTUE
# =========================================================================
def gerer_tortue(evenement):
    if evenement.type == pygame.KEYDOWN:
        if evenement.key == pygame.K_SPACE and not contexte["termine"]:
            avancer_tortue()
        elif evenement.key == pygame.K_a:
            contexte["auto"] = not contexte["auto"]


def avancer_tortue():
    pa, pt, ecart = etape_tortue(
        contexte["position_achille"],
        contexte["position_tortue"],
        contexte["vitesse_achille"],
        contexte["vitesse_tortue"],
        contexte["ecart"],
    )
    contexte["position_achille"] = pa
    contexte["position_tortue"] = pt
    contexte["ecart"] = ecart
    contexte["etape"] += 1
    if ecart <= contexte["limite"]:
        contexte["termine"] = True
        contexte["auto"] = False


def mettre_a_jour_tortue():
    if contexte["auto"] and not contexte["termine"]:
        maintenant = pygame.time.get_ticks()
        if maintenant - contexte["dernier_pas_ms"] > DELAI_AUTO_MS:
            avancer_tortue()
            contexte["dernier_pas_ms"] = maintenant


def dessiner_tortue():
    ecran.fill(BLANC)
    titre = police_titre.render("Achille et la Tortue", True, NOIR)
    ecran.blit(titre, (150, 60))

    x_gauche, x_droite, y = 100, 900, 350
    valeur_max = max(contexte["position_tortue"], contexte["position_achille"]) * 1.1 + 1
    dessiner_piste(ecran, x_gauche, x_droite, y, GRIS)

    px_tortue = valeur_vers_pixel(contexte["position_tortue"], 0, valeur_max, x_gauche, x_droite)
    px_achille = valeur_vers_pixel(contexte["position_achille"], 0, valeur_max, x_gauche, x_droite)
    pygame.draw.circle(ecran, VERT, (int(px_tortue), y), 12)
    pygame.draw.circle(ecran, ROUGE, (int(px_achille), y), 12)
    ecran.blit(police_petite.render("Tortue", True, VERT), (px_tortue - 20, y + 20))
    ecran.blit(police_petite.render("Achille", True, ROUGE), (px_achille - 20, y - 40))

    lignes = [
        f"Étape : {contexte['etape']}",
        f"Position Achille : {contexte['position_achille']:.5f}",
        f"Position Tortue : {contexte['position_tortue']:.5f}",
        f"Écart : {contexte['ecart']:.6f}",
    ]
    for i, ligne in enumerate(lignes):
        ecran.blit(police_texte.render(ligne, True, NOIR), (100, 420 + i * 32))

    if contexte["termine"]:
        msg = f"Écart sous la limite après {contexte['etape']} étapes : le temps reste fini."
        ecran.blit(police_texte.render(msg, True, OR), (100, 560))
    else:
        aide = "ESPACE : une étape   |   A : lecture automatique (" + ("ON)" if contexte["auto"] else "OFF)")
        ecran.blit(police_petite.render(aide, True, GRIS), (100, 560))

    souris_pos = pygame.mouse.get_pos()
    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# ECRAN : DICHOTOMIE
# =========================================================================
def gerer_dichotomie(evenement):
    if evenement.type == pygame.KEYDOWN:
        if evenement.key == pygame.K_SPACE and not contexte["termine"]:
            avancer_dichotomie()
        elif evenement.key == pygame.K_a:
            contexte["auto"] = not contexte["auto"]


def avancer_dichotomie():
    pf, ecart = etape_dichotomie(contexte["position_fleche"], contexte["ecart"])
    contexte["position_fleche"] = pf
    contexte["ecart"] = ecart
    contexte["etape"] += 1
    if ecart <= contexte["limite"]:
        contexte["termine"] = True
        contexte["auto"] = False


def mettre_a_jour_dichotomie():
    if contexte["auto"] and not contexte["termine"]:
        maintenant = pygame.time.get_ticks()
        if maintenant - contexte["dernier_pas_ms"] > DELAI_AUTO_MS:
            avancer_dichotomie()
            contexte["dernier_pas_ms"] = maintenant


def dessiner_dichotomie():
    ecran.fill(BLANC)
    titre = police_titre.render("La Dichotomie", True, NOIR)
    ecran.blit(titre, (150, 60))

    x_gauche, x_droite, y = 100, 900, 350
    valeur_max = contexte["position_arbre"] * 1.05
    dessiner_piste(ecran, x_gauche, x_droite, y, GRIS)

    px_fleche = valeur_vers_pixel(contexte["position_fleche"], 0, valeur_max, x_gauche, x_droite)
    px_arbre = valeur_vers_pixel(contexte["position_arbre"], 0, valeur_max, x_gauche, x_droite)
    pygame.draw.polygon(ecran, VERT, [(px_arbre - 12, y + 10), (px_arbre + 12, y + 10), (px_arbre, y - 30)])
    ecran.blit(police_petite.render("Arbre", True, VERT), (px_arbre - 18, y + 15))
    pygame.draw.circle(ecran, ROUGE, (int(px_fleche), y), 10)
    ecran.blit(police_petite.render("Flèche", True, ROUGE), (px_fleche - 18, y - 40))

    lignes = [
        f"Étape : {contexte['etape']}",
        f"Position flèche : {contexte['position_fleche']:.5f}",
        f"Écart restant : {contexte['ecart']:.6f}",
    ]
    for i, ligne in enumerate(lignes):
        ecran.blit(police_texte.render(ligne, True, NOIR), (100, 420 + i * 32))

    if contexte["termine"]:
        msg = f"Écart sous la limite après {contexte['etape']} étapes."
        ecran.blit(police_texte.render(msg, True, OR), (100, 560))
    else:
        aide = "ESPACE : une étape   |   A : lecture automatique (" + ("ON)" if contexte["auto"] else "OFF)")
        ecran.blit(police_petite.render(aide, True, GRIS), (100, 560))

    souris_pos = pygame.mouse.get_pos()
    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# ECRAN : SOUS-MENU DE LA FLECHE
# =========================================================================
def gerer_fleche_menu(evenement):
    b1, b2, b3 = contexte["boutons"]
    if bouton_clique(b1, evenement):
        entrer_etat("fleche_mode1")
    elif bouton_clique(b2, evenement):
        entrer_etat("fleche_mode2")
    elif bouton_clique(b3, evenement):
        entrer_etat("fleche_mode3")


def dessiner_fleche_menu():
    ecran.fill(BLANC)
    titre = police_titre.render("Le Paradoxe de la Flèche", True, NOIR)
    ecran.blit(titre, (150, 140))
    souris_pos = pygame.mouse.get_pos()
    for bouton in contexte["boutons"]:
        dessiner_bouton(ecran, bouton, police_petite, BLEU, BLANC, souris_pos)
    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# ECRAN : FLECHE - MODE 1 (instants en fonction de la distance)
# =========================================================================
def gerer_fleche_mode1(evenement):
    gerer_champ_texte(contexte["champ_pas"], evenement)
    gerer_champ_texte(contexte["champ_distance"], evenement)

    if bouton_clique(contexte["bouton_lancer"], evenement):
        nb_pas = valeur_champ(contexte["champ_pas"], 0)
        distance = valeur_champ(contexte["champ_distance"], 0)
        if nb_pas > 0 and distance >= 0:
            contexte["nombre_de_pas"] = min(nb_pas, 500)  # limite d'affichage raisonnable
            contexte["distance"] = distance
            contexte["i"] = 0
            contexte["lance"] = True
            contexte["termine"] = False

    if evenement.type == pygame.KEYDOWN and contexte["lance"]:
        if evenement.key == pygame.K_SPACE and not contexte["termine"]:
            avancer_fleche_mode1()
        elif evenement.key == pygame.K_a:
            contexte["auto"] = not contexte["auto"]


def avancer_fleche_mode1():
    contexte["i"] += 1
    if contexte["i"] >= contexte["nombre_de_pas"]:
        contexte["termine"] = True
        contexte["auto"] = False


def mettre_a_jour_fleche_mode1():
    if contexte.get("lance") and contexte["auto"] and not contexte["termine"]:
        maintenant = pygame.time.get_ticks()
        if maintenant - contexte["dernier_pas_ms"] > 60:
            avancer_fleche_mode1()
            contexte["dernier_pas_ms"] = maintenant


def dessiner_fleche_mode1():
    ecran.fill(BLANC)
    ecran.blit(police_titre.render("Flèche - Mode 1 : instants successifs", True, NOIR), (100, 60))
    souris_pos = pygame.mouse.get_pos()

    dessiner_champ_texte(ecran, contexte["champ_pas"], police_texte, BLEU, GRIS, NOIR)
    dessiner_champ_texte(ecran, contexte["champ_distance"], police_texte, BLEU, GRIS, NOIR)
    dessiner_bouton(ecran, contexte["bouton_lancer"], police_texte, VERT, BLANC, souris_pos)

    if contexte["lance"]:
        x_gauche, x_droite, y = 100, 900, 350
        distance = contexte["distance"]
        dessiner_piste(ecran, x_gauche, x_droite, y, GRIS)

        i = contexte["i"]
        if i > 0:
            position = position_instant_fleche(i, contexte["nombre_de_pas"], distance)
            px = valeur_vers_pixel(position, 0, distance * 1.02 + 0.001, x_gauche, x_droite)
            pygame.draw.circle(ecran, ROUGE, (int(px), y), 10)
            texte = f"L'instant {i} se trouve à {position:.3f} m du tireur."
            ecran.blit(police_texte.render(texte, True, NOIR), (100, 420))
        else:
            ecran.blit(police_texte.render("Appuyez sur ESPACE pour démarrer.", True, NOIR), (100, 420))

        aide = "ESPACE : instant suivant   |   A : lecture automatique (" + ("ON)" if contexte["auto"] else "OFF)")
        ecran.blit(police_petite.render(aide, True, GRIS), (100, 460))

        if contexte["termine"]:
            ecran.blit(police_texte.render("Tous les instants ont été affichés.", True, OR), (100, 500))

    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# ECRAN : FLECHE - MODE 2 (figer la flèche / équivalent de KeyboardInterrupt)
# =========================================================================
def gerer_fleche_mode2(evenement):
    gerer_champ_texte(contexte["champ_distance"], evenement)

    if bouton_clique(contexte["bouton_lancer"], evenement):
        distance = valeur_champ(contexte["champ_distance"], 0)
        if distance >= 0:
            contexte["distance"] = distance
            contexte["debut_ms"] = pygame.time.get_ticks()
            contexte["lance"] = True
            contexte["fige"] = False
            contexte["resultat"] = None

    if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_SPACE:
        if contexte["lance"] and not contexte["fige"]:
            figer_fleche_mode2()


def figer_fleche_mode2():
    # Équivalent du KeyboardInterrupt (Ctrl+C) du script original :
    # ici, la touche ESPACE joue le rôle de l'interruption.
    temps_ecoule_s = (pygame.time.get_ticks() - contexte["debut_ms"]) / 1000
    temps_ecoule_s = min(temps_ecoule_s, contexte["duree_totale"])
    instant_i, position = position_a_instant(
        temps_ecoule_s, contexte["duree_totale"], contexte["nombre_de_pas"], contexte["distance"]
    )
    contexte["resultat"] = (instant_i, position)
    contexte["fige"] = True


def dessiner_fleche_mode2():
    ecran.fill(BLANC)
    ecran.blit(police_titre.render("Flèche - Mode 2 : figer un instant", True, NOIR), (100, 60))
    souris_pos = pygame.mouse.get_pos()

    dessiner_champ_texte(ecran, contexte["champ_distance"], police_texte, BLEU, GRIS, NOIR)
    dessiner_bouton(ecran, contexte["bouton_lancer"], police_texte, VERT, BLANC, souris_pos)

    if contexte["lance"]:
        x_gauche, x_droite, y = 100, 900, 380
        distance = contexte["distance"]
        dessiner_piste(ecran, x_gauche, x_droite, y, GRIS)

        if not contexte["fige"]:
            temps_ecoule_s = (pygame.time.get_ticks() - contexte["debut_ms"]) / 1000
            if temps_ecoule_s >= contexte["duree_totale"]:
                temps_ecoule_s = contexte["duree_totale"]
                if contexte["resultat"] is None:
                    contexte["resultat"] = "fin"
            ratio = min(temps_ecoule_s / contexte["duree_totale"], 1.0)
            px = x_gauche + ratio * (x_droite - x_gauche)
            pygame.draw.circle(ecran, ROUGE, (int(px), y), 10)

            restant = max(0, contexte["duree_totale"] - temps_ecoule_s)
            ecran.blit(police_texte.render(f"Il reste {restant:.1f} secondes", True, NOIR), (100, 420))
            ecran.blit(police_petite.render("Appuyez sur ESPACE pour figer la flèche à cet instant.", True, GRIS), (100, 460))
            if contexte["resultat"] == "fin":
                ecran.blit(police_texte.render("Décompte terminé, la flèche est dans la cible.", True, OR), (100, 500))
        else:
            instant_i, position = contexte["resultat"]
            px = valeur_vers_pixel(position, 0, distance * 1.02 + 0.001, x_gauche, x_droite)
            pygame.draw.circle(ecran, ROUGE, (int(px), y), 12)
            ecran.blit(police_texte.render(f"La flèche est figée à l'instant {instant_i}", True, NOIR), (100, 420))
            ecran.blit(police_texte.render(f"Elle se trouve à {position:.3f} m du tireur.", True, NOIR), (100, 455))

    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# ECRAN : FLECHE - MODE 3 (indice de doute)
# =========================================================================
def gerer_fleche_mode3(evenement):
    gerer_champ_texte(contexte["champ_pas"], evenement)
    gerer_champ_texte(contexte["champ_distance"], evenement)
    gerer_champ_texte(contexte["champ_doute"], evenement)

    if bouton_clique(contexte["bouton_lancer"], evenement):
        nb_pas = valeur_champ(contexte["champ_pas"], 0)
        distance = valeur_champ(contexte["champ_distance"], 0)
        indice_doute = valeur_champ(contexte["champ_doute"], 0)
        if nb_pas > 0 and distance >= 0:
            min_doute, max_doute, position = fleche_stat(distance, indice_doute, nb_pas)
            contexte["resultat"] = {
                "distance": distance,
                "indice_doute": indice_doute,
                "min_doute": min_doute,
                "max_doute": max_doute,
                "position": position,
            }


def dessiner_fleche_mode3():
    ecran.fill(BLANC)
    ecran.blit(police_titre.render("Flèche - Mode 3 : indice de doute", True, NOIR), (100, 60))
    souris_pos = pygame.mouse.get_pos()

    dessiner_champ_texte(ecran, contexte["champ_pas"], police_texte, BLEU, GRIS, NOIR)
    dessiner_champ_texte(ecran, contexte["champ_distance"], police_texte, BLEU, GRIS, NOIR)
    dessiner_champ_texte(ecran, contexte["champ_doute"], police_texte, BLEU, GRIS, NOIR)
    dessiner_bouton(ecran, contexte["bouton_lancer"], police_texte, VERT, BLANC, souris_pos)

    resultat = contexte["resultat"]
    if resultat:
        x_gauche, x_droite, y = 100, 900, 380
        distance = resultat["distance"]
        dessiner_piste(ecran, x_gauche, x_droite, y, GRIS)

        px_min = valeur_vers_pixel(resultat["min_doute"], 0, distance * 1.02 + 0.001, x_gauche, x_droite)
        px_max = valeur_vers_pixel(resultat["max_doute"], 0, distance * 1.02 + 0.001, x_gauche, x_droite)
        px_pos = valeur_vers_pixel(resultat["position"], 0, distance * 1.02 + 0.001, x_gauche, x_droite)

        # fourchette d'incertitude (zone grisée)
        pygame.draw.rect(ecran, (225, 225, 210), (px_min, y - 15, max(1, px_max - px_min), 30))
        pygame.draw.circle(ecran, OR, (int(px_pos), y), 11)  # position tirée au sort
        pygame.draw.circle(ecran, BLEU, (int(px_max), y), 6)  # position certaine (distance)

        ecart_a_distance = distance - resultat["position"]
        lignes = [
            f"Avec un indice de doute de {resultat['indice_doute']}, la flèche pourrait se trouver",
            f"à {ecart_a_distance:.2f} m de la cible, dans une fourchette de {resultat['min_doute']:.2f} m à {resultat['max_doute']:.2f} m du tireur.",
        ]
        for i, ligne in enumerate(lignes):
            ecran.blit(police_texte.render(ligne, True, NOIR), (100, 420 + i * 30))

    dessiner_bouton(ecran, bouton_retour, police_petite, GRIS_CLAIR, NOIR, souris_pos)


# =========================================================================
# BOUCLE PRINCIPALE
# =========================================================================
# Table de correspondance état -> (fonction de gestion, fonction de dessin, fonction de mise à jour)
ECRANS = {
    "menu": (gerer_menu, dessiner_menu, None),
    "tortue": (gerer_tortue, dessiner_tortue, mettre_a_jour_tortue),
    "dichotomie": (gerer_dichotomie, dessiner_dichotomie, mettre_a_jour_dichotomie),
    "fleche_menu": (gerer_fleche_menu, dessiner_fleche_menu, None),
    "fleche_mode1": (gerer_fleche_mode1, dessiner_fleche_mode1, mettre_a_jour_fleche_mode1),
    "fleche_mode2": (gerer_fleche_mode2, dessiner_fleche_mode2, None),
    "fleche_mode3": (gerer_fleche_mode3, dessiner_fleche_mode3, None),
}


def boucle_principale():
    initialiser_menu()
    en_cours = True
    while en_cours:
        for evenement in pygame.event.get():
            gerer_evenement, _, _ = ECRANS[etat]  # relu à chaque événement, au cas où etat change en cours de frame

            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE and etat != "menu":
                entrer_etat("menu")
                initialiser_menu()
            elif etat != "menu" and bouton_clique(bouton_retour, evenement):
                entrer_etat("menu")
                initialiser_menu()
            else:
                gerer_evenement(evenement)

        _, dessiner, mettre_a_jour = ECRANS[etat]  # etat final de la frame
        if mettre_a_jour:
            mettre_a_jour()

        dessiner()
        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    boucle_principale()
