"""
Application interactive Pygame : Les Paradoxes de Zénon (La Dichotomie & Le Javelot).
Version 2.0 UX Haute Clarté : Design net, boutons alignés à droite, mode Infini (∞), tableau enrichi et visualisations contrastées.
"""
import pygame
import sys
import math
import numpy as np
from typing import Optional

from zeno_sim import ZenoModel
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
        pygame.display.set_caption("Les Paradoxes de Zénon : La Dichotomie & Le Javelot (v2.0)")
        self.clock = pygame.time.Clock()
        self.running = True

        # Polices nettes
        self.font_title = get_font(23, bold=True)
        self.font_subtitle = get_font(13, bold=False)
        self.font_ui = get_font(13, bold=False)
        self.font_ui_bold = get_font(13, bold=True)
        self.font_big_val = get_font(18, bold=True)
        self.font_infinity = get_font(26, bold=True)

        # Moteur mathématique
        self.distance = 8.0
        self.speed = 1.0
        self.model = ZenoModel(total_distance=self.distance, speed=self.speed)

        # État de la simulation
        # Modes: "ZENON", "REAL", "SPLIT"
        self.mode = "REAL"
        self.is_playing = False
        self.sim_time = 0.0
        self.step_idx = 0
        self.sim_speed_mult = 1.0
        self.impact_triggered = False
        self.infinity_active = False

        # Effets visuels & Sons
        self.particles = ParticleSystem()
        self.sound = SoundSynth()
        self.right_tab = "GRAPH" # "GRAPH" ou "LOUPE"

        # Initialisation et disposition UI
        self._init_ui()
        self._reposition_layout()

    def _init_ui(self):
        # 1. Barre de modes en haut (placés tout à droite)
        self.btn_mode_zenon = Button(0, 0, 205, 36, "🏛️ Paradoxe de Zénon", 
                                     callback=lambda: self.set_mode("ZENON"), color=COLORS["gold"])
        self.btn_mode_real = Button(0, 0, 220, 36, "📐 Résolution Math.", 
                                    callback=lambda: self.set_mode("REAL"), color=COLORS["cyan"], active=True)
        self.btn_mode_split = Button(0, 0, 155, 36, "⚖️ Double Vue", 
                                     callback=lambda: self.set_mode("SPLIT"), color=COLORS["purple"])

        # 2. Contrôles en bas à gauche
        self.slider_distance = Slider(24, 0, 246, 24, min_val=2.0, max_val=100.0, 
                                      initial_val=self.distance, label="Distance Totale", unit="m", step=1.0,
                                      on_change=self._on_distance_changed)
        
        self.slider_speed = Slider(24, 0, 246, 24, min_val=0.5, max_val=10.0, 
                                   initial_val=self.speed, label="Vitesse du Javelot", unit="m/s", step=0.5,
                                   on_change=self._on_speed_changed)

        # Boutons presets de distance
        self.btn_p8 = Button(0, 0, 56, 24, "8 m", callback=lambda: self.set_preset_distance(8.0), color=COLORS["panel_card"])
        self.btn_p16 = Button(0, 0, 56, 24, "16 m", callback=lambda: self.set_preset_distance(16.0), color=COLORS["panel_card"])
        self.btn_p50 = Button(0, 0, 56, 24, "50 m", callback=lambda: self.set_preset_distance(50.0), color=COLORS["panel_card"])
        self.btn_p100 = Button(0, 0, 62, 24, "100 m", callback=lambda: self.set_preset_distance(100.0), color=COLORS["panel_card"])

        # Boutons d'action principaux
        self.btn_play = Button(0, 0, 120, 34, "▶ Lancer", callback=self.toggle_play, color=COLORS["emerald"])
        self.btn_step = Button(0, 0, 120, 34, "⏭ Pas Suivant", callback=self.next_step, color=COLORS["gold"])
        
        # Bouton Infini (∞) spécial & bouton reset
        self.btn_infinity = Button(0, 0, 246, 32, "♾️ Saut Limite Infini (n → ∞)", callback=self.trigger_infinity, color=COLORS["infinity_color"])
        self.btn_reset = Button(0, 0, 246, 28, "🔄 Réinitialiser", callback=self.reset_sim, color=COLORS["panel_card"])

        # 3. Tableau de données au milieu
        self.data_table = DataTable(0, 0, 540, 230)
        self.data_table.set_data(self.model.steps, active_step=-1)

        # 4. Panneau droit : Graphique & Loupe
        self.mini_graph = MiniGraph(0, 0, 460, 195)
        self.zoom_loupe = ZoomLoupe(0, 0, 460, 195)

        self.btn_tab_graph = Button(0, 0, 225, 28, "📈 Graphique Limite", 
                                    callback=lambda: self.set_right_tab("GRAPH"), color=COLORS["cyan"], active=True)
        self.btn_tab_loupe = Button(0, 0, 225, 28, "🔬 Loupe Zoom x50", 
                                    callback=lambda: self.set_right_tab("LOUPE"), color=COLORS["gold"])

    def _reposition_layout(self):
        """Repositionne dynamiquement tous les éléments en fonction de la taille de l'écran."""
        # 1. Header (Mode Buttons alignés tout à droite)
        right_margin = 24
        btn_y = 16
        w_split = 155
        w_real = 215
        w_zenon = 200
        spacing = 10

        x_split = self.width - right_margin - w_split
        x_real = x_split - spacing - w_real
        x_zenon = x_real - spacing - w_zenon

        self.btn_mode_zenon.set_position(x_zenon, btn_y, w_zenon, 36)
        self.btn_mode_real.set_position(x_real, btn_y, w_real, 36)
        self.btn_mode_split.set_position(x_split, btn_y, w_split, 36)

        # 2. Zone inférieure (Deck de contrôle et statistiques)
        panel_y = self.height - 275
        ctrl_w = 260
        gap = 16

        # Colonne Gauche (Contrôles)
        self.slider_distance.set_position(24, panel_y + 42, ctrl_w)
        self.slider_speed.set_position(24, panel_y + 92, ctrl_w)

        # Boutons presets
        p_w = (ctrl_w - 18) // 4
        self.btn_p8.set_position(24, panel_y + 122, p_w, 24)
        self.btn_p16.set_position(24 + p_w + 6, panel_y + 122, p_w, 24)
        self.btn_p50.set_position(24 + (p_w + 6) * 2, panel_y + 122, p_w, 24)
        self.btn_p100.set_position(24 + (p_w + 6) * 3, panel_y + 122, p_w, 24)

        # Boutons Actions
        act_w = (ctrl_w - 8) // 2
        self.btn_play.set_position(24, panel_y + 154, act_w, 34)
        self.btn_step.set_position(24 + act_w + 8, panel_y + 154, act_w, 34)
        self.btn_infinity.set_position(24, panel_y + 194, ctrl_w, 32)
        self.btn_reset.set_position(24, panel_y + 231, ctrl_w, 26)

        # Colonne Centrale (Tableau de données)
        middle_x = 24 + ctrl_w + gap
        remaining_w = self.width - middle_x - 24
        table_w = int(remaining_w * 0.54)
        right_w = remaining_w - table_w - gap

        self.data_table.set_position(middle_x, panel_y, table_w, 260)

        # Colonne Droite (Graphique / Loupe)
        right_x = middle_x + table_w + gap
        tab_w = (right_w - 10) // 2
        self.btn_tab_graph.set_position(right_x, panel_y, tab_w, 28)
        self.btn_tab_loupe.set_position(right_x + tab_w + 10, panel_y, tab_w, 28)
        
        self.mini_graph.set_position(right_x, panel_y + 35, right_w, 225)
        self.zoom_loupe.set_position(right_x, panel_y + 35, right_w, 225)

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
        self.reset_sim()

    def set_preset_distance(self, dist: float):
        self.distance = dist
        self.slider_distance.set_value(dist)
        self._on_distance_changed(dist)
        self.sound.play_click()

    def _on_distance_changed(self, new_d: float):
        self.distance = new_d
        self.model.update_parameters(self.distance, self.speed)
        self.data_table.set_data(self.model.steps, self.step_idx, self.infinity_active)
        self.reset_sim()

    def _on_speed_changed(self, new_v: float):
        self.speed = new_v
        self.model.update_parameters(self.distance, self.speed)
        self.data_table.set_data(self.model.steps, self.step_idx, self.infinity_active)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.text = "⏸ Pause" if self.is_playing else "▶ Reprendre"
        self.btn_play.base_color = COLORS["gold"] if self.is_playing else COLORS["emerald"]
        self.sound.play_click()

    def next_step(self):
        if self.step_idx < len(self.model.steps) - 1:
            self.step_idx += 1
            step = self.model.get_step(self.step_idx)
            self.sim_time = step.cumul_time
            self.data_table.active_step_idx = self.step_idx
            self.sound.play_step()
            
            if self.step_idx >= 12 and not self.impact_triggered:
                self.impact_triggered = True
                self.sound.play_impact()
                target_x = self.width - 100
                target_y = 230
                self.particles.emit_impact(target_x, target_y, count=45)

    def trigger_infinity(self):
        """Active le saut limite à l'infini (n → ∞)."""
        self.infinity_active = True
        self.is_playing = False
        self.sim_time = self.model.total_time
        self.step_idx = 20
        self.data_table.set_data(self.model.steps, self.step_idx, show_infinity=True)
        self.sound.play_infinity()
        
        # Émission d'un burst cosmique de particules
        target_x = self.width - 100
        target_y = 230 if self.mode != "SPLIT" else 350
        self.particles.emit_impact(target_x, target_y, count=80, theme="infinity")

    def reset_sim(self):
        self.is_playing = False
        self.sim_time = 0.0
        self.step_idx = 0
        self.impact_triggered = False
        self.infinity_active = False
        self.btn_play.text = "▶ Lancer"
        self.btn_play.base_color = COLORS["emerald"]
        self.data_table.set_data(self.model.steps, active_step=-1, show_infinity=False)
        self.particles.particles.clear()
        self.sound.play_click()

    def update(self, dt: float):
        for btn in [self.btn_mode_zenon, self.btn_mode_real, self.btn_mode_split, 
                    self.btn_p8, self.btn_p16, self.btn_p50, self.btn_p100, 
                    self.btn_play, self.btn_step, self.btn_infinity, self.btn_reset,
                    self.btn_tab_graph, self.btn_tab_loupe]:
            btn.update(dt)

        self.particles.update(dt)

        if self.is_playing:
            eff_dt = dt * self.sim_speed_mult
            
            if self.mode == "REAL":
                self.sim_time += eff_dt
                if self.sim_time >= self.model.total_time:
                    self.sim_time = self.model.total_time
                    self.is_playing = False
                    self.btn_play.text = "▶ Recommencer"
                    self.btn_play.base_color = COLORS["emerald"]
                    if not self.impact_triggered:
                        self.impact_triggered = True
                        self.sound.play_impact()
                        target_x = self.width - 100
                        target_y = 230
                        self.particles.emit_impact(target_x, target_y, count=60)
            
            elif self.mode == "ZENON":
                step_duration = 0.75
                self.sim_time += eff_dt
                target_step_time = (self.step_idx + 1) * step_duration
                
                if self.sim_time >= target_step_time:
                    if self.step_idx < len(self.model.steps) - 1:
                        self.step_idx += 1
                        self.sound.play_step()
                    else:
                        self.is_playing = False
                        self.btn_play.text = "▶ Recommencer"
            
            elif self.mode == "SPLIT":
                self.sim_time += eff_dt
                if self.sim_time >= self.model.total_time:
                    self.sim_time = self.model.total_time
                    self.is_playing = False
                    self.btn_play.text = "▶ Recommencer"
                    if not self.impact_triggered:
                        self.impact_triggered = True
                        self.sound.play_impact()
                        self.particles.emit_impact(self.width - 100, 350, count=55)

            st = self.model.get_continuous_state(self.sim_time)
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

            # UI Events
            self.btn_mode_zenon.handle_event(event)
            self.btn_mode_real.handle_event(event)
            self.btn_mode_split.handle_event(event)
            
            self.slider_distance.handle_event(event)
            self.slider_speed.handle_event(event)
            
            self.btn_p8.handle_event(event)
            self.btn_p16.handle_event(event)
            self.btn_p50.handle_event(event)
            self.btn_p100.handle_event(event)
            
            self.btn_play.handle_event(event)
            self.btn_step.handle_event(event)
            self.btn_infinity.handle_event(event)
            self.btn_reset.handle_event(event)
            
            self.data_table.handle_event(event)
            self.btn_tab_graph.handle_event(event)
            self.btn_tab_loupe.handle_event(event)

    def draw(self):
        self.screen.fill(COLORS["bg_dark"])

        # 1. En-tête / Titre à gauche et Boutons à droite
        self._draw_header()

        # 2. Zone de visualisation de la trajectoire
        if self.mode == "SPLIT":
            self._draw_split_tracks()
        else:
            self._draw_single_track()

        # 3. Panneaux du bas
        self._draw_bottom_panel()

        # 4. Particules
        self.particles.draw(self.screen)

        pygame.display.flip()

    def _draw_header(self):
        # Titre net et moderne à gauche
        title_surf = self.font_title.render("LES PARADOXES DE ZÉNON", True, COLORS["text_main"])
        self.screen.blit(title_surf, (24, 14))

        sub_text = "Dichotomie : Le javelot atteindra-t-il sa cible ? (Séries convergentes & Limites)"
        sub_surf = self.font_subtitle.render(sub_text, True, COLORS["text_muted"])
        self.screen.blit(sub_surf, (24, 42))

        # Boutons de modes alignés à droite
        self.btn_mode_zenon.draw(self.screen, self.font_ui_bold)
        self.btn_mode_real.draw(self.screen, self.font_ui_bold)
        self.btn_mode_split.draw(self.screen, self.font_ui_bold)

    def _draw_single_track(self):
        track_y = 225
        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        # Bandeau explicatif du mode actuel
        self._draw_mode_banner(frame_rect.x + 16, frame_rect.y + 12, frame_rect.width - 32)

        # Piste de lancer
        piste_rect = pygame.Rect(track_start_x - 30, track_y - 45, track_w + 60, 90)
        pygame.draw.rect(self.screen, COLORS["track_bg"], piste_rect, border_radius=8)
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, track_y), (track_end_x, track_y), 4)

        # Point de départ (0m)
        pygame.draw.circle(self.screen, COLORS["white"], (track_start_x, track_y), 6)
        start_lbl = self.font_ui_bold.render("Départ (0 m)", True, COLORS["text_muted"])
        self.screen.blit(start_lbl, (track_start_x - 35, track_y + 18))

        # Cible au bout
        self._draw_target(track_end_x, track_y)

        # Jalons des fractions (1/2, 3/4, 7/8...)
        for i, step in enumerate(self.model.steps[:6]):
            frac_ratio = step.cumul_distance / self.model.total_distance
            jx = track_start_x + int(frac_ratio * track_w)
            
            pygame.draw.line(self.screen, COLORS["panel_border_bright"], (jx, track_y - 20), (jx, track_y + 20), 2)
            
            frac_lbl = self.font_ui_bold.render(step.fraction_str if i == 0 else f"+{step.fraction_str}", True, COLORS["gold"])
            self.screen.blit(frac_lbl, (jx - 14, track_y - 38))

            dist_lbl = self.font_ui.render(f"{step.cumul_distance:g}m", True, COLORS["text_muted"])
            self.screen.blit(dist_lbl, (jx - 12, track_y + 22))

            if i < 4:
                prev_ratio = 0.0 if i == 0 else self.model.steps[i-1].cumul_distance / self.model.total_distance
                prev_x = track_start_x + int(prev_ratio * track_w)
                mid_x = (prev_x + jx) // 2
                arc_lbl = self.font_ui.render(f"Δd = {step.delta_distance:g}m", True, (130, 170, 220))
                self.screen.blit(arc_lbl, (mid_x - 22, track_y - 58))

        # Javelot et informations selon le mode
        if self.infinity_active:
            # Mode Infini : Javelot exactement sur la cible avec halo
            self._draw_javelin(track_end_x, track_y, infinity_glow=True)
            self._draw_infinity_overlay(track_start_x, track_y + 60)
        elif self.mode == "REAL":
            st = self.model.get_continuous_state(self.sim_time)
            cur_d = st["current_distance"]
            cur_ratio = min(1.0, cur_d / self.model.total_distance)
            jx = track_start_x + int(cur_ratio * track_w)
            self._draw_javelin(jx, track_y)
            self._draw_live_stats_overlay(track_start_x, track_y + 70, st["current_distance"], st["current_time"], 
                                         st["remaining_distance"], st["progress"])
        elif self.mode == "ZENON":
            step = self.model.get_step(self.step_idx)
            cur_ratio = step.cumul_distance / self.model.total_distance
            jx = track_start_x + int(cur_ratio * track_w)
            self._draw_javelin(jx, track_y)
            self._draw_zenon_step_overlay(track_start_x, track_y + 60, step)

    def _draw_split_tracks(self):
        frame_h = self.height - 370
        frame_rect = pygame.Rect(24, 75, self.width - 48, frame_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], frame_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["panel_border"], frame_rect, width=1, border_radius=12)

        track_start_x = 90
        track_end_x = self.width - 90
        track_w = track_end_x - track_start_x

        # 1. Piste du Haut : Vision Zénon
        y_zenon = 175
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_zenon), (track_end_x, y_zenon), 3)
        self._draw_target(track_end_x, y_zenon)
        lbl_z = self.font_ui_bold.render("1. Point de vue de Zénon (Découpage discret : 'Infinité d'arrêts')", True, COLORS["gold"])
        self.screen.blit(lbl_z, (track_start_x, y_zenon - 45))

        st = self.model.get_continuous_state(self.sim_time)
        zenon_step = self.model.get_step(st["current_step_index"])
        zx = track_start_x + int((zenon_step.cumul_distance / self.model.total_distance) * track_w)
        self._draw_javelin(zx, y_zenon)

        # 2. Piste du Bas : Réalité continue
        y_real = 345
        pygame.draw.line(self.screen, COLORS["track_line"], (track_start_x, y_real), (track_end_x, y_real), 3)
        self._draw_target(track_end_x, y_real)
        lbl_r = self.font_ui_bold.render("2. Réalité Physique & Mathématique (Mouvement continu & Limite)", True, COLORS["cyan"])
        self.screen.blit(lbl_r, (track_start_x, y_real - 45))

        rx = track_start_x + int(st["progress"] * track_w)
        self._draw_javelin(rx, y_real)

        # Cartouche de comparaison au bas de la piste
        info_t = f"Temps écoulé : {st['current_time']:.2f}s / {self.model.total_time:.2f}s  |  Distance : {st['current_distance']:.2f}m / {self.model.total_distance:.2f}m"
        info_surf = self.font_ui_bold.render(info_t, True, COLORS["text_main"])
        self.screen.blit(info_surf, (track_start_x, 430))

    def _draw_mode_banner(self, x: int, y: int, width: int):
        banner_rect = pygame.Rect(x, y, width, 55)
        if self.infinity_active:
            pygame.draw.rect(self.screen, (50, 18, 70), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["infinity_color"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("♾️ DÉMONSTRATION DE LA LIMITE À L'INFINI (n → ∞)", True, COLORS["infinity_color"])
            t2 = self.font_ui.render(f"lim(n→∞) Σ(1/2ⁿ) = 1.00000000...  |  Distance restante = 0.000 m  |  Temps exact = {self.model.total_time:g}s. Triomphe mathématique !", True, COLORS["text_main"])
        elif self.mode == "ZENON":
            pygame.draw.rect(self.screen, (45, 34, 15), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["gold"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("🏛️ Vision du Paradoxe de Zénon : L'illusion de l'inaccessible", True, COLORS["gold"])
            t2 = self.font_ui.render("« Le javelot doit franchir 1/2, puis 1/4, puis 1/8... Comme il y a une infinité d'étapes, il n'atteindrait jamais la cible ! »", True, COLORS["text_main"])
        elif self.mode == "REAL":
            pygame.draw.rect(self.screen, (15, 45, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["cyan"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("📐 Résolution Mathématique : Somme d'une série géométrique convergente", True, COLORS["cyan"])
            t2 = self.font_ui.render(f"« Le temps se divise comme l'espace : Σ Δt = {self.model.total_time:g}s et Σ Δd = {self.model.total_distance:g}m. La cible est touchée exactement à t = {self.model.total_time:g}s ! »", True, COLORS["text_main"])
        else:
            pygame.draw.rect(self.screen, (38, 22, 60), banner_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["purple"], banner_rect, width=1, border_radius=8)
            t1 = self.font_ui_bold.render("⚖️ Double Vue Comparée : Paradoxe vs Vérité Physique", True, COLORS["purple"])
            t2 = self.font_ui.render("Observez comment le temps continu franchit chaque division sans jamais s'arrêter.", True, COLORS["text_main"])

        self.screen.blit(t1, (x + 14, y + 8))
        self.screen.blit(t2, (x + 14, y + 28))

    def _draw_javelin(self, x: int, y: int, infinity_glow: bool = False):
        length = 52
        trail_col = COLORS["infinity_color"] if infinity_glow else COLORS["cyan"]
        tip_col = COLORS["infinity_color"] if infinity_glow else COLORS["gold"]

        # Traînée lumineuse
        pygame.draw.line(self.screen, (trail_col[0], trail_col[1], trail_col[2]), (x - length - 20, y), (x - length, y), 2)
        
        # Corps du javelot
        pygame.draw.line(self.screen, COLORS["white"], (x - length, y), (x, y), 3)
        # Empennage
        pygame.draw.line(self.screen, trail_col, (x - length, y - 7), (x - length + 12, y), 2)
        pygame.draw.line(self.screen, trail_col, (x - length, y + 7), (x - length + 12, y), 2)
        # Pointe
        pygame.draw.polygon(self.screen, tip_col, [
            (x, y),
            (x - 14, y - 6),
            (x - 14, y + 6)
        ])
        
        # Halo de pointe
        glow_radius = 16 if infinity_glow else 10
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (tip_col[0], tip_col[1], tip_col[2], 140), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

    def _draw_target(self, x: int, y: int):
        r = 30
        pygame.draw.circle(self.screen, COLORS["white"], (x, y), r)
        pygame.draw.circle(self.screen, COLORS["cyan"], (x, y), int(r * 0.75))
        pygame.draw.circle(self.screen, COLORS["ruby"], (x, y), int(r * 0.5))
        pygame.draw.circle(self.screen, COLORS["gold"], (x, y), int(r * 0.25))
        
        pygame.draw.rect(self.screen, COLORS["panel_border_bright"], (x - 3, y + r, 6, 25))
        lbl = self.font_ui_bold.render(f"CIBLE ({self.model.total_distance:g} m)", True, COLORS["ruby"])
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

    def _draw_infinity_overlay(self, x: int, y: int, width: Optional[int] = None):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (40, 16, 60), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["infinity_color"], panel_rect, width=1, border_radius=8)

        t_inf = self.font_infinity.render("♾️ LIMITE ATTEINTE : n → ∞", True, COLORS["infinity_color"])
        t_desc = self.font_ui.render(f"Distance totale = {self.model.total_distance:g} m (100%)  |  Temps = {self.model.total_time:g} s  |  Distance restante = 0.000000000 m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("« L'infinité d'étapes infinitésimales tient dans un intervalle de temps fini ! »", True, COLORS["gold"])

        self.screen.blit(t_inf, (x + 15, y + 14))
        self.screen.blit(t_desc, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_zenon_step_overlay(self, x: int, y: int, step):
        w = self.width - 180
        panel_rect = pygame.Rect(x, y + 10, w, 70)
        pygame.draw.rect(self.screen, (38, 28, 14), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["gold"], panel_rect, width=1, border_radius=8)

        t_step = self.font_title.render(f"Étape {step.step_num} : Fraction {step.fraction_str}", True, COLORS["gold"])
        t_expl = self.font_ui.render(f"Distance étape : {step.delta_distance:g} m  |  Cumul : {step.cumul_distance:g} m  |  Reste à franchir : {step.remaining_distance:g} m", True, COLORS["text_main"])
        t_quote = self.font_ui_bold.render("« Il reste toujours une nouvelle moitié à parcourir... Le javelot semble prisonnier de la division ! »", True, COLORS["gold"])

        self.screen.blit(t_step, (x + 15, y + 14))
        self.screen.blit(t_expl, (x + 15, y + 42))
        self.screen.blit(t_quote, (x + 15, y + 60))

    def _draw_bottom_panel(self):
        panel_y = self.height - 275
        ctrl_w = 260

        # 1. Contrôles (Gauche)
        ctrl_rect = pygame.Rect(24, panel_y, ctrl_w, 260)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], ctrl_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["panel_border"], ctrl_rect, width=1, border_radius=10)

        title_ctrl = self.font_ui_bold.render("⚙️ Paramètres & Contrôles", True, COLORS["text_main"])
        self.screen.blit(title_ctrl, (34, panel_y + 10))

        self.slider_distance.draw(self.screen, self.font_ui, self.font_ui_bold)
        self.slider_speed.draw(self.screen, self.font_ui, self.font_ui_bold)

        self.btn_p8.draw(self.screen, self.font_ui)
        self.btn_p16.draw(self.screen, self.font_ui)
        self.btn_p50.draw(self.screen, self.font_ui)
        self.btn_p100.draw(self.screen, self.font_ui)

        self.btn_play.draw(self.screen, self.font_ui_bold)
        self.btn_step.draw(self.screen, self.font_ui_bold)
        self.btn_infinity.draw(self.screen, self.font_ui_bold)
        self.btn_reset.draw(self.screen, self.font_ui)

        # 2. Tableau de données (Milieu)
        self.data_table.draw(self.screen, self.font_ui_bold, self.font_ui, self.model.total_distance, self.model.total_time)

        # 3. Panneau Droit (Graphique ou Loupe)
        self.btn_tab_graph.draw(self.screen, self.font_ui_bold)
        self.btn_tab_loupe.draw(self.screen, self.font_ui_bold)

        st = self.model.get_continuous_state(self.sim_time)
        if self.right_tab == "GRAPH":
            self.mini_graph.draw(self.screen, self.model.total_distance, self.model.total_time, 
                                 st["current_time"], st["current_distance"], self.model.steps, 
                                 self.font_ui, self.font_ui_bold)
        else:
            self.zoom_loupe.draw(self.screen, self.model.total_distance, st["current_distance"], 
                                 self.model.steps, self.font_ui_bold, self.font_ui)

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
