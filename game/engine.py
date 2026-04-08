# moteur de jeu - gere les deplacements, collisions, score, vies, victoire/defaite

from game.agents import GhostMode


# suite des modes des fantômes : (mode, durée en ticks)
# à 60 fps : 420 ticks = 7 s, 1200 = 20 s, 300 = 5 s, 600 = 10 s
MODE_SEQUENCE = [
    (GhostMode.CAGED, 600),   # les fantômes restent dans la cage 10 s
    (GhostMode.SCATTER, 420),
    (GhostMode.CHASE, 1200),
    (GhostMode.SCATTER, 420),
    (GhostMode.CHASE, 1200),
    (GhostMode.SCATTER, 300),
    (GhostMode.CHASE, 1200),
    (GhostMode.SCATTER, 300),
    (GhostMode.CHASE, -1),  # indéfini
]


class GameEngine:

    def __init__(self, environment, pacman, ghosts, recorder=None):
        self.env = environment
        self.pacman = pacman
        self.ghosts = ghosts
        self.recorder = recorder

        self.score = 0
        self.lives = 3
        self.level = 1
        self.tick_count = 0
        self.game_over = False
        self.game_won = False
        self.paused = False

        # vitesse de déplacement (bouge tous les n ticks à 60 fps)
        self.pacman_speed = 8
        self.ghost_speed = 8
        self.ghost_frightened_speed = 12

        # suite des modes des fantômes
        self.ghost_mode_index = 0
        self.ghost_mode_timer = MODE_SEQUENCE[0][1]
        self.current_ghost_mode = MODE_SEQUENCE[0][0]

        # points quand on mange un fantôme
        self.ghost_eat_combo = 200

        # apparition des fruits
        self.pellets_eaten = 0
        self.fruit_spawned_1 = False
        self.fruit_spawned_2 = False

    def tick(self):
        # avance le jeu d'un tick
        if self.game_over or self.game_won or self.paused:
            return

        self.tick_count += 1

        # --- suite des modes des fantômes ---
        self._update_ghost_mode_cycle()

        # --- déplacer pac-man ---
        if self.tick_count % self.pacman_speed == 0:
            action = self.pacman.get_action(self.env)
            if action != (0, 0):
                nx = self.pacman.x + action[0]
                ny = self.pacman.y + action[1]
                if self.env.is_corridor(nx, ny):
                    self.pacman.x = nx
                    self.pacman.y = ny
                    self.pacman.direction = action
                    self._on_pacman_move()

        # --- déplacer les fantômes ---
        for ghost in self.ghosts:
            speed = (self.ghost_frightened_speed
                     if ghost.mode == GhostMode.FRIGHTENED
                     else self.ghost_speed)
            if self.tick_count % speed == 0:
                action = ghost.get_action(
                    self.env, pacman=self.pacman, ghosts=self.ghosts
                )
                if action != (0, 0):
                    nx = ghost.x + action[0]
                    ny = ghost.y + action[1]
                    if self.env.is_corridor(nx, ny):
                        ghost.x = nx
                        ghost.y = ny
                        ghost.direction = action

        # --- vérifier les collisions ---
        self._check_ghost_collisions()

        # --- gérer les fruits ---
        self.env.update_fruit()
        eaten_ratio = self.pellets_eaten / max(1, self.env.total_pellets)
        if not self.fruit_spawned_1 and eaten_ratio >= 0.3:
            self.env.spawn_fruit()
            self.fruit_spawned_1 = True
        elif not self.fruit_spawned_2 and eaten_ratio >= 0.7:
            self.env.spawn_fruit()
            self.fruit_spawned_2 = True

        # --- condition de victoire ---
        if self.env.all_pellets_eaten():
            self.game_won = True

        # --- enregistrer l'image du jeu ---
        if self.recorder:
            self.recorder.record_frame(self.get_state())

    def _on_pacman_move(self):
        # appelé quand pac-man bouge sur une nouvelle case
        x, y = self.pacman.x, self.pacman.y

        # manger une bille ou une grosse bille
        points, is_power = self.env.eat_pellet(x, y)
        if points > 0:
            self.score += points
            self.pellets_eaten += 1
            if is_power:
                self.ghost_eat_combo = 200
                for ghost in self.ghosts:
                    ghost.set_frightened()

        # manger un fruit
        fruit_pts = self.env.eat_fruit(x, y)
        self.score += fruit_pts

    def _check_ghost_collisions(self):
        # regarde si pac-man touche un fantôme
        for ghost in self.ghosts:
            if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                if ghost.mode == GhostMode.FRIGHTENED:
                    self.score += self.ghost_eat_combo
                    self.ghost_eat_combo = min(1600, self.ghost_eat_combo * 2)
                    ghost.reset()
                    ghost.mode = GhostMode.EATEN
                elif ghost.mode != GhostMode.EATEN:
                    self._pacman_dies()
                    return

    def _pacman_dies(self):
        # pac-man perd une vie
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self._reset_positions()

    def _reset_positions(self):
        # remet tous les agents au départ
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
            ghost.mode = self.current_ghost_mode

    def _update_ghost_mode_cycle(self):
        # avance le temps du cycle scatter/chase
        if self.ghost_mode_timer > 0:
            self.ghost_mode_timer -= 1
            if self.ghost_mode_timer <= 0:
                if self.ghost_mode_index < len(MODE_SEQUENCE) - 1:
                    self.ghost_mode_index += 1
                    mode, duration = MODE_SEQUENCE[self.ghost_mode_index]
                    self.current_ghost_mode = mode
                    self.ghost_mode_timer = duration

        for ghost in self.ghosts:
            ghost.update_mode(self.current_ghost_mode)

    def restart(self, environment):
        # relance le jeu avec un nouvel environnement
        self.env = environment
        self.score = 0
        self.lives = 3
        self.tick_count = 0
        self.game_over = False
        self.game_won = False
        self.ghost_mode_index = 0
        self.ghost_mode_timer = MODE_SEQUENCE[0][1]
        self.current_ghost_mode = MODE_SEQUENCE[0][0]
        self.ghost_eat_combo = 200
        self.pellets_eaten = 0
        self.fruit_spawned_1 = False
        self.fruit_spawned_2 = False

    def get_state(self):
        # retourne un résumé de l'état du jeu
        return {
            "tick": self.tick_count,
            "score": self.score,
            "lives": self.lives,
            "pacman": {
                "x": self.pacman.x,
                "y": self.pacman.y,
                "dir": self.pacman.direction,
            },
            "ghosts": [
                {
                    "name": g.NAME,
                    "x": g.x,
                    "y": g.y,
                    "dir": g.direction,
                    "mode": g.mode,
                }
                for g in self.ghosts
            ],
            "pellets_remaining": self.env.pellets_remaining(),
            "fruit_pos": self.env.fruit_pos,
        }
