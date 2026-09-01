# Les Paradoxes de Zénon : Le Javelot, la Flèche et la Dichotomie 🎯

Application interactive et ludique en **Pygame** permettant d'expérimenter et de comprendre le célèbre paradoxe de la dichotomie de **Zénon d'Élée** et sa résolution par les mathématiques modernes (calcul infinitésimal et séries convergentes).

---

## 💡 Le Paradoxe et sa Résolution

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