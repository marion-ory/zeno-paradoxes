"""
Moteur de calcul mathématique et physique pour la simulation des Paradoxes de Zénon.
Gère les calculs de distance, temps, séries géométriques convergentes et étapes de dichotomie.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ZenoStep:
    step_num: int            # Numéro de l'étape (1, 2, 3...)
    fraction_str: str        # Ex: "1/2", "1/4", "1/8"
    fraction_val: float      # Ex: 0.5, 0.25, 0.125
    delta_distance: float    # Distance franchie pendant l'étape (m)
    delta_time: float        # Temps nécessaire pour cette étape (s)
    cumul_distance: float    # Distance totale franchie jusqu'ici (m)
    cumul_time: float        # Temps total écoulé jusqu'ici (s)
    remaining_distance: float# Distance restante jusqu'à la cible (m)
    percent_done: float      # Pourcentage du trajet total (%)

class ZenoModel:
    def __init__(self, total_distance: float = 8.0, speed: float = 1.0):
        self.total_distance = max(1.0, float(total_distance))
        self.speed = max(0.1, float(speed)) # m/s
        self.total_time = self.total_distance / self.speed
        self.steps: List[ZenoStep] = []
        self._precompute_steps(max_steps=20)
        
    def update_parameters(self, total_distance: float, speed: float):
        self.total_distance = max(1.0, float(total_distance))
        self.speed = max(0.1, float(speed))
        self.total_time = self.total_distance / self.speed
        self._precompute_steps(max_steps=20)

    def _precompute_steps(self, max_steps: int = 20):
        self.steps = []
        cumul_d = 0.0
        cumul_t = 0.0
        
        for k in range(1, max_steps + 1):
            fraction_val = 1.0 / (2 ** k)
            fraction_str = f"1/{2**k}"
            delta_d = self.total_distance / (2 ** k)
            delta_t = delta_d / self.speed
            cumul_d += delta_d
            cumul_t += delta_t
            remaining_d = self.total_distance - cumul_d
            percent = (cumul_d / self.total_distance) * 100.0
            
            step = ZenoStep(
                step_num=k,
                fraction_str=fraction_str,
                fraction_val=fraction_val,
                delta_distance=delta_d,
                delta_time=delta_t,
                cumul_distance=cumul_d,
                cumul_time=cumul_t,
                remaining_distance=remaining_d,
                percent_done=percent
            )
            self.steps.append(step)

    def get_step(self, step_index: int) -> ZenoStep:
        """Récupère les informations d'une étape (0-indexed). Calcule à la volée si au-delà de 20."""
        if step_index < len(self.steps):
            return self.steps[step_index]
        
        k = step_index + 1
        fraction_val = 1.0 / (2 ** k)
        fraction_str = f"1/{2**k}" if k <= 30 else f"1/2^{k}"
        delta_d = self.total_distance / (2 ** k)
        delta_t = delta_d / self.speed
        cumul_d = self.total_distance * (1.0 - fraction_val)
        cumul_t = self.total_time * (1.0 - fraction_val)
        remaining_d = self.total_distance - cumul_d
        percent = (cumul_d / self.total_distance) * 100.0
        
        return ZenoStep(
            step_num=k,
            fraction_str=fraction_str,
            fraction_val=fraction_val,
            delta_distance=delta_d,
            delta_time=delta_t,
            cumul_distance=cumul_d,
            cumul_time=cumul_t,
            remaining_distance=remaining_d,
            percent_done=percent
        )

    def get_continuous_state(self, current_time: float) -> Dict[str, Any]:
        """Retourne l'état continu en fonction du temps physique écoulé."""
        t = max(0.0, min(current_time, self.total_time))
        d = t * self.speed
        progress = d / self.total_distance
        reached = (t >= self.total_time - 1e-6)
        
        # Trouver à quelle étape de Zénon on correspondrait
        step_idx = 0
        while step_idx < len(self.steps) and d >= self.steps[step_idx].cumul_distance:
            step_idx += 1
            
        return {
            "current_time": t,
            "current_distance": d,
            "progress": progress,
            "remaining_distance": max(0.0, self.total_distance - d),
            "is_reached": reached,
            "current_step_index": step_idx,
            "total_time": self.total_time,
            "total_distance": self.total_distance
        }
