import time

# Fonction 1 de la flèche
def fleche(nombre_de_pas, distance):
    taille_du_pas = (distance / nombre_de_pas)
    for i in range (1, nombre_de_pas+1) :
        position = i*taille_du_pas
        print(f"l'instant {i} se trouve à {position} du tireur.")

    nombre_de_pas = int(input("Donnez un nombre de pas : "))
    distance = int(input("Donnez une distance de la cible : "))

