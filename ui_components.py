"""
Composants d'interface utilisateur (UI) modernes, nets et contrastés pour Pygame.
Comprend des boutons stylisés, des curseurs, des tableaux de données, des graphiques et des effets visuels.
"""
import pygame
import math
from typing import List, Tuple, Callable, Optional, Any
from zeno_sim import ZenoStep

# Palette de couleurs ultra-nette et contrastée (Thème Neo-Dark Lab)
COLORS = {
    "bg_dark": (11, 17, 32),            # Fond profond bleu nuit
    "panel_bg": (20, 30, 50),           # Panneau opaque bien contrasté
    "panel_card": (26, 38, 64),         # Cartes intérieures
    "panel_border": (55, 78, 115),      # Bordures nettes
    "panel_border_bright": (85, 120, 175),
    "text_main": (255, 255, 255),       # Blanc pur ultra-lisible
    "text_muted": (165, 185, 215),      # Gris-bleu clair
    "cyan": (0, 220, 255),              # Cyan néon vif
    "cyan_glow": (0, 220, 255, 90),
    "gold": (255, 190, 20),             # Or étincelant
    "gold_glow": (255, 190, 20, 100),
    "emerald": (16, 225, 140),          # Émeraude vive
    "emerald_glow": (16, 225, 140, 90),
    "ruby": (255, 70, 90),              # Rouge carmin vif
    "purple": (195, 110, 255),          # Violet néon
    "infinity_color": (230, 120, 255),  # Teinte spéciale Infini
    "track_bg": (16, 24, 42),
    "track_line": (50, 75, 115),
    "white": (255, 255, 255),
    "table_header": (28, 42, 70),
    "table_row_alt": (22, 33, 56),
    "table_row_active": (12, 60, 100),
    "table_infinity": (60, 25, 80),
}

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable[[], None]] = None,
                 color: Tuple[int, int, int] = COLORS["cyan"],
                 text_color: Tuple[int, int, int] = COLORS["text_main"],
                 icon: Optional[str] = None,
                 is_toggle: bool = False,
                 active: bool = False,
                 font_size_override: Optional[int] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.base_color = color
        self.text_color = text_color
        self.icon = icon
        self.is_toggle = is_toggle
        self.active = active
        self.is_hovered = False
        self.is_pressed = False
        self.hover_anim = 0.0

    def set_position(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        self.rect.x = x
        self.rect.y = y
        if width is not None:
            self.rect.width = width
        if height is not None:
            self.rect.height = height

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.is_toggle:
                    self.active = not self.active
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        return False

    def update(self, dt: float):
        target = 1.0 if self.is_hovered else 0.0
        self.hover_anim += (target - self.hover_anim) * min(1.0, dt * 16)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        # Couleur dynamique
        if self.active:
            fill_col = self.base_color
            border_col = COLORS["white"]
            txt_col = (10, 15, 25)
        else:
            r = int(self.base_color[0] * 0.25 + (self.base_color[0] * 0.45) * self.hover_anim)
            g = int(self.base_color[1] * 0.25 + (self.base_color[1] * 0.45) * self.hover_anim)
            b = int(self.base_color[2] * 0.25 + (self.base_color[2] * 0.45) * self.hover_anim)
            fill_col = (r, g, b)
            border_col = (
                min(255, int(self.base_color[0] * (0.8 + 0.3 * self.hover_anim))),
                min(255, int(self.base_color[1] * (0.8 + 0.3 * self.hover_anim))),
                min(255, int(self.base_color[2] * (0.8 + 0.3 * self.hover_anim)))
            )
            txt_col = COLORS["text_main"]

        # Effet Halo lumineux si survolé ou actif
        if self.hover_anim > 0.05 or self.active:
            glow_amt = max(self.hover_anim, 0.6 if self.active else 0.0)
            glow_rect = self.rect.inflate(int(8 * glow_amt), int(8 * glow_amt))
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (self.base_color[0], self.base_color[1], self.base_color[2], int(60 * glow_amt)),
                             (0, 0, glow_rect.width, glow_rect.height), border_radius=9)
            surface.blit(glow_surf, glow_rect.topleft)

        # Fond du bouton avec bords arrondis
        pygame.draw.rect(surface, fill_col, self.rect, border_radius=7)
        pygame.draw.rect(surface, border_col, self.rect, width=2 if (self.is_hovered or self.active) else 1, border_radius=7)

        # Texte net anti-aliasé
        txt_surf = font.render(self.text, True, txt_col)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float, 
                 label: str, unit: str = "", step: float = 0.0,
                 on_change: Optional[Callable[[float], None]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.unit = unit
        self.step = step
        self.on_change = on_change
        self.is_dragging = False
        self.is_hovered = False

    def set_position(self, x: int, y: int, width: Optional[int] = None):
        self.rect.x = x
        self.rect.y = y
        if width is not None:
            self.rect.width = width

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_dragging:
                self._update_val_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        return False

    def _update_val_from_mouse(self, mouse_x: int):
        ratio = max(0.0, min(1.0, (mouse_x - self.rect.x) / self.rect.width))
        raw_val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.step > 0:
            raw_val = round(raw_val / self.step) * self.step
        self.value = max(self.min_val, min(self.max_val, raw_val))
        if self.on_change:
            self.on_change(self.value)

    def set_value(self, val: float):
        self.value = max(self.min_val, min(self.max_val, val))

    def draw(self, surface: pygame.Surface, font_main: pygame.font.Font, font_val: pygame.font.Font):
        # Libellé en haut
        label_surf = font_main.render(f"{self.label}:", True, COLORS["text_muted"])
        surface.blit(label_surf, (self.rect.x, self.rect.y - 20))

        # Valeur en haut à droite en surbrillance
        val_str = f"{self.value:g} {self.unit}".strip()
        val_surf = font_val.render(val_str, True, COLORS["cyan"])
        val_rect = val_surf.get_rect(topright=(self.rect.right, self.rect.y - 20))
        surface.blit(val_surf, val_rect)

        # Barre de fond du slider
        bar_rect = pygame.Rect(self.rect.x, self.rect.centery - 4, self.rect.width, 8)
        pygame.draw.rect(surface, (35, 50, 80), bar_rect, border_radius=4)

        # Barre de progression colorée
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        progress_rect = pygame.Rect(self.rect.x, self.rect.centery - 4, int(self.rect.width * ratio), 8)
        pygame.draw.rect(surface, COLORS["cyan"], progress_rect, border_radius=4)

        # Curseur / Handle avec halo
        handle_x = self.rect.x + int(self.rect.width * ratio)
        handle_y = self.rect.centery
        handle_radius = 9 if (self.is_dragging or self.is_hovered) else 7
        
        if self.is_dragging or self.is_hovered:
            glow_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 220, 255, 120), (18, 18), 16)
            surface.blit(glow_surf, (handle_x - 18, handle_y - 18))

        pygame.draw.circle(surface, COLORS["white"], (handle_x, handle_y), handle_radius)
        pygame.draw.circle(surface, COLORS["cyan"], (handle_x, handle_y), handle_radius, width=2)


class DataTable:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.columns = ["Étape", "Fraction", "Δ Dist.", "Δ Temps", "Σ Dist.", "Σ Temps", "Reste"]
        self.col_widths = [60, 70, 85, 80, 90, 85, 85]
        self.steps: List[ZenoStep] = []
        self.active_step_idx = -1
        self.scroll_y = 0
        self.max_visible_rows = 9
        self.show_infinity_row = False

    def set_position(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        self.rect.x = x
        self.rect.y = y
        if width is not None:
            self.rect.width = width
            # Adapter les largeurs de colonnes proportionnellement
            total_ratio = sum([55, 65, 80, 75, 85, 80, 80])
            self.col_widths = [int(w / total_ratio * (self.rect.width - 20)) for w in [55, 65, 80, 75, 85, 80, 80]]
        if height is not None:
            self.rect.height = height
            self.max_visible_rows = max(4, int((self.rect.height - 55) / 24))

    def set_data(self, steps: List[ZenoStep], active_step: int = -1, show_infinity: bool = False):
        self.steps = steps
        self.active_step_idx = active_step
        self.show_infinity_row = show_infinity

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_y = max(0, min(len(self.steps) - self.max_visible_rows, self.scroll_y - event.y))

    def draw(self, surface: pygame.Surface, font_head: pygame.font.Font, font_row: pygame.font.Font, total_d: float, total_t: float):
        # Fond du tableau net et contrasté
        pygame.draw.rect(surface, COLORS["panel_bg"], self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["panel_border"], self.rect, width=1, border_radius=10)

        # En-tête
        header_height = 30
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, header_height)
        pygame.draw.rect(surface, COLORS["table_header"], header_rect, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(surface, COLORS["panel_border_bright"], (self.rect.x, self.rect.y + header_height), 
                         (self.rect.right, self.rect.y + header_height), 1)

        curr_x = self.rect.x + 10
        for col_name, width in zip(self.columns, self.col_widths):
            head_surf = font_head.render(col_name, True, COLORS["text_main"])
            surface.blit(head_surf, (curr_x, self.rect.y + 6))
            curr_x += width

        # Lignes
        row_height = 24
        start_y = self.rect.y + header_height + 3
        visible_steps = self.steps[self.scroll_y : self.scroll_y + self.max_visible_rows]

        for i, step in enumerate(visible_steps):
            actual_idx = self.scroll_y + i
            y = start_y + i * row_height
            row_rect = pygame.Rect(self.rect.x + 4, y, self.rect.width - 8, row_height - 1)

            # Couleur de fond de la ligne
            if actual_idx == self.active_step_idx:
                pygame.draw.rect(surface, COLORS["table_row_active"], row_rect, border_radius=5)
                pygame.draw.rect(surface, COLORS["cyan"], row_rect, width=1, border_radius=5)
                txt_color = COLORS["cyan"]
            elif actual_idx < self.active_step_idx:
                pygame.draw.rect(surface, (18, 48, 72), row_rect, border_radius=5)
                txt_color = COLORS["emerald"]
            elif i % 2 == 1:
                pygame.draw.rect(surface, COLORS["table_row_alt"], row_rect, border_radius=5)
                txt_color = COLORS["text_main"]
            else:
                txt_color = COLORS["text_muted"]

            # Données formatées
            values = [
                f"n = {step.step_num}",
                step.fraction_str,
                f"{step.delta_distance:.3g} m",
                f"{step.delta_time:.3g} s",
                f"{step.cumul_distance:.3g} m",
                f"{step.cumul_time:.3g} s",
                f"{step.remaining_distance:.3g} m"
            ]

            curr_x = self.rect.x + 10
            for val_text, width in zip(values, self.col_widths):
                val_surf = font_row.render(val_text, True, txt_color)
                surface.blit(val_surf, (curr_x, y + 4))
                curr_x += width

        # Si le mode Infini est actif, afficher la ligne d'infinité au bas
        if self.show_infinity_row:
            inf_y = self.rect.bottom - 46
            inf_rect = pygame.Rect(self.rect.x + 4, inf_y, self.rect.width - 8, 22)
            pygame.draw.rect(surface, COLORS["table_infinity"], inf_rect, border_radius=5)
            pygame.draw.rect(surface, COLORS["infinity_color"], inf_rect, width=1, border_radius=5)
            
            inf_values = [
                "n = ∞",
                "1/2^∞ → 0",
                "0.000 m",
                "0.000 s",
                f"{total_d:g} m (100%)",
                f"{total_t:g} s (100%)",
                "0.000 m"
            ]
            curr_x = self.rect.x + 10
            for val_text, width in zip(inf_values, self.col_widths):
                inf_surf = font_row.render(val_text, True, COLORS["infinity_color"])
                surface.blit(inf_surf, (curr_x, inf_y + 3))
                curr_x += width

        # Résumé mathématique en bas du tableau
        info_y = self.rect.bottom - 22
        info_surf = font_row.render("✨ Limite : Σ 1/2ⁿ = 100% du trajet en 100% du temps prévu !", True, COLORS["gold"])
        surface.blit(info_surf, (self.rect.x + 12, info_y))


class MiniGraph:
    """Graphique dynamique de convergence mathématique : Distance = f(Temps) et Asymptote."""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)

    def set_position(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        self.rect.x = x
        self.rect.y = y
        if width is not None:
            self.rect.width = width
        if height is not None:
            self.rect.height = height

    def draw(self, surface: pygame.Surface, total_d: float, total_t: float, 
             current_t: float, current_d: float, steps: List[ZenoStep], 
             font_axis: pygame.font.Font, font_label: pygame.font.Font):
        # Fond du graphique
        pygame.draw.rect(surface, COLORS["panel_bg"], self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["panel_border"], self.rect, width=1, border_radius=10)

        # Marges intérieures
        gx = self.rect.x + 48
        gy = self.rect.y + 28
        gw = self.rect.width - 65
        gh = self.rect.height - 60

        # Titre
        title_surf = font_label.render("Convergence : Distance = f(Temps)", True, COLORS["cyan"])
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 7))

        # Axes
        pygame.draw.line(surface, COLORS["panel_border_bright"], (gx, gy + gh), (gx + gw, gy + gh), 2) # Axe Temps
        pygame.draw.line(surface, COLORS["panel_border_bright"], (gx, gy), (gx, gy + gh), 2)           # Axe Distance

        # Ligne d'asymptote / Cible (Distance max D)
        target_y = gy
        pygame.draw.line(surface, COLORS["ruby"], (gx, target_y), (gx + gw, target_y), 2)
        asymp_surf = font_axis.render(f"Cible = {total_d:g}m", True, COLORS["ruby"])
        surface.blit(asymp_surf, (gx + gw - 70, target_y - 16))

        # Labels axes
        time_label = font_axis.render(f"Temps (s) → Limite: {total_t:g}s", True, COLORS["text_muted"])
        surface.blit(time_label, (gx + gw // 3, gy + gh + 6))

        dist_label = font_axis.render("Dist.(m)", True, COLORS["text_muted"])
        surface.blit(dist_label, (self.rect.x + 4, gy - 4))

        # Grille
        for fraction in [0.25, 0.5, 0.75]:
            grid_y = gy + gh - int(gh * fraction)
            pygame.draw.line(surface, (30, 46, 75), (gx, grid_y), (gx + gw, grid_y), 1)
            lbl = font_axis.render(f"{total_d * fraction:g}", True, (120, 150, 190))
            surface.blit(lbl, (gx - 30, grid_y - 6))

        # Courbe théorique continue
        points_curve = []
        for px in range(0, int(gw) + 1):
            ratio_t = px / gw
            ratio_d = ratio_t
            py = gy + gh - int(gh * ratio_d)
            points_curve.append((gx + px, py))

        if len(points_curve) > 1:
            pygame.draw.lines(surface, (40, 75, 120), False, points_curve, 2)

        # Points d'étapes de Zénon
        for step in steps[:7]:
            if total_t > 0:
                sx = gx + int((step.cumul_time / total_t) * gw)
                sy = gy + gh - int((step.cumul_distance / total_d) * gh)
                pygame.draw.circle(surface, COLORS["gold"], (sx, sy), 4)
                pygame.draw.line(surface, (120, 95, 30), (sx, gy + gh), (sx, sy), 1)

        # Trait parcouru en temps réel
        if total_t > 0:
            cur_ratio_t = min(1.0, current_t / total_t)
            cur_ratio_d = min(1.0, current_d / total_d)
            cx = gx + int(cur_ratio_t * gw)
            cy = gy + gh - int(cur_ratio_d * gh)

            traveled_pts = [pt for pt in points_curve if pt[0] <= cx]
            if len(traveled_pts) > 1:
                pygame.draw.lines(surface, COLORS["cyan"], False, traveled_pts, 3)

            # Curseur javelot actuel
            pygame.draw.circle(surface, COLORS["white"], (cx, cy), 6)
            pygame.draw.circle(surface, COLORS["cyan"], (cx, cy), 9, width=2)


class ZoomLoupe:
    """Loupe microscopique montrant l'approche infinitésimale de la cible."""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.zoom_factor = 50.0

    def set_position(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        self.rect.x = x
        self.rect.y = y
        if width is not None:
            self.rect.width = width
        if height is not None:
            self.rect.height = height

    def draw(self, surface: pygame.Surface, total_d: float, current_d: float, 
             steps: List[ZenoStep], font_title: pygame.font.Font, font_labels: pygame.font.Font):
        pygame.draw.rect(surface, COLORS["panel_bg"], self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["gold"], self.rect, width=1, border_radius=10)

        # Titre
        header_surf = font_title.render(f"🔬 Loupe Microscopique (Zoom x{int(self.zoom_factor)})", True, COLORS["gold"])
        surface.blit(header_surf, (self.rect.x + 14, self.rect.y + 8))

        sub_surf = font_labels.render("Observation des divisions infinitésimales (1/16, 1/32, 1/64...)", True, COLORS["text_muted"])
        surface.blit(sub_surf, (self.rect.x + 14, self.rect.y + 28))

        track_y = self.rect.y + 75
        track_x_start = self.rect.x + 25
        track_x_target = self.rect.right - 40
        track_width = track_x_target - track_x_start

        window_range = total_d / (self.zoom_factor * 0.1)
        window_start_d = total_d - window_range

        pygame.draw.line(surface, COLORS["panel_border_bright"], (track_x_start, track_y), (track_x_target, track_y), 3)

        # Cible
        pygame.draw.line(surface, COLORS["ruby"], (track_x_target, track_y - 25), (track_x_target, track_y + 25), 4)
        tgt_lbl = font_labels.render(f"CIBLE ({total_d:g}m)", True, COLORS["ruby"])
        surface.blit(tgt_lbl, (track_x_target - 40, track_y + 30))

        # Graduations
        for step in steps:
            if step.cumul_distance >= window_start_d:
                ratio = (step.cumul_distance - window_start_d) / window_range
                gx = track_x_start + int(ratio * track_width)
                if track_x_start <= gx <= track_x_target:
                    pygame.draw.line(surface, COLORS["gold"], (gx, track_y - 14), (gx, track_y + 14), 2)
                    step_txt = font_labels.render(f"n={step.step_num}", True, COLORS["gold"])
                    surface.blit(step_txt, (gx - 12, track_y - 28))
                    
                    frac_txt = font_labels.render(step.fraction_str, True, COLORS["text_muted"])
                    surface.blit(frac_txt, (gx - 14, track_y + 16))

        # Position javelot
        if current_d >= window_start_d:
            cur_ratio = min(1.0, (current_d - window_start_d) / window_range)
            jx = track_x_start + int(cur_ratio * track_width)
            
            pygame.draw.polygon(surface, COLORS["cyan"], [
                (jx, track_y),
                (jx - 15, track_y - 7),
                (jx - 15, track_y + 7)
            ])
            pygame.draw.line(surface, COLORS["white"], (jx - 15, track_y), (jx - 45, track_y), 3)
            
            rem = max(0.0, total_d - current_d)
            rem_txt = font_labels.render(f"Reste: {rem:.4g}m", True, COLORS["cyan"])
            surface.blit(rem_txt, (max(track_x_start, jx - 35), track_y - 45))
        else:
            out_txt = font_labels.render("← Javelot en approche (hors champ zoom)", True, COLORS["text_muted"])
            surface.blit(out_txt, (track_x_start + 10, track_y - 12))


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], lifetime: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 180 * dt
        self.age += dt
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        alpha = max(0, int(255 * (1.0 - self.age / self.lifetime)))
        radius = max(1, int(4 * (1.0 - self.age / self.lifetime)))
        p_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (self.color[0], self.color[1], self.color[2], alpha), (radius, radius), radius)
        surface.blit(p_surf, (int(self.x - radius), int(self.y - radius)))


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def emit_impact(self, x: float, y: float, count: int = 45, theme: str = "normal"):
        import random
        for _ in range(count):
            angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            speed = random.uniform(90, 360)
            vx = math.cos(angle) * speed + random.uniform(-40, -10)
            vy = math.sin(angle) * speed
            if theme == "infinity":
                color = random.choice([COLORS["infinity_color"], COLORS["purple"], COLORS["gold"], COLORS["white"]])
            else:
                color = random.choice([COLORS["cyan"], COLORS["gold"], COLORS["emerald"], COLORS["white"]])
            lifetime = random.uniform(0.5, 1.2)
            self.particles.append(Particle(x, y, vx, vy, color, lifetime))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)
