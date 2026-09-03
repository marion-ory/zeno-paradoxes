import time

def fleche_decompte(distance, nombre_de_pas,duree_totale=10):
    print(f"La flèche peut se situer dans un intervale de {distance}m par rapport à la cible.\nLe nombre d'instant(s) possible(s) est de {nombre_de_pas}.")
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
        distance_cible = distance - position
        print(f"\nLa flèche est affiché à l'instant {instant_i}")
        print(f"Elle se trouve à {position:.2f} m du tireur, donc à {distance_cible:.2f} de la cible.")

distance = int(input("Donnez une distance de la cible : "))
nombre_de_pas = int(input("Donnez un nombre de pas (granularité) : "))
fleche_decompte(distance, nombre_de_pas)
