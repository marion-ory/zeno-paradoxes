from random import randint

def fleche_stat(distance, indice_doute, nombre_de_pas, largeur_par_doute=5):
    max_doute = distance
    min_doute = max(0, distance-indice_doute*largeur_par_doute)
    taille_pas = (max_doute - min_doute)/nombre_de_pas 
    random_pas = randint(0, nombre_de_pas)
    position = min_doute + random_pas * taille_pas
    return min_doute, max_doute, position

if __name__ == "__main__":
    nombre_de_pas = int(input("Donnez un nombre de pas : "))
    distance = int(input("Donnez une distance de la cible : "))
    indice_doute = int(input("Donnez un indice de doute : "))

    # fleche(nombre_de_pas, distance)
    min_doute, max_doute, position = fleche_stat(distance, indice_doute, nombre_de_pas)
    print(f"Avec un indice de doute de {indice_doute}, la fleche pourrait se trouver à {distance-position}m de la cible")

