"""
Application interactive Pygame : Les Paradoxes de Zénon
1. La Dichotomie & Le Javelot
2. Achille et la Tortue (Moteur engine.py)
3. La Flèche en vol (Moteur menu_fleche.py)
Version 3.5 Multi-Paradoxes : 3 Menus sur le Dashboard, visualisations adaptées et contrôles interactifs.
"""
import pygame
import sys
import math
import numpy as np
from typing import Optional

from zeno_sim import ZenoModel
from tortue_sim import TortueModel
from fleche_vol_sim import FlecheVolModel
from ui_components import COLORS, Button, Slider, DataTable, MiniGraph, ZoomLoupe, ParticleSystem

# Initialisation de Pygame et Audio
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception:
    pass

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    font_names = ["Helvetica Neue", "Arial", "Segoe UI", "DejaVu Sans", "sans-serif"]
    for name in font_names:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

class SoundSynth:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.step_sound = self._create_beep(freq=640, duration=0.07, wave_type="sine") if self.enabled else None
        self.impact_sound = self._create_beep(freq=180, duration=0.28, wave_type="impact") if self.enabled else None
        self.click_sound = self._create_beep(freq=880, duration=0.04, wave_type="sine") if self.enabled else None
        self.infinity_sound = self._create_beep(freq=1050, duration=0.35, wave_type="infinity") if self.enabled else None

    def _create_beep(self, freq: float, duration: float, wave_type: str = "sine") -> Optional[pygame.mixer.Sound]:
        if not self.enabled:
            return None
        try:
            sample_rate = 44100
            n_samples = int(round(duration * sample_rate))
            buf = np.zeros((n_samples, 2), dtype=np.int16)
            max_amp = 19000

            for i in range(n_samples):
                t = i / sample_rate
                if wave_type == "sine":
                    envelope = math.exp(-i / (n_samples * 0.35))
                    val = max_amp * envelope * math.sin(2 * math.pi * freq * t)
                elif wave_type == "impact":
                    envelope = math.exp(-i / (n_samples * 0.2))
                    noise = (np.random.rand() * 2 - 1) * 0.35
                    val = max_amp * envelope * (math.sin(2 * math.pi * freq * t) * 0.65 + noise)
                elif wave_type == "infinity":
                    envelope = math.exp(-i / (n_samples * 0.6))
                    val = max_amp * envelope * (math.sin(2 * math.pi * freq * t) + 0.5 * math.sin(2 * math.pi * freq * 1.5 * t))
                buf[i, 0] = int(val)
                buf[i, 1] = int(val)
            return pygame.sndarray.make_sound(buf)
        except Exception:
            return None

    def play_step(self):
        if self.step_sound: self.step_sound.play()
    def play_impact(self):
        if self.impact_sound: self.impact_sound.play()
    def play_click(self):
        if self.click_sound: self.click_sound.play()
    def play_infinity(self):
        if self.infinity_sound: self.infinity_sound.play()


class ZenoApp:
    def __init__(self):
        self.width = 1360
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("Les Paradoxes de Zénon : La Dichotomie, La Tortue & La Flèche (v3.5)")
        self.clock = pygame.time.Clock()
        self.running = True

        # Polices nettes
        self.font_title = get_font(21, bold=True)
        self.font_subtitle = get_font(13, bold=False)
        self.font_ui = get_font(13, bold=False)
        self.font_ui_bold = get_font(13, bold=True)
        self.font_big_val = get_font(18, bold=True)
        self.font_infinity = get_font(26, bold=True)

        # Sélection de la simulation active : "DICHOTOMIE", "TORTUE", "FLECHE"
        self.current_sim = "DICHOTOMIE"

        # 1. Modèle Dichotomie
        self.dichotomie_dist = 8.0
        self.dichotomie_speed = 1.0
        self.model_dichotomie = ZenoModel(total_distance=self.dichotomie_dist, speed=self.dichotomie_speed)

        # 2. Modèle Tortue (issu de engine.py)
        self.pos_tortue_init = 10.0
        self.vitesse_achille = 2.0
        self.vitesse_tortue = 0.5
        self.model_tortue = TortueModel(
            pos_a=0.0,
            pos_t=self.pos_tortue_init,
            vitesse_a=self.vitesse_achille,
            vitesse_t=self.vitesse_tortue
        )

        # 3. Modèle Flèche en vol (issu de menu_fleche.py)
        self.fleche_dist = 100.0
        self.fleche_duree = 5.0
        self.fleche_pas = 10
        self.model_fleche = FlecheVolModel(
            distance=self.fleche_dist,
            duree_totale=self.fleche_duree,
            nombre_de_pas=self.fleche_pas
        )

        # État courant de la simulation
        self.mode = "REAL"  # "ZENON", "REAL", "SPLIT"
        self.is_playing = False
        self.sim_time = 0.0
        self.step_idx = 0
        self.sim_speed_mult = 1.0
        self.impact_triggered = False
        self.infinity_active = False

        # Effets visuels & Audio
        self.particles = ParticleSystem()
        self.sound = SoundSynth()
        self.right_tab = "GRAPH"  # "GRAPH" ou "LOUPE"

        # Initialisation UI
        self._init_ui()
        self._reposition_layout()

    @property
    def active_model(self):
        if self.current_sim == "TORTUE":
            return self.model_tortue
        elif self.current_sim == "FLECHE":
            return self.model_fleche
        else:
            return self.model_dichotomie

    def _init_ui(self):
        # 1. Menu supérieur à 3 simulations (Dashboard Navigation Tabs)
        self.btn_sim_dichotomie = Button(0, 0, 140, 36, "📏 Dichotomie",
                                         callback=lambda: self.set_sim("DICHOTOMIE"), color=COLORS["cyan"], active=True)
        self.btn_sim_tortue = Button(0, 0, 175, 36, "🐢 Achille & Tortue",
                                     callback=lambda: self.set_sim("TORTUE"), color=COLORS["emerald"])
        self.btn_sim_fleche = Button(0, 0, 140, 36, "🏹 La Flèche",
                                     callback=lambda: self.set_sim("FLECHE"), color=COLORS["gold"])

        # 2. Boutons de modes (Paradoxe, Résolution, Comparer)
        self.btn_mode_zenon = Button(0, 0, 135, 36, "Paradoxe",
                                     callback=lambda: self.set_mode("ZENON"), color=COLORS["gold"])
        self.btn_mode_real = Button(0, 0, 145, 36, "Résolution",
                                    callback=lambda: self.set_mode("REAL"), color=COLORS["cyan"], active=True)
        self.btn_mode_split = Button(0, 0, 130, 36, "Comparer",
                                     callback=lambda: self.set_mode("SPLIT"), color=COLORS["purple"])

        # 3. Contrôles Dichotomie
        self.slider_distance = Slider(24, 0, 246, 24, min_val=2.0, max_val=100.0,
                                      initial_val=self.dichotomie_dist, label="Distance Totale", unit="m", step=1.0,
                                      on_change=self._on_distance_changed)
        self.slider_speed = Slider(24, 0, 246, 24, min_val=0.5, max_val=10.0,
                                   initial_val=self.dichotomie_speed, label="Vitesse Javelot", unit="m/s", step=0.5,
                                   on_change=self._on_speed_changed)

        self.btn_p8 = Button(0, 0, 56, 24, "8 m", callback=lambda: self.set_preset_dichotomie(8.0), color=COLORS["panel_card"])
        self.btn_p16 = Button(0, 0, 56, 24, "16 m", callback=lambda: self.set_preset_dichotomie(16.0), color=COLORS["panel_card"])
        self.btn_p50 = Button(0, 0, 56, 24, "50 m", callback=lambda: self.set_preset_dichotomie(50.0), color=COLORS["panel_card"])
        self.btn_p100 = Button(0, 0, 62, 24, "100 m", callback=lambda: self.set_preset_dichotomie(100.0), color=COLORS["panel_card"])

        # 4. Contrôles Tortue
        self.slider_pos_t = Slider(24, 0, 246, 24, min_val=2.0, max_val=50.0,
                                   initial_val=self.pos_tortue_init, label="Avance Tortue", unit="m", step=1.0,
                                   on_change=self._on_tortue_pos_changed)
        self.slider_v_a = Slider(24, 0, 246, 24, min_val=1.0, max_val=10.0,
                                 initial_val=self.vitesse_achille, label="Vitesse Achille", unit="m/s", step=0.5,
                                 on_change=self._on_achille_speed_changed)
        self.slider_v_t = Slider(24, 0, 246, 24, min_val=0.2, max_val=4.0,
                                 initial_val=self.vitesse_tortue, label="Vitesse Tortue", unit="m/s", step=0.1,
                                 on_change=self._on_tortue_speed_changed)

        self.btn_t10 = Button(0, 0, 56, 22, "10 m", callback=lambda: self.set_preset_tortue(10.0, 2.0, 0.5), color=COLORS["panel_card"])
        self.btn_t20 = Button(0, 0, 56, 22, "20 m", callback=lambda: self.set_preset_tortue(20.0, 2.5, 1.0), color=COLORS["panel_card"])
        self.btn_t5 = Button(0, 0, 56, 22, "5 m", callback=lambda: self.set_preset_tortue(5.0, 3.0, 0.5), color=COLORS["panel_card"])
        self.btn_t15 = Button(0, 0, 62, 22, "15 m", callback=lambda: self.set_preset_tortue(15.0, 4.0, 1.0), color=COLORS["panel_card"])

        # 5. Contrôles Flèche en vol (menu_fleche.py)
        self.slider_fl_dist = Slider(24, 0, 246, 24, min_val=20.0, max_val=200.0,
                                     initial_val=self.fleche_dist, label="Distance Cible", unit="m", step=10.0,
                                     on_change=self._on_fl_dist_changed)
        self.slider_fl_duree = Slider(24, 0, 246, 24, min_val=1.0, max_val=20.0,
                                      initial_val=self.fleche_duree, label="Durée Totale", unit="s", step=0.5,
                                      on_change=self._on_fl_duree_changed)
        self.slider_fl_pas = Slider(24, 0, 246, 24, min_val=4.0, max_val=40.0,
                                    initial_val=self.fleche_pas, label="Nombre d'instants", unit="pas", step=1.0,
                                    on_change=self._on_fl_pas_changed)

        self.btn_fl_p20 = Button(0, 0, 56, 22, "20 m", callback=lambda: self.set_preset_fleche(20.0, 2.0, 5), color=COLORS["panel_card"])
        self.btn_fl_p50 = Button(0, 0, 56, 22, "50 m", callback=lambda: self.set_preset_fleche(50.0, 3.0, 10), color=COLORS["panel_card"])
        self.btn_fl_p100 = Button(0, 0, 56, 22, "100m", callback=lambda: self.set_preset_fleche(100.0, 5.0, 10), color=COLORS["panel_card"])
        self.btn_fl_p200 = Button(0, 0, 62, 22, "200m", callback=lambda: self.set_preset_fleche(200.0, 8.0, 20), color=COLORS["panel_card"])

        # 6. Boutons d'action principaux
        self.btn_play = Button(0, 0, 120, 32, "Lancer", callback=self.toggle_play, color=COLORS["emerald"])
        self.btn_step = Button(0, 0, 120, 32, "Étape suivante", callback=self.next_step, color=COLORS["gold"])
        self.btn_infinity = Button(0, 0, 246, 30, "Voir la limite n → ∞", callback=self.trigger_infinity, color=COLORS["infinity_color"])
        self.btn_reset = Button(0, 0, 246, 24, "Réinitialiser", callback=self.reset_sim, color=COLORS["panel_card"])

        # 7. Tableau de données
        self.data_table = DataTable(0, 0, 540, 230)
        self.data_table.set_data(self.active_model.steps, active_step=-1)

        # 8. Panneau droit : Graphique & Loupe
        self.mini_graph = MiniGraph(0, 0, 460, 195)
        self.zoom_loupe = ZoomLoupe(0, 0, 460, 195)

        self.btn_tab_graph = Button(0, 0, 225, 28, "Graphique",
                                    callback=lambda: self.set_right_tab("GRAPH"), color=COLORS["cyan"], active=True)
        self.btn_tab_loupe = Button(0, 0, 225, 28, "Loupe ×50",
                                    callback=lambda: self.set_right_tab("LOUPE"), color=COLORS["gold"])

    def _reposition_layout(self):
        """Repositionne dynamiquement tous les éléments selon la taille de l'écran."""
        right_margin = 24
        btn_y = 16
        spacing = 8

        # Modes alignés à droite
        w_split = 125
        w_real = 135
        w_zenon = 130

        x_split = self.width - right_margin - w_split
        x_real = x_split - spacing - w_real
        x_zenon = x_real - spacing - w_zenon

        self.btn_mode_zenon.set_position(x_zenon, btn_y, w_zenon, 36)
        self.btn_mode_real.set_position(x_real, btn_y, w_real, 36)
        self.btn_mode_split.set_position(x_split, btn_y, w_split, 36)

        # 3 Menus de simulation au centre
        sim_w1 = 135
        sim_w2 = 170
        sim_w3 = 135
        total_sim_w = sim_w1 + sim_w2 + sim_w3 + 20
        sim_start_x = max(360, (x_zenon - total_sim_w) // 2 + 180)

        self.btn_sim_dichotomie.set_position(sim_start_x, btn_y, sim_w1, 36)
        self.btn_sim_tortue.set_position(sim_start_x + sim_w1 + 10, btn_y, sim_w2, 36)
        self.btn_sim_fleche.set_position(sim_start_x + sim_w1 + sim_w2 + 20, btn_y, sim_w3, 36)

        # Zone inférieure
        panel_y = self.height - 275
        ctrl_w = 260
        gap = 16

        # Contrôles Dichotomie
        self.slider_distance.set_position(24, panel_y + 42, ctrl_w)
        self.slider_speed.set_position(24, panel_y + 92, ctrl_w)

        p_w = (ctrl_w - 18) // 4
        self.btn_p8.set_position(24, panel_y + 122, p_w, 24)
        self.btn_p16.set_position(24 + p_w + 6, panel_y + 122, p_w, 24)
        self.btn_p50.set_position(24 + (p_w + 6) * 2, panel_y + 122, p_w, 24)
        self.btn_p100.set_position(24 + (p_w + 6) * 3, panel_y + 122, p_w, 24)

        # Contrôles Tortue
        self.slider_pos_t.set_position(24, panel_y + 36, ctrl_w)
        self.slider_v_a.set_position(24, panel_y + 74, ctrl_w)
        self.slider_v_t.set_position(24, panel_y + 112, ctrl_w)

        self.btn_t10.set_position(24, panel_y + 138, p_w, 22)
        self.btn_t20.set_position(24 + p_w + 6, panel_y + 138, p_w, 22)
        self.btn_t5.set_position(24 + (p_w + 6) * 2, panel_y + 138, p_w, 22)
        self.btn_t15.set_position(24 + (p_w + 6) * 3, panel_y + 138, p_w, 22)

        # Contrôles Flèche en vol
        self.slider_fl_dist.set_position(24, panel_y + 36, ctrl_w)
        self.slider_fl_duree.set_position(24, panel_y + 74, ctrl_w)
        self.slider_fl_pas.set_position(24, panel_y + 112, ctrl_w)

        self.btn_fl_p20.set_position(24, panel_y + 138, p_w, 22)
        self.btn_fl_p50.set_position(24 + p_w + 6, panel_y + 138, p_w, 22)
        self.btn_fl_p100.set_position(24 + (p_w + 6) * 2, panel_y + 138, p_w, 22)
        self.btn_fl_p200.set_position(24 + (p_w + 6) * 3, panel_y + 138, p_w, 22)

        # Actions
        act_w = (ctrl_w - 8) // 2
        self.btn_play.set_position(24, panel_y + 166, act_w, 32)
        self.btn_step.set_position(24 + act_w + 8, panel_y + 166, act_w, 32)
        self.btn_infinity.set_position(24, panel_y + 203, ctrl_w, 30)
        self.btn_reset.set_position(24, panel_y + 237, ctrl_w, 24)

        # Tableau
        middle_x = 24 + ctrl_w + gap
        remaining_w = self.width - middle_x - 24
        table_w = int(remaining_w * 0.54)
        right_w = remaining_w - table_w - gap

        self.data_table.set_position(middle_x, panel_y, table_w, 260)

        # Panneau Droit
        right_x = middle_x + table_w + gap
        tab_w = (right_w - 10) // 2
        self.btn_tab_graph.set_position(right_x, panel_y, tab_w, 28)
        self.btn_tab_loupe.set_position(right_x + tab_w + 10, panel_y, tab_w, 28)

        self.mini_graph.set_position(right_x, panel_y + 35, right_w, 225)
        self.zoom_loupe.set_position(right_x, panel_y + 35, right_w, 225)

    def set_sim(self, new_sim: str):
        if self.current_sim == new_sim:
            return
        self.current_sim = new_sim
        self.btn_sim_dichotomie.active = (new_sim == "DICHOTOMIE")
        self.btn_sim_tortue.active = (new_sim == "TORTUE")
        self.btn_sim_fleche.active = (new_sim == "FLECHE")

        self.data_table.set_sim_type(new_sim)
        self.data_table.set_data(self.active_model.steps, active_step=-1)
        self.reset_sim(play_sound=False)
        self.sound.play_click()

    def set_right_tab(self, tab: str):
        self.right_tab = tab
        self.btn_tab_graph.active = (tab == "GRAPH")
        self.btn_tab_loupe.active = (tab == "LOUPE")
        self.sound.play_click()

    def set_mode(self, new_mode: str):
        self.mode = new_mode
        self.btn_mode_zenon.active = (new_mode == "ZENON")
        self.btn_mode_real.active = (new_mode == "REAL")
        self.btn_mode_split.active = (new_mode == "SPLIT")
        self.sound.play_click()
        self.reset_sim(play_sound=False)

    # --- Callbacks Dichotomie ---
    def set_preset_dichotomie(self, dist: float):
        self.dichotomie_dist = dist
        self.slider_distance.set_value(dist)
        self._on_distance_changed(dist)
        self.sound.play_click()

    def _on_distance_changed(self, new_d: float):
        self.dichotomie_dist = new_d
        self.model_dichotomie.update_parameters(self.dichotomie_dist, self.dichotomie_speed)
        self.data_table.set_data(self.model_dichotomie.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_speed_changed(self, new_v: float):
        self.dichotomie_speed = new_v
        self.model_dichotomie.update_parameters(self.dichotomie_dist, self.dichotomie_speed)
        self.data_table.set_data(self.model_dichotomie.steps, self.step_idx, self.infinity_active)

    # --- Callbacks Tortue ---
    def set_preset_tortue(self, pos_t: float, v_a: float, v_t: float):
        self.pos_tortue_init = pos_t
        self.vitesse_achille = v_a
        self.vitesse_tortue = v_t
        self.slider_pos_t.set_value(pos_t)
        self.slider_v_a.set_value(v_a)
        self.slider_v_t.set_value(v_t)
        self.model_tortue.update_parameters(self.pos_tortue_init, self.vitesse_achille, self.vitesse_tortue)
        self.data_table.set_data(self.model_tortue.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_tortue_pos_changed(self, new_pos: float):
        self.pos_tortue_init = new_pos
        self.model_tortue.update_parameters(self.pos_tortue_init, self.vitesse_achille, self.vitesse_tortue)
        self.data_table.set_data(self.model_tortue.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_achille_speed_changed(self, new_v_a: float):
        self.vitesse_achille = max(new_v_a, self.vitesse_tortue + 0.1)
        self.model_tortue.update_parameters(self.pos_tortue_init, self.vitesse_achille, self.vitesse_tortue)
        self.data_table.set_data(self.model_tortue.steps, self.step_idx, self.infinity_active)

    def _on_tortue_speed_changed(self, new_v_t: float):
        self.vitesse_tortue = min(new_v_t, self.vitesse_achille - 0.1)
        self.model_tortue.update_parameters(self.pos_tortue_init, self.vitesse_achille, self.vitesse_tortue)
        self.data_table.set_data(self.model_tortue.steps, self.step_idx, self.infinity_active)

    # --- Callbacks Flèche en vol (menu_fleche.py) ---
    def set_preset_fleche(self, dist: float, duree: float, pas: int):
        self.fleche_dist = dist
        self.fleche_duree = duree
        self.fleche_pas = pas
        self.slider_fl_dist.set_value(dist)
        self.slider_fl_duree.set_value(duree)
        self.slider_fl_pas.set_value(pas)
        self.model_fleche.update_parameters(dist, duree, pas)
        self.data_table.set_data(self.model_fleche.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_fl_dist_changed(self, new_d: float):
        self.fleche_dist = new_d
        self.model_fleche.update_parameters(self.fleche_dist, self.fleche_duree, self.fleche_pas)
        self.data_table.set_data(self.model_fleche.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_fl_duree_changed(self, new_dur: float):
        self.fleche_duree = new_dur
        self.model_fleche.update_parameters(self.fleche_dist, self.fleche_duree, self.fleche_pas)
        self.data_table.set_data(self.model_fleche.steps, self.step_idx, self.infinity_active)

    def _on_fl_pas_changed(self, new_pas: float):
        self.fleche_pas = int(new_pas)
        self.model_fleche.update_parameters(self.fleche_dist, self.fleche_duree, self.fleche_pas)
        self.data_table.set_data(self.model_fleche.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def toggle_play(self):
        m = self.active_model
        is_finished = (
            self.infinity_active
            or self.sim_time >= m.total_time - 1e-6
            or (self.mode == "ZENON" and self.step_idx >= len(m.steps) - 1)
        )
        if is_finished and not self.is_playing:
            self.reset_sim(play_sound=False)
        self.is_playing = not self.is_playing
        self.btn_play.text = "Pause" if self.is_playing else "Reprendre"
        self.btn_play.base_color = COLORS["gold"] if self.is_playing else COLORS["emerald"]
        self.sound.play_click()

    def next_step(self):
        m = self.active_model
        if self.step_idx < len(m.steps) - 1:
            self.step_idx += 1
            step = m.get_step(self.step_idx)
            self.sim_time = step.instant_time if hasattr(step, "instant_time") else step.cumul_time
            self.data_table.active_step_idx = self.step_idx
            self.sound.play_step()

            if self.step_idx >= len(m.steps) - 1 and not self.impact_triggered:
                self.impact_triggered = True
                self.sound.play_impact()
                target_x = self.width - 100
                target_y = 230
                self.particles.emit_impact(target_x, target_y, count=45)

        self._update_control_states()

    def trigger_infinity(self):
        m = self.active_model
        self.infinity_active = True
        self.is_playing = False
        self.sim_time = m.total_time
        self.step_idx = len(m.steps)
        self.data_table.set_data(m.steps, self.step_idx, show_infinity=True)
        self.sound.play_infinity()

        target_x = self.width - 100
        target_y = 230 if self.mode != "SPLIT" else 350
        self.particles.emit_impact(target_x, target_y, count=80, theme="infinity")
        self._update_control_states()

    def reset_sim(self, play_sound: bool = True):
        self.is_playing = False
        self.sim_time = 0.0
        self.step_idx = 0
        self.impact_triggered = False
        self.infinity_active = False
        self.btn_play.text = "Lancer"
        self.btn_play.base_color = COLORS["emerald"]
        self.data_table.set_data(self.active_model.steps, active_step=-1, show_infinity=False)
        self.particles.particles.clear()
        self._update_control_states()
        if play_sound:
            self.sound.play_click()

    def _update_control_states(self):
        m = self.active_model
        self.btn_step.disabled = self.infinity_active or self.step_idx >= len(m.steps) - 1
        self.btn_infinity.disabled = self.infinity_active

    def update(self, dt: float):
        m = self.active_model

        all_btns = [
            self.btn_sim_dichotomie, self.btn_sim_tortue, self.btn_sim_fleche,
            self.btn_mode_zenon, self.btn_mode_real, self.btn_mode_split,
            self.btn_play, self.btn_step, self.btn_infinity, self.btn_reset,
            self.btn_tab_graph, self.btn_tab_loupe
        ]
        if self.current_sim == "DICHOTOMIE":
            all_btns.extend([self.btn_p8, self.btn_p16, self.btn_p50, self.btn_p100])
        elif self.current_sim == "TORTUE":
            all_btns.extend([self.btn_t10, self.btn_t20, self.btn_t5, self.btn_t15])
        else:
            all_btns.extend([self.btn_fl_p20, self.btn_fl_p50, self.btn_fl_p100, self.btn_fl_p200])

        for btn in all_btns:
            btn.update(dt)

        self.particles.update(dt)
        self._update_control_states()

        if self.is_playing:
            eff_dt = dt * self.sim_speed_mult

            if self.mode == "REAL":
                self.sim_time += eff_dt
                if self.sim_time >= m.total_time:
                    self.sim_time = m.total_time
                    self.is_playing = False
                    self.btn_play.text = "Recommencer"
                    self.btn_play.base_color = COLORS["emerald"]
                    if not self.impact_triggered:
                        self.impact_triggered = True
                        self.sound.play_impact()
                        target_x = self.width - 100
                        target_y = 230
                        self.particles.emit_impact(target_x, target_y, count=60)

            elif self.mode == "ZENON":
                step_duration = 0.85
                self.sim_time += eff_dt
                target_step_time = (self.step_idx + 1) * step_duration

                if self.sim_time >= target_step_time:
                    if self.step_idx < len(m.steps) - 1:
                        self.step_idx += 1
                        self.sound.play_step()
                    else:
                        self.is_playing = False
                        self.btn_play.text = "Recommencer"

            elif self.mode == "SPLIT":
                self.sim_time += eff_dt
                if self.sim_time >= m.total_time:
                    self.sim_time = m.total_time
                    self.is_playing = False
                    self.btn_play.text = "Recommencer"
                    if not self.impact_triggered:
                        self.impact_triggered = True
                        self.sound.play_impact()
                        self.particles.emit_impact(self.width - 100, 350, count=55)

            st = m.get_continuous_state(self.sim_time)
            self.data_table.active_step_idx = st["current_step_index"]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width = max(1120, event.w)
                self.height = max(720, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.RESIZABLE)
                self._reposition_layout()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.toggle_play()
                elif event.key == pygame.K_RIGHT:
                    self.next_step()
                elif event.key == pygame.K_i:
                    self.trigger_infinity()
                elif event.key == pygame.K_r:
                    self.reset_sim()
                elif event.key == pygame.K_1:
                    self.set_mode("ZENON")
                elif event.key == pygame.K_2:
                    self.set_mode("REAL")
                elif event.key == pygame.K_3:
                    self.set_mode("SPLIT")
                elif event.key == pygame.K_d:
                    self.set_sim("DICHOTOMIE")
                elif event.key == pygame.K_t:
                    self.set_sim("TORTUE")
                elif event.key == pygame.K_f:
                    self.set_sim("FLECHE")

            # UI Events
            self.btn_sim_dichotomie.handle_event(event)
            self.btn_sim_tortue.handle_event(event)
            self.btn_sim_fleche.handle_event(event)

            self.btn_mode_zenon.handle_event(event)
            self.btn_mode_real.handle_event(event)
            self.btn_mode_split.handle_event(event)

            if self.current_sim == "DICHOTOMIE":
                self.slider_distance.handle_event(event)
                self.slider_speed.handle_event(event)
                self.btn_p8.handle_event(event)
                self.btn_p16.handle_event(event)
                self.btn_p50.handle_event(event)
                self.btn_p100.handle_event(event)
            elif self.current_sim == "TORTUE":
                self.slider_pos_t.handle_event(event)
                self.slider_v_a.handle_event(event)
                self.slider_v_t.handle_event(event)
                self.btn_t10.handle_event(event)
                self.btn_t20.handle_event(event)
                self.btn_t5.handle_event(event)
                self.btn_t15.handle_event(event)
            else:
                self.slider_fl_dist.handle_event(event)
                self.slider_fl_duree.handle_event(event)
                self.slider_fl_pas.handle_event(event)
                self.btn_fl_p20.handle_event(event)
                self.btn_fl_p50.handle_event(event)
                self.btn_fl_p100.handle_event(event)
                self.btn_fl_p200.handle_event(event)

            self.btn_play.handle_event(event)
            self.btn_step.handle_event(event)
            self.btn_infinity.handle_event(event)
            self.btn_reset.handle_event(event)

            self.data_table.handle_event(event)
            self.btn_tab_graph.handle_event(event)
            self.btn_tab_loupe.handle_event(event)

    def draw(self):
        self.screen.fill(COLORS["bg_dark"])

        # 1. En-tête / Titre, 3 Menus de simulation et Modes
        self._draw_header()

        # 2. Zone de visualisation
        if self.current_sim == "DICHOTOMIE":
            if self.mode == "SPLIT":
                self._draw_dichotomie_split_tracks()
            else:
                self._draw_dichotomie_single_track()
        elif self.current_sim == "TORTUE":
            if self.mode == "SPLIT":
                self._draw_tortue_split_tracks()
            else:
                self._draw_tortue_single_track()
        else:
            if self.mode == "SPLIT":
                self._draw_fleche_split_tracks()
            else:
                self._draw_fleche_single_track()

        # 3. Panneaux du bas
        self._draw_bottom_panel()

        # 4. Particules
        self.particles.draw(self.screen)

        pygame.display.flip()

    def _draw_header(self):
        title_surf = self.font_title.render("LES PARADOXES DE ZÉNON", True, COLORS["text_main"])
        self.screen.blit(title_surf, (24, 14))

        if self.current_sim == "DICHOTOMIE":
            sub_text = "1. La Dichotomie · Succession infinie de moitiés (1/2, 1/4, 1/8...)"
        elif self.current_sim == "TORTUE":
            sub_text = "2. Achille & la Tortue · Série convergente calculée par engine.py"
        else:
            sub_text = "3. La Flèche en vol · Mouvement balistique continu vs Instants figés (menu_fleche.py)"
        sub_surf = self.font_subtitle.render(sub_text, True, COLORS["text_muted"])
        self.screen.blit(sub_surf, (24, 42))

        # 3 Menus de sélection au centre
        self.btn_sim_dichotomie.draw(self.screen, self.font_ui_bold)
        self.btn_sim_tortue.draw(self.screen, self.font_ui_bold)
        self.btn_sim_fleche.draw(self.screen, self.font_ui_bold)

        # Boutons de modes à droite
        self.btn_mode_zenon.draw(self.screen, self.font_ui_bold)
        self.btn_mode_real.draw(self.screen, self.font_ui_bold)
        self.btn_mode_split.draw(self.screen, self.font_ui_bold)

    # =========================================================================
    # SIMULATION 1 : LA DICHOTOMIE (1/2, 1/4, 1/8...)
    # =========================================================================
    def _draw_dichotomie_single_track(self):
        track_y = 225
        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        self._draw_dichotomie_banner(frame_rect.x + 16, frame_rect.y + 12, frame_rect.width - 32)

        piste_rect = pygame.Rect(track_start_x - 30, track_y - 45, track_w + 60, 90)
        pygame.draw.rect(self.screen, COLORS["track_bg"], piste_rect, border_radius=8)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, track_y), (track_end_x, track_y), 4)

        pygame.draw.circle(self.screen, COLORS["white"], (track_start_x, track_y), 6)
        start_lbl = self.font_ui_bold.render("Départ (0 m)", True, COLORS["text_muted"])
        self.screen.blit(start_lbl, (track_start_x - 35, track_y + 18))

        self._draw_target(track_end_x, track_y, self.model_dichotomie.total_distance)

        for i, step in enumerate(self.model_dichotomie.steps[:6]):
            frac_ratio = step.cumul_distance / self.model_dichotomie.total_distance
            jx = track_start_x + int(frac_ratio * track_w)

            pygame.draw.line(self.screen, COLORS["panel_border_bright"], (jx, track_y - 20), (jx, track_y + 20), 2)
            frac_lbl = self.font_ui_bold.render(step.fraction_str if i == 0 else f"+{step.fraction_str}", True, COLORS["gold"])
            self.screen.blit(frac_lbl, (jx - 14, track_y - 38))

            dist_lbl = self.font_ui.render(f"{step.cumul_distance:g}m", True, COLORS["text_muted"])
            self.screen.blit(dist_lbl, (jx - 12, track_y + 22))

        if self.infinity_active:
            self._draw_javelin(track_end_x, track_y, infinity_glow=True)
            self._draw_infinity_overlay(track_start_x, track_y + 60, self.model_dichotomie.total_distance, self.model_dichotomie.total_time)
        elif self.mode == "REAL":
            st = self.model_dichotomie.get_continuous_state(self.sim_time)
            cur_ratio = min(1.0, st["current_distance"] / self.model_dichotomie.total_distance)
            jx = track_start_x + int(cur_ratio * track_w)
            self._draw_javelin(jx, track_y)
            self._draw_live_stats_overlay(track_start_x, track_y + 70, st["current_distance"], st["current_time"],
                                         st["remaining_distance"], st["progress"])
        elif self.mode == "ZENON":
            step = self.model_dichotomie.get_step(self.step_idx)
            cur_ratio = step.cumul_distance / self.model_dichotomie.total_distance
            jx = track_start_x + int(cur_ratio * track_w)
            self._draw_javelin(jx, track_y)
            self._draw_zenon_step_overlay(track_start_x, track_y + 60, step)

    def _draw_dichotomie_split_tracks(self):
        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        y_zenon = 175
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_zenon), (track_end_x, y_zenon), 3)
        self._draw_target(track_end_x, y_zenon, self.model_dichotomie.total_distance)
        lbl_z = self.font_ui_bold.render("1. Point de vue de Zénon (Découpage discret : 'Infinité d'arrêts')", True, COLORS["gold"])
        self.screen.blit(lbl_z, (track_start_x, y_zenon - 45))

        st = self.model_dichotomie.get_continuous_state(self.sim_time)
        zenon_step = self.model_dichotomie.get_step(st["current_step_index"])
        zx = track_start_x + int((zenon_step.cumul_distance / self.model_dichotomie.total_distance) * track_w)
        self._draw_javelin(zx, y_zenon)

        y_real = 345
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_real), (track_end_x, y_real), 3)
        self._draw_target(track_end_x, y_real, self.model_dichotomie.total_distance)
        lbl_r = self.font_ui_bold.render("2. Réalité Physique & Mathématique (Mouvement continu & Limite)", True, COLORS["cyan"])
        self.screen.blit(lbl_r, (track_start_x, y_real - 45))

        rx = track_start_x + int(st["progress"] * track_w)
        self._draw_javelin(rx, y_real)

        info_t = f"Temps écoulé : {st['current_time']:.2f}s / {self.model_dichotomie.total_time:.2f}s  |  Distance : {st['current_distance']:.2f}m / {self.model_dichotomie.total_distance:.2f}m"
        info_surf = self.font_ui_bold.render(info_t, True, COLORS["text_main"])
        self.screen.blit(info_surf, (track_start_x, 430))

    def _draw_dichotomie_banner(self, x: int, y: int, width: int):
        banner_rect = pygame.Rect(x, y, width, 55)
        if self.infinity_active:
            pygame.draw.rect(self.screen, (50, 18, 70), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["infinity_color"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Limite atteinte · n → ∞", True, COLORS["infinity_color"])
            t2 = self.font_ui.render(f"La série vaut 1 : {self.model_dichotomie.total_distance:g} m franchis en {self.model_dichotomie.total_time:g} s, 0 m restant.", True, COLORS["text_main"])
        elif self.mode == "ZENON":
            pygame.draw.rect(self.screen, (45, 34, 15), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["gold"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Le paradoxe · une succession infinie de moitiés", True, COLORS["gold"])
            t2 = self.font_ui.render("1/2, puis 1/4, puis 1/8… Zénon conclut à tort qu'une infinité d'étapes impose un temps infini.", True, COLORS["text_main"])
        elif self.mode == "REAL":
            pygame.draw.rect(self.screen, (15, 45, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["cyan"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("La résolution · une série géométrique convergente", True, COLORS["cyan"])
            t2 = self.font_ui.render(f"Le temps se divise comme l'espace : la cible est touchée exactement à t = {self.model_dichotomie.total_time:g} s.", True, COLORS["text_main"])
        else:
            pygame.draw.rect(self.screen, (38, 22, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["purple"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Comparer les deux lectures du mouvement", True, COLORS["purple"])
            t2 = self.font_ui.render("Le découpage est infini, mais le mouvement physique reste continu jusqu'à la cible.", True, COLORS["text_main"])

        self.screen.blit(t1, (x + 14, y + 8))
        self.screen.blit(t2, (x + 14, y + 28))

    # =========================================================================
    # SIMULATION 2 : ACHILLE ET LA TORTUE (ENGINE.PY)
    # =========================================================================
    def _draw_tortue_single_track(self):
        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        self._draw_tortue_banner(frame_rect.x + 16, frame_rect.y + 12, frame_rect.width - 32)

        m = self.model_tortue
        max_d = m.track_distance

        y_achille = 200
        y_tortue = 265

        piste_rect = pygame.Rect(track_start_x - 20, 160, track_w + 40, 135)
        pygame.draw.rect(self.screen, COLORS["track_bg"], piste_rect, border_radius=8)

        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_achille), (track_end_x, y_achille), 3)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_tortue), (track_end_x, y_tortue), 3)

        pygame.draw.line(self.screen, COLORS["white"], (track_start_x, 165), (track_start_x, 290), 2)
        lbl_start = self.font_ui_bold.render("Départ 0m", True, COLORS["text_muted"])
        self.screen.blit(lbl_start, (track_start_x - 30, 296))

        tortue_start_x = track_start_x + int((m.pos_t_init / max_d) * track_w)
        pygame.draw.line(self.screen, (30, 80, 50), (tortue_start_x, 165), (tortue_start_x, 290), 1)
        lbl_t_start = self.font_ui.render(f"Avance ({m.pos_t_init:g}m)", True, COLORS["emerald"])
        self.screen.blit(lbl_t_start, (tortue_start_x - 25, 296))

        catch_x = track_start_x + int((m.catchup_distance / max_d) * track_w)
        pygame.draw.line(self.screen, COLORS["gold"], (catch_x, 165), (catch_x, 290), 2)
        lbl_catch = self.font_ui_bold.render(f"DÉPASSEMENT ({m.catchup_distance:.1f}m)", True, COLORS["gold"])
        self.screen.blit(lbl_catch, (catch_x - 55, 142))

        for step in m.steps[:5]:
            step_x = track_start_x + int((step.pos_achille / max_d) * track_w)
            pygame.draw.line(self.screen, COLORS["panel_border_bright"], (step_x, y_achille - 12), (step_x, y_achille + 12), 1)
            lbl_st = self.font_ui.render(f"n={step.step_num}", True, COLORS["gold"])
            self.screen.blit(lbl_st, (step_x - 10, y_achille - 28))

        if self.infinity_active:
            self._draw_achille(catch_x, y_achille, infinity_glow=True)
            self._draw_tortue_avatar(catch_x, y_tortue, infinity_glow=True)
            self._draw_tortue_infinity_overlay(track_start_x, 320)
        elif self.mode == "REAL":
            st = m.get_continuous_state(self.sim_time)
            ax = track_start_x + int(min(1.0, st["pos_achille"] / max_d) * track_w)
            tx = track_start_x + int(min(1.0, st["pos_tortue"] / max_d) * track_w)

            self._draw_achille(ax, y_achille)
            self._draw_tortue_avatar(tx, y_tortue)
            self._draw_tortue_stats_overlay(track_start_x, 320, st["pos_achille"], st["pos_tortue"],
                                           st["ecart"], st["current_time"], m.total_time)
        elif self.mode == "ZENON":
            step = m.get_step(self.step_idx)
            ax = track_start_x + int((step.pos_achille / max_d) * track_w)
            tx = track_start_x + int((step.pos_tortue / max_d) * track_w)

            self._draw_achille(ax, y_achille)
            self._draw_tortue_avatar(tx, y_tortue)
            self._draw_tortue_step_overlay(track_start_x, 320, step)

    def _draw_tortue_split_tracks(self):
        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x
        m = self.model_tortue
        max_d = m.track_distance

        y_top_a = 165
        y_top_t = 215
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_top_a), (track_end_x, y_top_a), 2)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_top_t), (track_end_x, y_top_t), 2)

        lbl_z = self.font_ui_bold.render("1. Lecture de Zénon : Achille n'arrive qu'à l'ancienne position de la tortue", True, COLORS["gold"])
        self.screen.blit(lbl_z, (track_start_x, 135))

        st = m.get_continuous_state(self.sim_time)
        zenon_step = m.get_step(st["current_step_index"])
        z_ax = track_start_x + int((zenon_step.pos_achille / max_d) * track_w)
        z_tx = track_start_x + int((zenon_step.pos_tortue / max_d) * track_w)
        self._draw_achille(z_ax, y_top_a)
        self._draw_tortue_avatar(z_tx, y_top_t)

        y_bot_a = 310
        y_bot_t = 360
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_bot_a), (track_end_x, y_bot_a), 2)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_bot_t), (track_end_x, y_bot_t), 2)

        lbl_r = self.font_ui_bold.render("2. Réalité continue : Les deux avancent sans arrêt et Achille double à t = T", True, COLORS["cyan"])
        self.screen.blit(lbl_r, (track_start_x, 280))

        r_ax = track_start_x + int(min(1.0, st["pos_achille"] / max_d) * track_w)
        r_tx = track_start_x + int(min(1.0, st["pos_tortue"] / max_d) * track_w)
        self._draw_achille(r_ax, y_bot_a)
        self._draw_tortue_avatar(r_tx, y_bot_t)

        info_t = f"Temps : {st['current_time']:.2f}s / {m.total_time:.2f}s  |  Achille : {st['pos_achille']:.2f}m  |  Tortue : {st['pos_tortue']:.2f}m  |  Écart : {st['ecart']:.3f}m"
        info_surf = self.font_ui_bold.render(info_t, True, COLORS["text_main"])
        self.screen.blit(info_surf, (track_start_x, 430))

    def _draw_tortue_banner(self, x: int, y: int, width: int):
        banner_rect = pygame.Rect(x, y, width, 55)
        m = self.model_tortue

        if self.infinity_active:
            pygame.draw.rect(self.screen, (50, 18, 70), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["infinity_color"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Convergence exacte · n → ∞ (engine.py)", True, COLORS["infinity_color"])
            t2 = self.font_ui.render(f"Achille rejoint la tortue exactement à {m.catchup_distance:.2f} m au bout de {m.total_time:.2f} s.", True, COLORS["text_main"])
        elif self.mode == "ZENON":
            pygame.draw.rect(self.screen, (45, 34, 15), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["gold"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Le paradoxe d'Achille · Le piège de la position précédente", True, COLORS["gold"])
            t2 = self.font_ui.render("Quand Achille arrive là où la tortue était, celle-ci s'est encore déplacée. L'écart décroît mais ne semble jamais nul.", True, COLORS["text_main"])
        elif self.mode == "REAL":
            pygame.draw.rect(self.screen, (15, 50, 45), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["emerald"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Résolution physique · Dépassement à vitesse constante", True, COLORS["emerald"])
            t2 = self.font_ui.render(f"Temps fini T = d / (v_A - v_T) = {m.total_time:.2f} s. Achille dépasse la tortue sans s'arrêter !", True, COLORS["text_main"])
        else:
            pygame.draw.rect(self.screen, (38, 22, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["purple"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Comparer les deux points de vue", True, COLORS["purple"])
            t2 = self.font_ui.render("Zénon découpe le temps en intervalles infinitésimaux, alors que la réalité s'écoule de façon continue.", True, COLORS["text_main"])

        self.screen.blit(t1, (x + 14, y + 8))
        self.screen.blit(t2, (x + 14, y + 28))

    # =========================================================================
    # SIMULATION 3 : LA FLÈCHE EN VOL (MENU_FLECHE.PY)
    # =========================================================================
    def _draw_fleche_single_track(self):
        track_y = 225
        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        self._draw_fleche_vol_banner(frame_rect.x + 16, frame_rect.y + 12, frame_rect.width - 32)

        piste_rect = pygame.Rect(track_start_x - 30, track_y - 45, track_w + 60, 90)
        pygame.draw.rect(self.screen, COLORS["track_bg"], piste_rect, border_radius=8)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, track_y), (track_end_x, track_y), 4)

        # Tireur / Arc au départ
        pygame.draw.circle(self.screen, COLORS["cyan"], (track_start_x, track_y), 7)
        pygame.draw.arc(self.screen, COLORS["gold"], (track_start_x - 12, track_y - 18, 24, 36), -math.pi/2, math.pi/2, 2)
        lbl_arc = self.font_ui_bold.render("Tireur (0 m)", True, COLORS["text_muted"])
        self.screen.blit(lbl_arc, (track_start_x - 35, track_y + 18))

        # Cible
        self._draw_target(track_end_x, track_y, self.model_fleche.distance)

        # Graduations des instants discrets (menu_fleche.py)
        for step in self.model_fleche.steps:
            ratio = step.position / self.model_fleche.distance
            ix = track_start_x + int(ratio * track_w)
            pygame.draw.line(self.screen, (40, 65, 95), (ix, track_y - 14), (ix, track_y + 14), 1)
            lbl_i = self.font_ui.render(f"i={step.step_num}", True, (130, 160, 200))
            self.screen.blit(lbl_i, (ix - 10, track_y - 28))

        if self.infinity_active:
            self._draw_javelin(track_end_x, track_y, infinity_glow=True)
            self._draw_fleche_vol_infinity_overlay(track_start_x, track_y + 60)
        elif self.mode == "REAL":
            st = self.model_fleche.get_continuous_state(self.sim_time)
            fx = track_start_x + int(st["progress"] * track_w)
            self._draw_javelin(fx, track_y)
            self._draw_fleche_vol_stats_overlay(track_start_x, track_y + 70, st["position"], st["remaining"],
                                               st["current_time"], self.model_fleche.total_time, self.model_fleche.vitesse_reelle)
        elif self.mode == "ZENON":
            step = self.model_fleche.get_step(self.step_idx)
            ratio = step.position / self.model_fleche.distance
            fx = track_start_x + int(ratio * track_w)
            # Effet stroboscopique : cadre d'instant figé
            pygame.draw.rect(self.screen, (70, 50, 20), (fx - 45, track_y - 20, 60, 40), width=1, border_radius=6)
            self._draw_javelin(fx, track_y)
            self._draw_fleche_vol_step_overlay(track_start_x, track_y + 60, step)

    def _draw_fleche_split_tracks(self):
        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        # 1. Haut : Instants figés
        y_top = 175
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_top), (track_end_x, y_top), 3)
        self._draw_target(track_end_x, y_top, self.model_fleche.distance)
        lbl_z = self.font_ui_bold.render("1. Zénon : À chaque instant individuel, la flèche est figée dans l'espace", True, COLORS["gold"])
        self.screen.blit(lbl_z, (track_start_x, y_top - 45))

        st = self.model_fleche.get_continuous_state(self.sim_time)
        zenon_step = self.model_fleche.get_step(st["current_step_index"])
        zx = track_start_x + int((zenon_step.position / self.model_fleche.distance) * track_w)
        pygame.draw.rect(self.screen, (70, 50, 20), (zx - 45, y_top - 18, 60, 36), width=1, border_radius=5)
        self._draw_javelin(zx, y_top)

        # 2. Bas : Vol continu réel
        y_bot = 345
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_bot), (track_end_x, y_bot), 3)
        self._draw_target(track_end_x, y_bot, self.model_fleche.distance)
        lbl_r = self.font_ui_bold.render("2. Réalité : Le mouvement existe car la vitesse v = dx/dt est non nulle !", True, COLORS["cyan"])
        self.screen.blit(lbl_r, (track_start_x, y_bot - 45))

        rx = track_start_x + int(st["progress"] * track_w)
        self._draw_javelin(rx, y_bot)

        info_t = f"Temps : {st['current_time']:.2f}s / {self.model_fleche.total_time:.2f}s  |  Position : {st['position']:.2f}m / {self.model_fleche.distance:.2f}m  |  Vitesse v = {self.model_fleche.vitesse_reelle:.1f} m/s"
        info_surf = self.font_ui_bold.render(info_t, True, COLORS["text_main"])
        self.screen.blit(info_surf, (track_start_x, 430))

    def _draw_fleche_vol_banner(self, x: int, y: int, width: int):
        banner_rect = pygame.Rect(x, y, width, 55)
        m = self.model_fleche

        if self.infinity_active:
            pygame.draw.rect(self.screen, (50, 18, 70), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["infinity_color"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Continu infinitésimal · dt → 0 (menu_fleche.py)", True, COLORS["infinity_color"])
            t2 = self.font_ui.render(f"La somme infinie d'instants sans durée forme le continuum temporel du vol jusqu'à {m.distance:g} m.", True, COLORS["text_main"])
        elif self.mode == "ZENON":
            pygame.draw.rect(self.screen, (45, 34, 15), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["gold"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Le paradoxe de la flèche · L'immobilité de chaque instant", True, COLORS["gold"])
            t2 = self.font_ui.render("À un instant indivisible, la flèche n'a pas le temps de bouger : elle est donc au repos à chaque instant !", True, COLORS["text_main"])
        elif self.mode == "REAL":
            pygame.draw.rect(self.screen, (15, 45, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["cyan"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("La résolution par le calcul différentiel", True, COLORS["cyan"])
            t2 = self.font_ui.render(f"La vitesse est la dérivée de la position v(t) = dx/dt = {m.vitesse_reelle:g} m/s. Le repos n'est pas le mouvement.", True, COLORS["text_main"])
        else:
            pygame.draw.rect(self.screen, (38, 22, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["purple"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("Comparer les instants figés et la trajectoire réelle", True, COLORS["purple"])
            t2 = self.font_ui.render("Zénon confond un instant (durée nulle) et un intervalle (où la vitesse opère).", True, COLORS["text_main"])

        self.screen.blit(t1, (x + 14, y + 8))
        self.screen.blit(t2, (x + 14, y + 28))

    def _draw_fleche_vol_stats_overlay(self, x: int, y: int, pos: float, rem: float, cur_t: float, total_t: float, vit: float):
        w = self.width - 180
        prog = min(1.0, cur_t / total_t) if total_t > 0 else 1.0

        h = 10
        pygame.draw.rect(self.screen, (30, 44, 70), (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, COLORS["gold"], (x, y, int(w * prog), h), border_radius=5)

        stats = [
            ("Position Flèche", f"{pos:.2f} m", COLORS["cyan"]),
            ("Distance Restante", f"{rem:.2f} m", COLORS["gold"]),
            ("Vitesse Réelle (dx/dt)", f"{vit:.1f} m/s", COLORS["emerald"]),
            ("Temps Écoulé", f"{cur_t:.2f} s / {total_t:.2f}s", COLORS["purple"])
        ]

        card_w = (w - 45) // 4
        for i, (label, val, col) in enumerate(stats):
            cx = x + i * (card_w + 15)
            cy = y + 22
            card_rect = pygame.Rect(cx, cy, card_w, 48)
            pygame.draw.rect(self.screen, COLORS["panel_card"], card_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["panel_border"], card_rect, width=1, border_radius=6)

            lbl_surf = self.font_ui.render(label, True, COLORS["text_muted"])
            val_surf = self.font_big_val.render(val, True, col)
            self.screen.blit(lbl_surf, (cx + 10, cy + 6))
            self.screen.blit(val_surf, (cx + 10, cy + 24))

    def _draw_fleche_vol_step_overlay(self, x: int, y: int, step):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (38, 28, 14), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["gold"], panel_rect, width=1, border_radius=8)

        t_step = self.font_title.render(f"Instant i = {step.step_num} / {self.model_fleche.nombre_de_pas} (menu_fleche.py)", True, COLORS["gold"])
        t_expl = self.font_ui.render(f"Position : {step.position:.2f} m  |  Temps t = {step.instant_time:.2f} s  |  Statut Zénon : Immobile à cet instant !", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("Zénon : 'Si à tout instant elle n'avance pas, comment avance-t-elle ?'", True, COLORS["gold"])

        self.screen.blit(t_step, (x + 15, y + 14))
        self.screen.blit(t_expl, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_fleche_vol_infinity_overlay(self, x: int, y: int):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (40, 16, 60), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["infinity_color"], panel_rect, width=1, border_radius=8)

        t_inf = self.font_infinity.render("CONTINUUM ATTEINT · dt → 0", True, COLORS["infinity_color"])
        t_desc = self.font_ui.render(f"La flèche touche la cible à {self.model_fleche.distance:g} m en {self.model_fleche.total_time:g} s.", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("Le continu n'est pas une simple suite d'instants isolés : la dérivée est réelle.", True, COLORS["gold"])

        self.screen.blit(t_inf, (x + 15, y + 14))
        self.screen.blit(t_desc, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    # =========================================================================
    # AVATARS & DESSINS COMMUNS
    # =========================================================================
    def _draw_achille(self, x: int, y: int, infinity_glow: bool = False):
        trail_col = COLORS["infinity_color"] if infinity_glow else COLORS["cyan"]
        body_col = COLORS["infinity_color"] if infinity_glow else COLORS["cyan"]
        helm_col = COLORS["infinity_color"] if infinity_glow else COLORS["gold"]

        pygame.draw.line(self.screen, trail_col, (x - 26, y), (x - 12, y), 2)
        pygame.draw.line(self.screen, trail_col, (x - 20, y - 4), (x - 10, y - 4), 1)
        pygame.draw.line(self.screen, trail_col, (x - 20, y + 4), (x - 10, y + 4), 1)

        pygame.draw.polygon(self.screen, body_col, [
            (x + 10, y),
            (x - 6, y - 9),
            (x - 10, y),
            (x - 6, y + 9)
        ])

        pygame.draw.circle(self.screen, helm_col, (x + 3, y - 6), 5)
        pygame.draw.line(self.screen, COLORS["ruby"], (x, y - 11), (x + 8, y - 6), 2)

        if infinity_glow:
            glow_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (230, 120, 255, 130), (18, 18), 16)
            self.screen.blit(glow_surf, (x - 18, y - 18))

        lbl = self.font_ui_bold.render("Achille", True, COLORS["cyan"])
        self.screen.blit(lbl, (x - 16, y - 24))

    def _draw_tortue_avatar(self, x: int, y: int, infinity_glow: bool = False):
        shell_col = COLORS["infinity_color"] if infinity_glow else COLORS["emerald"]
        patte_col = (20, 70, 45) if not infinity_glow else (90, 40, 100)

        pygame.draw.circle(self.screen, patte_col, (x - 7, y - 8), 3)
        pygame.draw.circle(self.screen, patte_col, (x + 7, y - 8), 3)
        pygame.draw.circle(self.screen, patte_col, (x - 7, y + 8), 3)
        pygame.draw.circle(self.screen, patte_col, (x + 7, y + 8), 3)

        head_x = x + 13
        pygame.draw.circle(self.screen, shell_col, (head_x, y), 4)

        shell_rect = pygame.Rect(x - 11, y - 8, 22, 16)
        pygame.draw.ellipse(self.screen, shell_col, shell_rect)
        pygame.draw.ellipse(self.screen, COLORS["panel_border_bright"], shell_rect, width=1)

        pygame.draw.line(self.screen, (10, 45, 30), (x - 3, y - 8), (x - 3, y + 8), 1)
        pygame.draw.line(self.screen, (10, 45, 30), (x + 3, y - 8), (x + 3, y + 8), 1)

        if infinity_glow:
            glow_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (230, 120, 255, 110), (18, 18), 15)
            self.screen.blit(glow_surf, (x - 18, y - 18))

        lbl = self.font_ui_bold.render("Tortue", True, COLORS["emerald"])
        self.screen.blit(lbl, (x - 16, y + 12))

    def _draw_javelin(self, x: int, y: int, infinity_glow: bool = False):
        length = 52
        trail_col = COLORS["infinity_color"] if infinity_glow else COLORS["cyan"]
        tip_col = COLORS["infinity_color"] if infinity_glow else COLORS["gold"]

        pygame.draw.line(self.screen, (trail_col[0], trail_col[1], trail_col[2]), (x - length - 20, y), (x - length, y), 2)
        pygame.draw.line(self.screen, COLORS["white"], (x - length, y), (x, y), 3)
        pygame.draw.line(self.screen, trail_col, (x - length, y - 7), (x - length + 12, y), 2)
        pygame.draw.line(self.screen, trail_col, (x - length, y + 7), (x - length + 12, y), 2)
        pygame.draw.polygon(self.screen, tip_col, [(x, y), (x - 14, y - 6), (x - 14, y + 6)])

        glow_radius = 16 if infinity_glow else 10
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (tip_col[0], tip_col[1], tip_col[2], 140), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

    def _draw_target(self, x: int, y: int, dist: float):
        r = 30
        pygame.draw.circle(self.screen, COLORS["white"], (x, y), r)
        pygame.draw.circle(self.screen, COLORS["cyan"], (x, y), int(r * 0.75))
        pygame.draw.circle(self.screen, COLORS["ruby"], (x, y), int(r * 0.5))
        pygame.draw.circle(self.screen, COLORS["gold"], (x, y), int(r * 0.25))

        pygame.draw.rect(self.screen, COLORS["panel_border_bright"], (x - 3, y + r, 6, 25))
        lbl = self.font_ui_bold.render(f"CIBLE ({dist:g} m)", True, COLORS["ruby"])
        self.screen.blit(lbl, (x - 38, y + r + 28))

    def _draw_live_stats_overlay(self, x: int, y: int, cur_d: float, cur_t: float, rem_d: float, progress: float):
        w = self.width - 180
        h = 10
        pygame.draw.rect(self.screen, (30, 44, 70), (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, COLORS["cyan"], (x, y, int(w * progress), h), border_radius=5)

        stats = [
            ("Distance Parcourue", f"{cur_d:.2f} m", COLORS["cyan"]),
            ("Temps Écoulé", f"{cur_t:.2f} s", COLORS["emerald"]),
            ("Distance Restante", f"{rem_d:.3f} m", COLORS["gold"]),
            ("Progression", f"{progress * 100:.1f} %", COLORS["text_main"])
        ]

        card_w = (w - 45) // 4
        for i, (label, val, col) in enumerate(stats):
            cx = x + i * (card_w + 15)
            cy = y + 22
            card_rect = pygame.Rect(cx, cy, card_w, 48)
            pygame.draw.rect(self.screen, COLORS["panel_card"], card_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["panel_border"], card_rect, width=1, border_radius=6)

            lbl_surf = self.font_ui.render(label, True, COLORS["text_muted"])
            val_surf = self.font_big_val.render(val, True, col)
            self.screen.blit(lbl_surf, (cx + 10, cy + 6))
            self.screen.blit(val_surf, (cx + 10, cy + 24))

    def _draw_tortue_stats_overlay(self, x: int, y: int, pos_a: float, pos_t: float, ecart: float, cur_t: float, total_t: float):
        w = self.width - 180
        prog = min(1.0, cur_t / total_t) if total_t > 0 else 1.0

        h = 10
        pygame.draw.rect(self.screen, (30, 44, 70), (x, y, w, h), border_radius=5)
        bar_col = COLORS["gold"] if prog >= 1.0 else COLORS["emerald"]
        pygame.draw.rect(self.screen, bar_col, (x, y, int(w * prog), h), border_radius=5)

        stats = [
            ("Position Achille", f"{pos_a:.2f} m", COLORS["cyan"]),
            ("Position Tortue", f"{pos_t:.2f} m", COLORS["emerald"]),
            ("Écart Résiduel", f"{ecart:.3f} m", COLORS["gold"]),
            ("Temps de Course", f"{cur_t:.2f} s / {total_t:.2f}s", COLORS["purple"])
        ]

        card_w = (w - 45) // 4
        for i, (label, val, col) in enumerate(stats):
            cx = x + i * (card_w + 15)
            cy = y + 22
            card_rect = pygame.Rect(cx, cy, card_w, 48)
            pygame.draw.rect(self.screen, COLORS["panel_card"], card_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLORS["panel_border"], card_rect, width=1, border_radius=6)

            lbl_surf = self.font_ui.render(label, True, COLORS["text_muted"])
            val_surf = self.font_big_val.render(val, True, col)
            self.screen.blit(lbl_surf, (cx + 10, cy + 6))
            self.screen.blit(val_surf, (cx + 10, cy + 24))

    def _draw_infinity_overlay(self, x: int, y: int, total_d: float, total_t: float):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (40, 16, 60), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["infinity_color"], panel_rect, width=1, border_radius=8)

        t_inf = self.font_infinity.render("LIMITE ATTEINTE · n → ∞", True, COLORS["infinity_color"])
        t_desc = self.font_ui.render(f"Distance = {total_d:g} m  |  Temps = {total_t:g} s  |  Distance restante = 0.000 m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("Une infinité d'étapes infinitésimales tient dans un temps fini.", True, COLORS["gold"])

        self.screen.blit(t_inf, (x + 15, y + 14))
        self.screen.blit(t_desc, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_tortue_infinity_overlay(self, x: int, y: int):
        w = self.width - 180
        m = self.model_tortue
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (40, 16, 60), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["infinity_color"], panel_rect, width=1, border_radius=8)

        t_inf = self.font_infinity.render("LIMITE ATTEINTE · n → ∞ (Dépassement exact)", True, COLORS["infinity_color"])
        t_desc = self.font_ui.render(f"Point de rencontre D = {m.catchup_distance:.2f} m  |  Temps de rattrapage T = {m.total_time:.2f} s  |  Écart = 0.000 m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("La série d'intervalles temporels converge : Achille double effectivement la tortue !", True, COLORS["gold"])

        self.screen.blit(t_inf, (x + 15, y + 14))
        self.screen.blit(t_desc, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_zenon_step_overlay(self, x: int, y: int, step):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (38, 28, 14), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["gold"], panel_rect, width=1, border_radius=8)

        t_step = self.font_title.render(f"Étape {step.step_num} · part {step.fraction_str}", True, COLORS["gold"])
        t_expl = self.font_ui.render(f"Distance étape : {step.delta_distance:g} m  |  Cumul : {step.cumul_distance:g} m  |  Reste à franchir : {step.remaining_distance:g} m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("Il reste toujours une nouvelle moitié à parcourir…", True, COLORS["gold"])

        self.screen.blit(t_step, (x + 15, y + 14))
        self.screen.blit(t_expl, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_tortue_step_overlay(self, x: int, y: int, step):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (38, 28, 14), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["gold"], panel_rect, width=1, border_radius=8)

        t_step = self.font_title.render(f"Itération {step.step_num} (engine.py)", True, COLORS["gold"])
        t_expl = self.font_ui.render(f"Achille atteint {step.pos_achille:.2f} m  |  La Tortue est déjà à {step.pos_tortue:.2f} m  |  Nouvel écart : {step.ecart:.3f} m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render(f"Durée de l'étape : Δt = {step.delta_time:.3f} s (Temps cumulé = {step.cumul_time:.3f} s)", True, COLORS["emerald"])

        self.screen.blit(t_step, (x + 15, y + 14))
        self.screen.blit(t_expl, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    # =========================================================================
    # PANNEAU INFÉRIEUR (CONTRÔLES, DONNÉES, GRAPHIQUES)
    # =========================================================================
    def _draw_bottom_panel(self):
        panel_y = self.height - 275
        ctrl_w = 260

        ctrl_rect = pygame.Rect(24, panel_y, ctrl_w, 260)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], ctrl_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["panel_border"], ctrl_rect, width=1, border_radius=10)

        if self.current_sim == "DICHOTOMIE":
            title_txt = "Paramètres · Dichotomie"
        elif self.current_sim == "TORTUE":
            title_txt = "Paramètres · Tortue"
        else:
            title_txt = "Paramètres · La Flèche"
        title_ctrl = self.font_ui_bold.render(title_txt, True, COLORS["text_main"])
        self.screen.blit(title_ctrl, (34, panel_y + 10))

        if self.current_sim == "DICHOTOMIE":
            self.slider_distance.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.slider_speed.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.btn_p8.draw(self.screen, self.font_ui)
            self.btn_p16.draw(self.screen, self.font_ui)
            self.btn_p50.draw(self.screen, self.font_ui)
            self.btn_p100.draw(self.screen, self.font_ui)
        elif self.current_sim == "TORTUE":
            self.slider_pos_t.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.slider_v_a.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.slider_v_t.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.btn_t10.draw(self.screen, self.font_ui)
            self.btn_t20.draw(self.screen, self.font_ui)
            self.btn_t5.draw(self.screen, self.font_ui)
            self.btn_t15.draw(self.screen, self.font_ui)
        else:
            self.slider_fl_dist.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.slider_fl_duree.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.slider_fl_pas.draw(self.screen, self.font_ui, self.font_ui_bold)
            self.btn_fl_p20.draw(self.screen, self.font_ui)
            self.btn_fl_p50.draw(self.screen, self.font_ui)
            self.btn_fl_p100.draw(self.screen, self.font_ui)
            self.btn_fl_p200.draw(self.screen, self.font_ui)

        self.btn_play.draw(self.screen, self.font_ui_bold)
        self.btn_step.draw(self.screen, self.font_ui_bold)
        self.btn_infinity.draw(self.screen, self.font_ui_bold)
        self.btn_reset.draw(self.screen, self.font_ui)

        # Tableau de données
        m = self.active_model
        if self.current_sim == "TORTUE":
            tot_d = self.model_tortue.catchup_distance
        elif self.current_sim == "FLECHE":
            tot_d = self.model_fleche.distance
        else:
            tot_d = self.model_dichotomie.total_distance
        tot_t = m.total_time
        self.data_table.draw(self.screen, self.font_ui_bold, self.font_ui, tot_d, tot_t)

        # Panneau Droit (Graphique ou Loupe)
        self.btn_tab_graph.draw(self.screen, self.font_ui_bold)
        self.btn_tab_loupe.draw(self.screen, self.font_ui_bold)

        st = m.get_continuous_state(self.sim_time)
        if self.right_tab == "GRAPH":
            if self.current_sim == "DICHOTOMIE":
                self.mini_graph.draw(self.screen, self.model_dichotomie.total_distance, self.model_dichotomie.total_time,
                                     st["current_time"], st["current_distance"], self.model_dichotomie.steps,
                                     self.font_ui, self.font_ui_bold)
            elif self.current_sim == "TORTUE":
                self.mini_graph.draw_tortue(self.screen, self.model_tortue.pos_a_init, self.model_tortue.pos_t_init,
                                            self.model_tortue.vitesse_a, self.model_tortue.vitesse_t,
                                            self.model_tortue.catchup_distance, self.model_tortue.total_time,
                                            st["current_time"], st["pos_achille"], st["pos_tortue"],
                                            self.font_ui, self.font_ui_bold)
            else:
                self.mini_graph.draw_fleche_vol(self.screen, self.model_fleche.distance, self.model_fleche.total_time,
                                                st["current_time"], st["position"], self.model_fleche.steps,
                                                self.font_ui, self.font_ui_bold)
        else:
            if self.current_sim == "DICHOTOMIE":
                self.zoom_loupe.draw(self.screen, self.model_dichotomie.total_distance, st["current_distance"],
                                     self.model_dichotomie.steps, self.font_ui_bold, self.font_ui)
            elif self.current_sim == "TORTUE":
                self.zoom_loupe.draw_tortue(self.screen, self.model_tortue.catchup_distance,
                                            st["pos_achille"], st["pos_tortue"],
                                            self.font_ui_bold, self.font_ui)
            else:
                self.zoom_loupe.draw_fleche_vol(self.screen, self.model_fleche.distance, st["position"],
                                                self.model_fleche.vitesse_reelle,
                                                self.font_ui_bold, self.font_ui)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = ZenoApp()
    app.run()
