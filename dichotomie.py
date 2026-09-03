position_arbre = 20
position_fleche = 0


ecart = position_arbre - position_fleche
limite = 0.001

while ecart > limite :
    n_position_fleche = ecart/2
    position_fleche = position_fleche + n_position_fleche
    ecart = ecart - n_position_fleche

print(f"L'écart entre la flèche et l'arbre est de {ecart} mètres. La flèche est à {position_fleche} mètres de l'arbre")
