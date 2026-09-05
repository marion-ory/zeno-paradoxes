# **Les paradoxes de Zenon**

### **Le paradoxe de la flèche**     
Dans ce paradoxe, il est question de la division en une infinité d'instants du déplacement d'une flèche décochée vers une cible, où la vitesse de la flèche serait alors de 0.     
En effet celle ci occupe alors uniquement sa propre longueur, elle est donc immobile pendant la totalité du trajet.     
Cela tendrait à prouver que la flèche ne se déplace pas et que le mouvement de la flèche entre le décochage et son arrêt sur la cible est une illusion entraînée par cette succession infinie de temps figés : la flèche est immobile à chaque instant, elle ne peut donc se délapcer, le mouvement est impossible.     

Point 1 :      
Création d'une fonction "flèche" avec comme argument des données rentrées par l'utilisateur : nombre de pas pour pour que la flèche se rende à la cible, affichage dans le terminal de la valeur de x (la position de la flèche). Si 10 pas ont été choisis, affichage de 10 valeurs de X entre 0 et la valeur de la cible (par exemple 100).     

Point 2 :
L’utilisateur lance la flèche, qui mettra 10 secondes pour aller de 0 (elle est décochée) à 100 (la cible). L'utilisateur fait un "keyboard interrupt" pour afficher la position de la cible à l'instant de l'appui sur la touche. La flèche est alors arrêtée net (car pas de mouvement dans un instant), pour une nouvelle mesure l'utilisateur doit re lancer la flèche. Pour ce mode, les données de la valeur de la cibles sont fixées à 100, et le nombe de pas à 1000000 (pour donner ce sentiment de continuité).    

Point 3 :      
Idem point 1 avec "indice de doute" à rentrer par l'utilisateur, qui consiste à déterminer combien d'instants auront été nécessaires pour que la flèche soit plantée dans la cible : l'utilisateur construit lui même l'illusion du mouvement en donnant cet "indice du doute". L'indice du doute se reporte à plusieurs fourchettes de distances de différentes tailles, plus le coef de doute est élevé et plus la fourchette est large.

#### **Variation des résultats sur la point n°3**     
Voici les résultats associés au déroulement du point 3 :      

**Cas n°1 :** : un faible nombre de pas      
nb de pas : 50      
Distance : 100      
Indice de doute : 10      
les valeurs disponibles sont donc : 0, 2, 4, 6, 8, 10. Il y a environ 17% de chance de tomber sur une de ces 6 valeurs. On risque de voir revenir très régulièrement les mêmes valeurs au fur et à mesure des tests.     
Avec un indice de doute de 10, la flèche pourrait se trouver à 0.00m de la cible, dans une fourchette de 10m à 0m de la cible.      

**Cas n°2 :** : un grand nombre de pas      
nb de pas : 50000      
Distance : 100      
Indice de doute : 10      
Avec un indice de doute de 10, la fleche pourrait se trouver à 5.16m de la cible, dans une fourchette de 0m à 10m de la cible. La dimension du pas est de 0.002. Il y donc une forte variabilité du placement de l'instant dans l'intervalle de distance donnée, au fur et à mesure des tests.