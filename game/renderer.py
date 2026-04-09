# rendu pygame - dessine le labyrinthe, pacman, fantômes, score, etc.

import pygame
import math

from game.agents import GhostMode


class PacmanRenderer:

    WALL_COLOR = (24, 85, 255)
    PELLET_COLOR = (255, 255, 255)
    POWER_PELLET_COLOR = (255, 255, 255)
    PACMAN_COLOR = (255, 220, 40)
    FRUIT_COLOR = (255, 50, 50)
    FRIGHTENED_COLOR = (33, 33, 222)
    FRIGHTENED_FLASH = (255, 255, 255)
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (235, 235, 235)

    GHOST_COLORS = {
        "Blinky": (255, 0, 0),
        "Pinky": (255, 184, 255),
        "Inky": (0, 255, 255),
        "Clyde": (255, 184, 82),
    }

    def __init__(self, screen, window_w, window_h):
        self.screen = screen
        self.window_w = window_w
        self.window_h = window_h
        self.font = pygame.font.SysFont("Segoe UI", 24)
        self.small_font = pygame.font.SysFont("Segoe UI", 18)
        self.big_font = pygame.font.SysFont("Segoe UI", 48)
        self.tick = 0

        self.cell_size = 24
        self.offset_x = 70
        self.offset_y = 120
        self._last_score = 0

    def _calculate_layout(self, maze_w, maze_h):
        max_cell_w = (self.window_w - 140) // maze_w
        max_cell_h = (self.window_h - 240) // maze_h
        self.cell_size = max(10, min(max_cell_w, max_cell_h))
        maze_px_w = maze_w * self.cell_size
        self.offset_x = (self.window_w - maze_px_w) // 2
        self.offset_y = 120

    def render(self, engine, game_mode="normal", capture_tick=None, replay_ai="bfs", rating_message=None):
        # dessine une frame complète du jeu
        self.tick += 1
        self._last_score = engine.score
        self._game_mode = game_mode
        self._capture_tick = capture_tick
        self._replay_ai = replay_ai
        self._rating_message = rating_message
        self.screen.fill(self.BG_COLOR)

        self._calculate_layout(engine.env.width, engine.env.height)

        self._draw_maze(engine.env)
        self._draw_pellets(engine.env)
        self._draw_fruit(engine.env)
        self._draw_ghosts(engine.ghosts)
        self._draw_pacman(engine.pacman)
        self._draw_hud(engine)

        if engine.game_over:
            self._draw_overlay("GAME OVER", (255, 50, 50))
        elif engine.game_won:
            self._draw_overlay("LEVEL COMPLETE!", (50, 255, 50))

        pygame.display.flip()

    def _draw_maze(self, env):
        maze_px_w = env.width * self.cell_size
        maze_px_h = env.height * self.cell_size
        pygame.draw.rect(
            self.screen, (8, 8, 20),
            (self.offset_x - 6, self.offset_y - 6, maze_px_w + 12, maze_px_h + 12),
            border_radius=12,
        )

        for x, y in env.walls:
            px = self.offset_x + x * self.cell_size
            py = self.offset_y + y * self.cell_size
            pygame.draw.rect(
                self.screen, self.WALL_COLOR,
                (px, py, self.cell_size, self.cell_size),
                border_radius=max(2, self.cell_size // 5),
            )

    def _draw_pellets(self, env):
        for x, y in env.pellets:
            cx = self.offset_x + x * self.cell_size + self.cell_size // 2
            cy = self.offset_y + y * self.cell_size + self.cell_size // 2
            r = max(1, self.cell_size // 8)
            pygame.draw.circle(self.screen, self.PELLET_COLOR, (cx, cy), r)

        # les power pellets clignotent
        show = (self.tick // 12) % 2 == 0
        if show:
            for x, y in env.power_pellets:
                cx = self.offset_x + x * self.cell_size + self.cell_size // 2
                cy = self.offset_y + y * self.cell_size + self.cell_size // 2
                r = max(3, self.cell_size // 3)
                pygame.draw.circle(self.screen, self.POWER_PELLET_COLOR, (cx, cy), r)

    def _draw_fruit(self, env):
        if not env.fruit_pos:
            return
        x, y = env.fruit_pos
        cx = self.offset_x + x * self.cell_size + self.cell_size // 2
        cy = self.offset_y + y * self.cell_size + self.cell_size // 2
        r = max(4, self.cell_size // 3)
        # dessine une cerise
        pygame.draw.circle(self.screen, self.FRUIT_COLOR, (cx - r // 3, cy), r)
        pygame.draw.circle(self.screen, (200, 0, 0), (cx + r // 3, cy), r)
        pygame.draw.line(self.screen, (0, 180, 0), (cx, cy - r), (cx, cy - r - 4), 2)

    def _draw_pacman(self, pacman):
        px = self.offset_x + pacman.x * self.cell_size + self.cell_size // 2
        py = self.offset_y + pacman.y * self.cell_size + self.cell_size // 2
        radius = max(5, self.cell_size // 2 - 2)

        mouth = (self.tick // 6) % 2
        open_angle = 35 if mouth == 0 else 5

        dir_angle = {
            (1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270
        }.get(tuple(pacman.direction), 0)

        start_a = dir_angle + open_angle
        end_a = dir_angle - open_angle

        # corps de pacman
        pygame.draw.circle(self.screen, self.PACMAN_COLOR, (px, py), radius)

        # découpe de la bouche
        v_start = pygame.math.Vector2(1, 0).rotate(start_a)
        v_end = pygame.math.Vector2(1, 0).rotate(end_a)
        p1 = (px, py)
        p2 = (int(px + radius * v_start.x), int(py - radius * v_start.y))
        p3 = (int(px + radius * v_end.x), int(py - radius * v_end.y))
        pygame.draw.polygon(self.screen, self.BG_COLOR, [p1, p2, p3])

    def _draw_ghosts(self, ghosts):
        for ghost in ghosts:
            px = self.offset_x + ghost.x * self.cell_size + self.cell_size // 2
            py = self.offset_y + ghost.y * self.cell_size + self.cell_size // 2
            radius = max(5, self.cell_size // 2 - 2)

            # choisir la couleur
            if ghost.mode == GhostMode.FRIGHTENED:
                if ghost.frightened_timer < 120 and (self.tick // 8) % 2:
                    color = self.FRIGHTENED_FLASH
                else:
                    color = self.FRIGHTENED_COLOR
            elif ghost.mode == GhostMode.EATEN:
                self._draw_ghost_eyes(px, py, radius, ghost.direction)
                continue
            else:
                color = self.GHOST_COLORS.get(ghost.NAME, (255, 0, 0))

            # corps du fantôme - dome + rectangle + base ondulee
            dome_rect = pygame.Rect(px - radius, py - radius, radius * 2, radius * 2)
            pygame.draw.circle(self.screen, color, (px, py - radius // 4), radius)
            pygame.draw.rect(self.screen, color,
                             (px - radius, py - radius // 4, radius * 2, radius))

            # base ondulée
            wave_count = 3
            wave_w = (radius * 2) // wave_count
            bottom_y = py + radius - radius // 4
            for i in range(wave_count):
                bx = px - radius + i * wave_w + wave_w // 2
                pygame.draw.circle(self.screen, color, (bx, bottom_y), wave_w // 2)

            # yeux

    def _draw_ghost_eyes(self, px, py, radius, direction):
        eye_r = max(2, radius // 3)
        pupil_r = max(1, eye_r // 2)
        eye_y = py - radius // 3

        for ex in [px - radius // 3, px + radius // 3]:
            # blanc de l'oeil
            pygame.draw.circle(self.screen, (255, 255, 255), (ex, eye_y), eye_r)
            # pupille suit la direction
            dx = direction[0] if direction else 0
            dy = direction[1] if direction else 0
            pupil_x = int(ex + dx * pupil_r)
            pupil_y = int(eye_y + dy * pupil_r)
            pygame.draw.circle(self.screen, (0, 0, 80), (pupil_x, pupil_y), pupil_r)

    def _draw_hud(self, engine):
        # score - cote gauche
        score_surf = self.font.render(f"Score: {engine.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_surf, (24, 16))

        # vies - cote droit
        lives_str = "\u2665 " * engine.lives
        lives_surf = self.font.render(f"Lives: {lives_str}", True, (255, 80, 80))
        self.screen.blit(lives_surf, (self.window_w - 220, 16))

        # niveau - centre
        level_surf = self.small_font.render(f"Level {engine.level}", True, (210, 210, 210))
        self.screen.blit(level_surf, (self.window_w // 2 - 30, 16))

        # ligne d'info
        remaining = engine.env.pellets_remaining()
        info = f"Pellets: {remaining}/{engine.env.total_pellets}   Maze: {engine.env.width}x{engine.env.height}"
        info_surf = self.small_font.render(info, True, (180, 180, 180))
        self.screen.blit(info_surf, (24, 50))

        # indicateur du mode fantômes
        mode_text = f"Ghosts: {engine.current_ghost_mode}"
        mode_surf = self.small_font.render(mode_text, True, (160, 160, 160))
        self.screen.blit(mode_surf, (24, 72))

        # indicateur du mode de jeu
        if self._game_mode == "solo":
            tag = self.font.render("SOLO (sans fantômes)", True, (80, 255, 80))
            self.screen.blit(tag, (self.window_w // 2 - 100, 50))
        elif self._game_mode == "replay":
            tag = self.font.render(f"REPLAY - IA : {self._replay_ai}", True, (80, 180, 255))
            self.screen.blit(tag, (self.window_w // 2 - 100, 50))
            if self._capture_tick is not None:
                cap = self.font.render(f"Capture au tick {self._capture_tick}", True, (255, 100, 100))
                self.screen.blit(cap, (self.window_w // 2 - 100, 74))

        # contrôles
        controls = "Arrows/WASD: move | N: new | R: restart | 1: solo | 2: replay | ESC: quit"
        ctrl_surf = self.small_font.render(controls, True, (140, 140, 140))
        self.screen.blit(ctrl_surf, (24, self.window_h - 50))

        rating_info = "0-7: rate maze | +/-: size | Numpad 0/2/4: loops%"
        rating_surf = self.small_font.render(rating_info, True, (120, 120, 120))
        self.screen.blit(rating_surf, (24, self.window_h - 28))

        # message de notation
        if self._rating_message:
            msg_surf = self.font.render(self._rating_message, True, (255, 220, 50))
            self.screen.blit(msg_surf, (self.window_w // 2 - msg_surf.get_width() // 2, 92))

    def _draw_overlay(self, text, color):
        overlay = pygame.Surface((self.window_w, self.window_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        text_surf = self.big_font.render(text, True, color)
        rect = text_surf.get_rect(center=(self.window_w // 2, self.window_h // 2 - 20))
        self.screen.blit(text_surf, rect)

        score_surf = self.font.render(f"Final Score: {self._last_score}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(self.window_w // 2, self.window_h // 2 + 30))
        self.screen.blit(score_surf, score_rect)

        # affiche le tick de capture en mode replay
        if self._game_mode == "replay" and self._capture_tick is not None:
            cap_surf = self.font.render(
                f"Capturé au tick {self._capture_tick}", True, (255, 180, 80)
            )
            cap_rect = cap_surf.get_rect(center=(self.window_w // 2, self.window_h // 2 + 60))
            self.screen.blit(cap_surf, cap_rect)
            hint_y = self.window_h // 2 + 95
        else:
            hint_y = self.window_h // 2 + 65

        hint = self.small_font.render("N: new maze  |  R: restart  |  1: solo  |  2: replay  |  ESC: quit", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.window_w // 2, hint_y))
        self.screen.blit(hint, hint_rect)
