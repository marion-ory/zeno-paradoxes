import pygame

# -----------------------------------------------------------------------
# Fonctions "outils" pour dessiner l'interface. Pas de classes : chaque
# élément (bouton, champ de texte) est un simple dictionnaire, et chaque
# fonction lit ou modifie ce dictionnaire.
# -----------------------------------------------------------------------


def creer_bouton(x, y, largeur, hauteur, texte):
    """Crée un bouton : un rectangle Pygame + le texte à afficher dedans."""
    return {"rect": pygame.Rect(x, y, largeur, hauteur), "texte": texte}


def dessiner_bouton(ecran, bouton, police, couleur_fond, couleur_texte, souris_pos):
    """Dessine un bouton ; s'éclaircit légèrement si la souris est dessus."""
    survole = bouton["rect"].collidepoint(souris_pos)
    couleur = tuple(min(255, c + 30) for c in couleur_fond) if survole else couleur_fond
    pygame.draw.rect(ecran, couleur, bouton["rect"], border_radius=8)
    pygame.draw.rect(ecran, couleur_texte, bouton["rect"], width=2, border_radius=8)
    texte_rendu = police.render(bouton["texte"], True, couleur_texte)
    texte_rect = texte_rendu.get_rect(center=bouton["rect"].center)
    ecran.blit(texte_rendu, texte_rect)


def bouton_clique(bouton, evenement):
    """Renvoie True si ce bouton vient d'être cliqué (clic gauche)."""
    return (
        evenement.type == pygame.MOUSEBUTTONDOWN
        and evenement.button == 1
        and bouton["rect"].collidepoint(evenement.pos)
    )


def creer_champ_texte(x, y, largeur, hauteur, etiquette):
    """Crée un champ de saisie numérique (dictionnaire)."""
    return {"rect": pygame.Rect(x, y, largeur, hauteur), "texte": "", "actif": False, "etiquette": etiquette}


def gerer_champ_texte(champ, evenement):
    """Met à jour un champ de texte selon les événements souris/clavier."""
    if evenement.type == pygame.MOUSEBUTTONDOWN:
        champ["actif"] = champ["rect"].collidepoint(evenement.pos)
    elif evenement.type == pygame.KEYDOWN and champ["actif"]:
        if evenement.key == pygame.K_BACKSPACE:
            champ["texte"] = champ["texte"][:-1]
        elif evenement.unicode.isdigit() and len(champ["texte"]) < 8:
            champ["texte"] += evenement.unicode


def dessiner_champ_texte(ecran, champ, police, couleur_actif, couleur_inactif, couleur_texte):
    """Dessine le champ de texte avec son étiquette au-dessus."""
    etiquette_rendue = police.render(champ["etiquette"], True, couleur_texte)
    ecran.blit(etiquette_rendue, (champ["rect"].x, champ["rect"].y - 26))
    couleur_bord = couleur_actif if champ["actif"] else couleur_inactif
    pygame.draw.rect(ecran, (255, 255, 255), champ["rect"], border_radius=4)
    pygame.draw.rect(ecran, couleur_bord, champ["rect"], width=2, border_radius=4)
    contenu = champ["texte"] if champ["texte"] else "0"
    texte_rendu = police.render(contenu, True, (20, 20, 20))
    ecran.blit(texte_rendu, (champ["rect"].x + 8, champ["rect"].y + 6))


def valeur_champ(champ, valeur_defaut=0):
    """Convertit le contenu d'un champ de texte en entier."""
    return int(champ["texte"]) if champ["texte"] else valeur_defaut


def valeur_vers_pixel(valeur, valeur_min, valeur_max, x_gauche, x_droite):
    """Convertit une valeur numérique en position horizontale à l'écran."""
    if valeur_max <= valeur_min:
        return x_gauche
    ratio = (valeur - valeur_min) / (valeur_max - valeur_min)
    ratio = max(0.0, min(1.0, ratio))
    return x_gauche + ratio * (x_droite - x_gauche)


def dessiner_piste(ecran, x_gauche, x_droite, y, couleur):
    """Dessine une ligne horizontale représentant la piste (0 -> distance)."""
    pygame.draw.line(ecran, couleur, (x_gauche, y), (x_droite, y), 4)
    pygame.draw.circle(ecran, couleur, (x_gauche, y), 6)
    pygame.draw.circle(ecran, couleur, (x_droite, y), 6)
