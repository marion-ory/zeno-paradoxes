import time
def fleche_decompte(distance=4356, duree_totale=10, nombre_de_pas=1000000):
    print("La flèche peut se situer dans un intervale de 100m par rapport à la cible, le nombre de pas possible est de 1,000,000.")
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


