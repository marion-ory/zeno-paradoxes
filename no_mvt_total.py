from random import choice
# Largeur par doute : permet de se détacher du simple 1 doute = 1 mètre et de transformer l'indice de doute en mètres.

def fleche_stat(distance, indice_doute, nombre_de_pas, largeur_par_doute=1):
    doute_nul = distance

    # Calcul de l'intervalle de présence possible des instants disponibles (les pas)
    max_doute = max(0, distance - indice_doute * largeur_par_doute)

    taille_pas = distance/nombre_de_pas 
    total_instant=[i*taille_pas for i in range (nombre_de_pas+1)]
    positions_possibles = [p for p in total_instant if max_doute <= p <= doute_nul]

    if not positions_possibles:
        positions_possibles = [doute_nul]

    position = choice(positions_possibles)
    return max_doute, doute_nul, position

nombre_de_pas = int(input("Donnez un nombre de pas : "))
distance = int(input("Donnez une distance de la cible : "))
indice_doute = int(input("Donnez un indice de doute : "))

# fleche(nombre_de_pas, distance)
max_doute, doute_nul, position = fleche_stat(distance, indice_doute, nombre_de_pas)
print(f"Avec un indice de doute de {indice_doute}, la fleche pourrait se trouver à {distance-position:.2f}m de la cible, dans une fourchette de {distance-max_doute}m à {distance- doute_nul}m de la cible.")
