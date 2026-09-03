"""
Moteur de calcul et pont pour le Paradoxe d'Achille et la Tortue.
Fait le lien avec les algorithmes définis dans engine.py sans en altérer la structure.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import io
import contextlib

# Import sécurisé d'engine.py (sans pollution console lors des imports de scripts annexes)
with contextlib.redirect_stdout(io.StringIO()):
    import engine

@dataclass
class AchilleStep:
    step_num: int             # Numéro d'itération (1, 2, 3...)
    pos_achille: float        # Position d'Achille à la fin de l'étape (m)
    pos_tortue: float         # Position de la Tortue à la fin de l'étape (m)
    ecart: float              # Écart entre Achille et Tortue au début de l'étape (m)
    delta_time: float         # Durée de l'étape (s)
    cumul_time: float         # Temps cumulé depuis le départ (s)
    delta_distance: float     # Distance parcourue par Achille durant cette étape (m)
    fraction_str: str         # Fraction relative de l'écart

class TortueModel:
    def __init__(self, pos_a: float = 0.0, pos_t: float = 10.0,
                 vitesse_a: float = 2.0, vitesse_t: float = 0.5, seuil: float = 0.001):
        self.pos_a_init = float(pos_a)
        self.pos_t_init = max(self.pos_a_init + 1.0, float(pos_t))
        self.vitesse_a = max(0.5, float(vitesse_a))
        self.vitesse_t = max(0.1, min(self.vitesse_a - 0.1, float(vitesse_t)))
        self.seuil = seuil
        
        self._compute_catchup()
        self._load_steps_from_engine()

    def update_parameters(self, pos_t: float, vitesse_a: float, vitesse_t: float):
        self.pos_t_init = max(self.pos_a_init + 1.0, float(pos_t))
        self.vitesse_a = max(0.5, float(vitesse_a))
        self.vitesse_t = max(0.1, min(self.vitesse_a - 0.1, float(vitesse_t)))
        self._compute_catchup()
        self._load_steps_from_engine()

    def _compute_catchup(self):
        # T_catch = (pos_T - pos_A) / (v_A - v_T)
        delta_v = max(0.001, self.vitesse_a - self.vitesse_t)
        self.total_time = (self.pos_t_init - self.pos_a_init) / delta_v
        self.catchup_distance = self.pos_a_init + self.vitesse_a * self.total_time
        # La piste doit couvrir au moins 15% au-delà du dépassement pour bien voir Achille dépasser
        self.track_distance = max(self.catchup_distance * 1.25, self.pos_t_init + 8.0, 20.0)

    def _load_steps_from_engine(self):
        """Utilise directement engine.simuler_achille sans modifier le fichier engine.py."""
        raw_history = engine.simuler_achille(
            self.pos_a_init,
            self.pos_t_init,
            self.vitesse_a,
            self.vitesse_t,
            self.seuil
        )
        self.steps: List[AchilleStep] = []
        cumul_t = 0.0
        prev_pos_a = self.pos_a_init

        ratio = self.vitesse_t / self.vitesse_a
        for h in raw_history:
            cumul_t += h["temps"]
            delta_d = h["position_Achille"] - prev_pos_a
            step_num = h["iteration"]

            if abs(ratio - 0.5) < 0.01:
                frac_str = f"1/{2**step_num}"
            else:
                frac_str = f"étape {step_num}"

            step = AchilleStep(
                step_num=step_num,
                pos_achille=h["position_Achille"],
                pos_tortue=h["position_Tortue"],
                ecart=h["ecart"],
                delta_time=h["temps"],
                cumul_time=cumul_t,
                delta_distance=delta_d,
                fraction_str=frac_str
            )
            self.steps.append(step)
            prev_pos_a = h["position_Achille"]

    def get_step(self, step_index: int) -> AchilleStep:
        if not self.steps:
            return AchilleStep(1, self.pos_t_init, self.pos_t_init, 0.0, 0.0, 0.0, 0.0, "0")
        idx = max(0, min(len(self.steps) - 1, step_index))
        return self.steps[idx]

    def get_continuous_state(self, current_time: float) -> Dict[str, Any]:
        """Retourne l'état physique continu au temps current_time."""
        t = max(0.0, current_time)
        pos_a = self.pos_a_init + self.vitesse_a * t
        pos_t = self.pos_t_init + self.vitesse_t * t
        ecart = max(0.0, pos_t - pos_a)
        is_caught = t >= self.total_time - 1e-6
        progress = min(1.0, t / self.total_time) if self.total_time > 0 else 1.0

        # Indice de l'étape de Zénon correspondante
        step_idx = 0
        while step_idx < len(self.steps) and t >= self.steps[step_idx].cumul_time:
            step_idx += 1

        return {
            "current_time": t,
            "pos_achille": pos_a,
            "pos_tortue": pos_t,
            "ecart": ecart,
            "is_caught": is_caught,
            "progress": progress,
            "current_step_index": min(step_idx, len(self.steps) - 1) if self.steps else 0,
            "total_time": self.total_time,
            "catchup_distance": self.catchup_distance,
            "track_distance": self.track_distance,
        }
