compteur = 0
pos_fleche = 0.00
target = 100.00
time = 1.0
speed = target / time
instant = 0.1

while pos_fleche < target:
    distance_instant = speed * instant
    pos_fleche += distance_instant
    ecart = target - pos_fleche
    compteur += 1

    print(f"La flèche est à la position {pos_fleche}m (reste {target - pos_fleche}m)")
