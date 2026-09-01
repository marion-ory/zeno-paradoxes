# Initialisation des positions Achille + Tortue
compteur = 0
position_Achille = 0.0
position_Tortue = 10.0

# Fixe un seuil limite
seuil = 0.001
ecart = 10.0

# Initialise la vitesse de Achille et la Tortue (Tortue deux fois moins rapide)
# Achille mettra 10secondes à parcourrir aproximativement 10metres

vitesse_Achille = 1.0
vitesse_Tortue = 0.5

while ecart > seuil:

    ecart = position_Tortue - position_Achille
    temps = ecart / vitesse_Achille

    position_Achille = position_Tortue
    position_Tortue += vitesse_Tortue * temps
    compteur += 1

    print(f"\n Position actuelle de Achille {position_Achille}")
    print(f"\n Position Tortue : {position_Tortue}")

    print(f"\n L'ecart entre Achille et la Tortue est de : {ecart} mètres")
    print(f" Itération {compteur}")
