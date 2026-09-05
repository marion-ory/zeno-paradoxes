import time
from random import choice

while True :
    choix_utilisateur = (input("Bienvenue dans le paradoxe de la flèche de Zénon !\nFaites votre choix entre ces trois options : \n1 - Créez un nombre d'instants de la flèche en fonctions de la distance\n2 - Figez la flèche dans un instant\n3 - Le mouvement est une illusion, recréez les instants possibles de la flèche qui ont mené à sa présence dans la cible\n4 - Fin du programme\nVotre choix : "))

    if not choix_utilisateur.isdigit() :
        print("Rentrez un nombre")
        continue

    choix_utilisateur = int(choix_utilisateur)
    
    if int(choix_utilisateur) not in (1, 2, 3, 4):
        print("Ce n'est pas une option possible du menu.")
        continue

    if choix_utilisateur == 1:
        # Fonction 1 de la flèche
        def fleche(nombre_de_pas, distance):
            taille_du_pas = (distance / nombre_de_pas)
            for i in range (1, nombre_de_pas+1) :
                position = i*taille_du_pas
                print(f"l'instant {i} se trouve à {position}m du tireur donc à {distance - position}m de la cible.")

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
            doute_nul = distance

            # Calcul de l'intervalle de présence possible des instants disponibles (les pas)
            max_doute = max(0, distance - indice_doute * largeur_par_doute)

            taille_pas = distance/nombre_de_pas 
            # Liste du total des instants et liste des instants disponibles dans l'intervalle de doute
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
        print(f"Avec un indice de doute de {indice_doute}, la fleche pourrait se trouver à {distance-position:.2f}m de la cible, dans une fourchette de {distance- doute_nul}m à {distance-max_doute}m de la cible. La dimension du pas est de {distance/nombre_de_pas}.")

    if choix_utilisateur == 4:
        print ("\nFin du programme.")
        break

    