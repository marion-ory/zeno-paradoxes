# Les Paradoxes de Zénon : Le Javelot, la Flèche et la Dichotomie 🎯

Application interactive et ludique en **Pygame** permettant d'expérimenter et de comprendre le célèbre paradoxe de la dichotomie de **Zénon d'Élée** et sa résolution par les mathématiques modernes (calcul infinitésimal et séries convergentes).

---

## 💡 Le Paradoxe de la dichotomie et sa Résolution

### 1. La vision de Zénon (L'illusion de l'inaccessible)
Zénon affirmait qu'un projectile (flèche ou javelot) ne pouvait jamais atteindre sa cible :
- Avant d'atteindre la cible ($D$), il doit d'abord atteindre la moitié ($\frac{1}{2} D$).
- Ensuite, il doit atteindre la moitié de la distance restante ($\frac{1}{4} D$).
- Puis la moitié suivante ($\frac{1}{8} D$), et ainsi de suite à l'infini.

> **L'erreur de Zénon :** Il pensait qu'une infinité d'étapes exigeait nécessairement un temps infini.

### 2. La résolution mathématique moderne
Les mathématiques ont prouvé que **le temps se divise exactement au même rythme que l'espace** :
$$\Delta t_k = \frac{\Delta d_k}{v} = \frac{D}{v \cdot 2^k}$$

La somme d'une infinité de fractions de distance forme une **série géométrique convergente** dont la somme vaut exactement **1** (100% du trajet) :
$$\sum_{k=1}^{\infty} \frac{1}{2^k} = \frac{1}{2} + \frac{1}{4} + \frac{1}{8} + \frac{1}{16} + \dots = 1$$

De même pour le temps :
$$T_{total} = \sum_{k=1}^{\infty} \Delta t_k = \frac{D}{v}$$

À l'instant $T = \frac{D}{v}$ pile, le javelot a franchi son infinité d'étapes et **touche la cible**.

---

## 🚀 Fonctionnalités du Simulateur

1. **Trois Modes de Visualisation :**
   - 🏛️ **Paradoxe de Zénon** : Décomposition étape par étape avec arrêt à chaque moitié et mise en évidence de la distance restante.
   - 📐 **Résolution Mathématique** : Trajectoire fluide en temps continu avec convergence de la somme, explosion de particules à l'impact et validation du mouvement.
   - ⚖️ **Double Vue (Comparatif)** : Les deux perspectives synchronisées en écran scindé.

2. **Personnalisation & Contrôles :**
   - Réglage de la distance totale $D$ (presets 8m, 16m, 50m, 100m ou slider continu de 2m à 100m).
   - Réglage de la vitesse du javelot $v$ (de 0.5 m/s à 10 m/s).
   - Boutons **Lancer / Pause**, **Pas Suivant** (pour avancer étape par étape) et **Réinitialiser**.

3. **Tableau Dynamique des Étapes :**
   - Affichage en temps réel de chaque étape $n$, fraction $\frac{1}{2^n}$, $\Delta d$, $\Delta t$, distance cumulée $\sum d$, temps cumulé $\sum t$ et distance restante.

4. **Outils d'Analyse :**
   - 📈 **Graphique de convergence** : Courbe continue $d = f(t)$ avec paliers de Zénon et asymptote de cible.
   - 🔬 **Loupe microscopique (Zoom)** : Visualisation des sous-divisions infinitésimales à l'approche de la cible.
   - 🔊 **Synthèse sonore procédurale** : Sons interactifs pour les étapes et l'impact.

---

## 🎮 Lancement du Programme

### Prérequis
- Python 3.8+
- Pygame (`pip install pygame`)
- NumPy (`pip install numpy`)

### Exécution
```bash
python3 main.py
# ou
python3 fleche.py
```

### Raccourcis Clavier
- <kbd>ESPACE</kbd> : Lancer / Mettre en pause la simulation
- <kbd>→</kbd> : Avancer d'une étape (Pas suivant)
- <kbd>R</kbd> : Réinitialiser la simulation
- <kbd>1</kbd> : Mode Paradoxe de Zénon
- <kbd>2</kbd> : Mode Résolution Mathématique
- <kbd>3</kbd> : Mode Double Vue (Comparatif)


## **Le paradoxe de la flèche**     
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