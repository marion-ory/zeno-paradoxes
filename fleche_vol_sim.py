"""
Moteur de calcul et modélisation pour le Paradoxe de la Flèche en vol de Zénon.
Basé sur les principes de discrétisation temporelle et de figeage d'instants de menu_fleche.py.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class FlecheStep:
    step_num: int            # Numéro de l'instant (i = 1, 2, ..., N)
    instant_time: float      # Temps de l'instant (s)
    position: float          # Position de la flèche à cet instant (m)
    remaining: float         # Distance restante jusqu'à la cible (m)
    delta_d: float           # Déplacement entre chaque instant (m)
    delta_time: float        # Intervalle de temps entre deux instants (s)
    state_zenon: str         # "Immobile (Δt=0)"
    vitesse_inst: float      # Vitesse instantanée continue (m/s)

class FlecheVolModel:
    def __init__(self, distance: float = 100.0, duree_totale: float = 5.0, nombre_de_pas: int = 10):
        self.distance = max(10.0, float(distance))
        self.duree_totale = max(1.0, float(duree_totale))
        self.nombre_de_pas = max(3, int(nombre_de_pas))
        self.vitesse_reelle = self.distance / self.duree_totale
        self.total_time = self.duree_totale
        self.total_distance = self.distance
        
        self.steps: List[FlecheStep] = []
        self._precompute_steps()

    def update_parameters(self, distance: float, duree_totale: float, nombre_de_pas: int):
        self.distance = max(10.0, float(distance))
        self.duree_totale = max(1.0, float(duree_totale))
        self.nombre_de_pas = max(3, int(nombre_de_pas))
        self.vitesse_reelle = self.distance / self.duree_totale
        self.total_time = self.duree_totale
        self.total_distance = self.distance
        self._precompute_steps()

    def _precompute_steps(self):
        """Discrétisation selon la fonction fleche(nombre_de_pas, distance) de menu_fleche.py."""
        self.steps = []
        taille_du_pas = self.distance / self.nombre_de_pas
        dt_pas = self.duree_totale / self.nombre_de_pas
        
        for i in range(1, self.nombre_de_pas + 1):
            pos = i * taille_du_pas
            t_instant = i * dt_pas
            rem = max(0.0, self.distance - pos)
            
            step = FlecheStep(
                step_num=i,
                instant_time=t_instant,
                position=pos,
                remaining=rem,
                delta_d=taille_du_pas,
                delta_time=dt_pas,
                state_zenon="Immobile",
                vitesse_inst=self.vitesse_reelle
            )
            self.steps.append(step)

    def get_step(self, step_index: int) -> FlecheStep:
        if not self.steps:
            return FlecheStep(1, 0.0, 0.0, self.distance, 0.0, 0.0, "Immobile", self.vitesse_reelle)
        idx = max(0, min(len(self.steps) - 1, step_index))
        return self.steps[idx]

    def get_continuous_state(self, current_time: float) -> Dict[str, Any]:
        """Retourne l'état physique exact au temps current_time."""
        t = max(0.0, min(current_time, self.duree_totale))
        progress = t / self.duree_totale if self.duree_totale > 0 else 1.0
        pos = progress * self.distance
        rem = max(0.0, self.distance - pos)
        is_hit = (t >= self.duree_totale - 1e-6)

        # Trouver l'indice de l'instant discret correspondant
        step_idx = 0
        while step_idx < len(self.steps) and t >= self.steps[step_idx].instant_time:
            step_idx += 1

        return {
            "current_time": t,
            "position": pos,
            "remaining": rem,
            "progress": progress,
            "is_hit": is_hit,
            "current_step_index": min(step_idx, len(self.steps) - 1) if self.steps else 0,
            "total_time": self.duree_totale,
            "total_distance": self.distance,
            "vitesse_reelle": self.vitesse_reelle,
            "nombre_de_pas": self.nombre_de_pas
        }
