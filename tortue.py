position_achille = 0
position_tortue = 10
vitesse_achille = 2
vitesse_tortue = 1

ecart = position_tortue - position_achille
limite = 0.001

while ecart > limite :
    temps_achille = ecart/vitesse_achille
    position_achille += ecart
    position_tortue += vitesse_tortue*temps_achille

    ecart = position_tortue - position_achille

print(f"L'écart entre Achille et la tortue est de {ecart}")
