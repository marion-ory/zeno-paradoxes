import pygame
import sys

# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================

LARGEUR, HAUTEUR = 900, 500
FPS = 60

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (200, 30, 30)
VERT = (30, 150, 30)
BLEU = (30, 30, 200)
GRIS = (150, 150, 150)
MARRON = (100, 60, 20)

pygame.init()
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Les paradoxes de Zenon")
horloge = pygame.time.Clock()
police = pygame.font.SysFont("arial", 22)
police_titre = pygame.font.SysFont("arial", 32, bold=True)

# Zone de dessin : une ligne horizontale qui sert de "piste" pour toutes les animations
MARGE_X = 80
LIGNE_Y = 300
LARGEUR_LIGNE = LARGEUR - 2 * MARGE_X

# Temps entre deux "étapes de Zénon" (en millisecondes). On ne fait pas
# une animation continue et fluide : on avance étape par étape, comme
# dans le raisonnement du paradoxe, pour bien voir chaque itération.
INTERVALLE_ETAPE_MS = 700


def texte(surface, contenu, x, y, couleur=NOIR, police_utilisee=None, centre=False):
    """Affiche du texte à l'écran. Si centre=True, x est le centre horizontal du texte."""
    police_utilisee = police_utilisee or police
    rendu = police_utilisee.render(contenu, True, couleur)
    rect = rendu.get_rect()
    if centre:
        rect.centerx = x
        rect.y = y
    else:
        rect.topleft = (x, y)
    surface.blit(rendu, rect)


def position_ecran(position_metres, distance_max):
    """Convertit une position en mètres en une position en pixels sur la ligne."""
    return MARGE_X + (position_metres / distance_max) * LARGEUR_LIGNE


# ============================================================
# PARADOXE 1 : ACHILLE ET LA TORTUE  (logique reprise de tortue.py)
# ============================================================

DISTANCE_INITIALE = 10
VITESSE_ACHILLE = 2
VITESSE_TORTUE = 1
LIMITE_ARRET_ACHILLE = 0.01

# Point de rencontre réel (formule classique de Zénon) : Achille rattrape la
# tortue à la position DISTANCE_INITIALE * vitesse_achille / (vitesse_achille - vitesse_tortue).
# On s'en sert pour fixer l'échelle du dessin (sinon les points sortiraient de l'écran).
POSITION_RENCONTRE = DISTANCE_INITIALE * VITESSE_ACHILLE / (VITESSE_ACHILLE - VITESSE_TORTUE)


def init_achille():
    return {
        "position_achille": 0,
        "position_tortue": DISTANCE_INITIALE,
        "termine": False,
        "dernier_temps": pygame.time.get_ticks(),
        "nb_etapes": 0,
    }


def maj_achille(etat):
    """Fait avancer la simulation d'une étape de Zénon toutes les INTERVALLE_ETAPE_MS."""
    if etat["termine"]:
        return

    maintenant = pygame.time.get_ticks()
    if maintenant - etat["dernier_temps"] < INTERVALLE_ETAPE_MS:
        return
    etat["dernier_temps"] = maintenant

    ecart = etat["position_tortue"] - etat["position_achille"]
    if ecart <= LIMITE_ARRET_ACHILLE:
        etat["termine"] = True
        return

    # Même logique que tortue.py : le temps qu'Achille mette à parcourir
    # l'écart actuel, la tortue continue d'avancer.
    temps_achille = ecart / VITESSE_ACHILLE
    etat["position_achille"] += ecart
    etat["position_tortue"] += VITESSE_TORTUE * temps_achille
    etat["nb_etapes"] += 1


def dessiner_achille(etat):
    pygame.draw.line(ecran, GRIS, (MARGE_X, LIGNE_Y), (MARGE_X + LARGEUR_LIGNE, LIGNE_Y), 3)

    distance_max = POSITION_RENCONTRE * 1.05  # petite marge pour ne pas coller au bord
    x_achille = position_ecran(etat["position_achille"], distance_max)
    x_tortue = position_ecran(etat["position_tortue"], distance_max)

    pygame.draw.circle(ecran, ROUGE, (int(x_achille), LIGNE_Y), 12)
    pygame.draw.circle(ecran, VERT, (int(x_tortue), LIGNE_Y), 8)

    texte(ecran, "Achille", x_achille, LIGNE_Y + 20, ROUGE, centre=True)
    texte(ecran, "Tortue", x_tortue, LIGNE_Y - 40, VERT, centre=True)

    ecart = etat["position_tortue"] - etat["position_achille"]
    texte(ecran, f"Etape {etat['nb_etapes']} - ecart restant : {ecart:.5f} m", MARGE_X, 50)

    if etat["termine"]:
        texte(ecran, "A chaque etape, Achille comble l'ecart mais la tortue a deja avance :",
              MARGE_X, HAUTEUR - 80)
        texte(ecran, "l'ecart tend vers 0 sans jamais s'annuler en un nombre fini d'etapes.",
              MARGE_X, HAUTEUR - 55)


# ============================================================
# PARADOXE 2 : LA DICHOTOMIE  (logique reprise de dichotomie.py)
# ============================================================

DISTANCE_ARBRE = 20
LIMITE_ARRET_DICHO = 0.01


def init_dichotomie():
    return {
        "position_fleche": 0,
        "ecart": DISTANCE_ARBRE,
        "termine": False,
        "dernier_temps": pygame.time.get_ticks(),
        "nb_etapes": 0,
    }


def maj_dichotomie(etat):
    if etat["termine"]:
        return

    maintenant = pygame.time.get_ticks()
    if maintenant - etat["dernier_temps"] < INTERVALLE_ETAPE_MS:
        return
    etat["dernier_temps"] = maintenant

    if etat["ecart"] <= LIMITE_ARRET_DICHO:
        etat["termine"] = True
        return

    # Même logique que dichotomie.py : on ne parcourt que la moitié
    # de l'écart restant à chaque étape.
    n_position = etat["ecart"] / 2
    etat["position_fleche"] += n_position
    etat["ecart"] -= n_position
    etat["nb_etapes"] += 1


def dessiner_dichotomie(etat):
    pygame.draw.line(ecran, GRIS, (MARGE_X, LIGNE_Y), (MARGE_X + LARGEUR_LIGNE, LIGNE_Y), 3)

    x_fleche = position_ecran(etat["position_fleche"], DISTANCE_ARBRE)
    x_arbre = MARGE_X + LARGEUR_LIGNE

    pygame.draw.rect(ecran, MARRON, (x_arbre - 6, LIGNE_Y - 40, 12, 40))
    texte(ecran, "Arbre", x_arbre, LIGNE_Y - 60, NOIR, centre=True)

    pygame.draw.circle(ecran, BLEU, (int(x_fleche), LIGNE_Y), 10)
    texte(ecran, "Fleche", x_fleche, LIGNE_Y + 20, BLEU, centre=True)

    texte(ecran, f"Etape {etat['nb_etapes']} - ecart restant : {etat['ecart']:.5f} m", MARGE_X, 50)

    if etat["termine"]:
        texte(ecran, "A chaque etape, la fleche ne parcourt que la moitie de la distance restante :",
              MARGE_X, HAUTEUR - 80)
        texte(ecran, "elle se rapproche indefiniment de l'arbre sans jamais officiellement l'atteindre.",
              MARGE_X, HAUTEUR - 55)


# ============================================================
# PARADOXE 3 : LA FLECHE (instants figes, logique reprise de menu_fleche.py, mode 1)
# ============================================================

DISTANCE_CIBLE = 20
NOMBRE_INSTANTS = 8
INTERVALLE_INSTANT_MS = 900


def init_fleche():
    # Même formule que fleche() dans menu_fleche.py : position(i) = i * (distance / pas)
    taille_du_pas = DISTANCE_CIBLE / NOMBRE_INSTANTS
    instants = [i * taille_du_pas for i in range(NOMBRE_INSTANTS + 1)]
    return {
        "instants": instants,
        "instant_courant": 0,
        "termine": False,
        "dernier_temps": pygame.time.get_ticks(),
    }


def maj_fleche(etat):
    if etat["termine"]:
        return

    maintenant = pygame.time.get_ticks()
    if maintenant - etat["dernier_temps"] < INTERVALLE_INSTANT_MS:
        return
    etat["dernier_temps"] = maintenant

    if etat["instant_courant"] >= len(etat["instants"]) - 1:
        etat["termine"] = True
        return
    etat["instant_courant"] += 1


def dessiner_fleche(etat):
    pygame.draw.line(ecran, GRIS, (MARGE_X, LIGNE_Y), (MARGE_X + LARGEUR_LIGNE, LIGNE_Y), 3)

    # On affiche tous les instants possibles comme des points figés sur la ligne,
    # et on met en évidence celui où la flèche se trouve "maintenant".
    for i, position in enumerate(etat["instants"]):
        x = position_ecran(position, DISTANCE_CIBLE)
        est_instant_actuel = (i == etat["instant_courant"])
        couleur = ROUGE if est_instant_actuel else GRIS
        rayon = 12 if est_instant_actuel else 6
        pygame.draw.circle(ecran, couleur, (int(x), LIGNE_Y), rayon)

    position_actuelle = etat["instants"][etat["instant_courant"]]
    texte(ecran, f"Instant {etat['instant_courant']} - la fleche est figee a {position_actuelle:.2f} m",
          MARGE_X, 50)
    texte(ecran, "A chaque instant, la fleche occupe une position fixe : elle y est donc immobile.",
          MARGE_X, HAUTEUR - 80)
    texte(ecran, "Or le temps n'est qu'une succession de ces instants figes... d'ou le paradoxe.",
          MARGE_X, HAUTEUR - 55)


# ============================================================
# MENU ET BOUCLE PRINCIPALE
# ============================================================

def dessiner_menu():
    texte(ecran, "Les trois paradoxes de Zenon", LARGEUR // 2, 100, NOIR, police_titre, centre=True)
    texte(ecran, "1 - Achille et la tortue", LARGEUR // 2, 200, NOIR, centre=True)
    texte(ecran, "2 - La dichotomie", LARGEUR // 2, 240, NOIR, centre=True)
    texte(ecran, "3 - La fleche", LARGEUR // 2, 280, NOIR, centre=True)
    texte(ecran, "Appuyez sur 1, 2 ou 3 pour lancer une simulation", LARGEUR // 2, 360, GRIS, centre=True)
    texte(ecran, "Pendant une simulation : R pour recommencer, ECHAP pour revenir au menu", LARGEUR // 2, 400, GRIS, centre=True)


def boucle_principale():
    mode = None  # None = on est dans le menu ; sinon 1, 2 ou 3
    etat = None
    en_cours = True

    while en_cours:
        # --- Gestion des événements ---
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False

            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    if mode is None:
                        en_cours = False
                    else:
                        mode = None
                        etat = None

                elif mode is None and evenement.key == pygame.K_1:
                    mode, etat = 1, init_achille()
                elif mode is None and evenement.key == pygame.K_2:
                    mode, etat = 2, init_dichotomie()
                elif mode is None and evenement.key == pygame.K_3:
                    mode, etat = 3, init_fleche()

                elif evenement.key == pygame.K_r and mode is not None:
                    if mode == 1:
                        etat = init_achille()
                    elif mode == 2:
                        etat = init_dichotomie()
                    elif mode == 3:
                        etat = init_fleche()

        # --- Mise à jour de la simulation active ---
        if mode == 1:
            maj_achille(etat)
        elif mode == 2:
            maj_dichotomie(etat)
        elif mode == 3:
            maj_fleche(etat)

        # --- Dessin (toujours après les mises à jour, pour refléter l'état final) ---
        ecran.fill(BLANC)
        if mode is None:
            dessiner_menu()
        elif mode == 1:
            dessiner_achille(etat)
        elif mode == 2:
            dessiner_dichotomie(etat)
        elif mode == 3:
            dessiner_fleche(etat)

        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    boucle_principale()