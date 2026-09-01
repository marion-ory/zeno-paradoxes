import time
from random import randint

choix_utilisateur = int(input("Bienvenue dans le paradoxe de la flèche de Zénon !\nFaites votre choix entre ces trois options : \n1 - Créez un nombre d'instants de la flèche en fonctions de la distance\n2 - Figez la flèche dans un instant\n3 - Le mouvement est une illusion, recréez les instants possibles de la flèche qui ont mené à sa présence dans la cible\n Votre choix : "))

if choix_utilisateur == 1:
    # Fonction 1 de la flèche
    def fleche(nombre_de_pas, distance):
        taille_du_pas = (distance / nombre_de_pas)
        for i in range (1, nombre_de_pas+1) :
            position = i*taille_du_pas
            print(f"l'instant {i} se trouve à {position} du tireur.")

    nombre_de_pas = int(input("Donnez un nombre de pas : "))
    distance = int(input("Donnez une distance de la cible : "))
    fleche(nombre_de_pas, distance)


if choix_utilisateur == 2:
    def fleche_decompte(distance, duree_totale=10, nombre_de_pas=1000000):
        print("La flèche peut se situer dans un intervale de {distance} par rapport à la cible, le nombre de pas possible est de 1,000,000.")
        debut = time.time()
        decompte = duree_totale
        try:
            while decompte > 0:
                print(f"Il reste {decompte} secondes")
                time.sleep(1)
                decompte -= 1
            print("Décompte terminée, la fleche est dans la cible")

        except KeyboardInterrupt :
            # Calcul du temps écoulé
            temps_ecoule = time.time() - debut
            # L'instant_i donne un chiffre entre 1 et 1000000
            instant_i = round((temps_ecoule / duree_totale) * nombre_de_pas)
            # Position rapportée à la distance (100)
            position = instant_i/nombre_de_pas * distance
            print(f"\nLa flèche est affiché à l'instant {instant_i}")
            print(f"Elle se trouve à {position:.3f} m du tireur.")
    distance = int(input("Donnez une distance de la cible : "))
    fleche_decompte(distance)

if choix_utilisateur == 3:
    def fleche_stat(distance, indice_doute, nombre_de_pas, largeur_par_doute=1):
        max_doute = distance
        min_doute = max(0, distance - indice_doute * largeur_par_doute)
        taille_pas = (max_doute - min_doute)/nombre_de_pas 
        random_pas = randint(0, nombre_de_pas)
        position = min_doute + random_pas * taille_pas
        return min_doute, max_doute, position

    nombre_de_pas = int(input("Donnez un nombre de pas : "))
    distance = int(input("Donnez une distance de la cible : "))
    indice_doute = int(input("Donnez un indice de doute : "))

    # fleche(nombre_de_pas, distance)
    min_doute, max_doute, position = fleche_stat(distance, indice_doute, nombre_de_pas)
    print(f"Avec un indice de doute de {indice_doute}, la fleche pourrait se trouver à {distance-position:.2f}m de la cible, dans une fourchette de {min_doute}m à {max_doute}m du tireur.")

