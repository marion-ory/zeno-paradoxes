# Initialisation des positions
compteur = 0
position_Arbre = 8.0
position_Pierre = 0.0

# Installation du seuil puisque infini
seuil = 0.001

distance = 8.0
ecart = position_Arbre - position_Pierre


while ecart > seuil:

    # Defini l'avancée de la pierre
    pas = ecart / 2
    position_Pierre += pas
    ecart = position_Arbre - position_Pierre
    compteur += 1

    print(f"La cible, l'arbre est à {position_Arbre} mètres")
    print(f"l'écart entre la pierre et l'arbre : {ecart} mètres ")
    print(f"\nLa pierre est à {pas} metre de l'arbre")
