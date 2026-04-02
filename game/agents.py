# agents — pacman (humain / futur IA) et fantômes (chacun avec une IA différente)

from abc import ABC, abstractmethod
from collections import deque
import random


class GhostMode:
    SCATTER = "scatter"
    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


# --- pathfinding ---

def bfs_direction(walls, width, height, start, target):
    # bfs : retourne (dx, dy) du premier pas vers la cible
    if start == target:
        return (0, 0)

    visited = {start}
    queue = deque([(start, None)])  # (position, 1ere direction prise)

    while queue:
        (x, y), first_dir = queue.popleft()
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in visited and (nx, ny) not in walls):
                direction = first_dir if first_dir else (dx, dy)
                if (nx, ny) == target:
                    return direction
                visited.add((nx, ny))
                queue.append(((nx, ny), direction))

    return (0, 0)


# --- classe de base agent ---

class Agent(ABC):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.direction = (0, 0)

    @abstractmethod
    def get_action(self, environment, **context):
        # retourne (dx, dy) pour le prochain mouvement
        pass

    def reset(self):
        # remet l'agent à sa position de départ
        self.x = self.start_x
        self.y = self.start_y
        self.direction = (0, 0)


# --- agent pacman ---

class HumanAgent(Agent):
    # pacman contrôlé par le clavier

    def __init__(self, x, y):
        super().__init__(x, y)
        self.next_direction = (0, 0)

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def get_action(self, environment, **context):
        # essaye la direction demandée
        nx = self.x + self.next_direction[0]
        ny = self.y + self.next_direction[1]
        if self.next_direction != (0, 0) and environment.is_corridor(nx, ny):
            self.direction = self.next_direction
            return self.direction

        # sinon continue dans la direction actuelle
        nx = self.x + self.direction[0]
        ny = self.y + self.direction[1]
        if environment.is_corridor(nx, ny):
            return self.direction

        return (0, 0)


# --- agents fantômes ---

class GhostAgent(Agent):
    # fantôme de base avec IA, chaque sous-classe définit son ciblage

    COLOR = (255, 0, 0)
    NAME = "Ghost"

    def __init__(self, x, y, maze_width, maze_height):
        super().__init__(x, y)
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.mode = GhostMode.SCATTER
        self.frightened_timer = 0
        self.scatter_target = (0, 0)

    def get_target(self, environment, pacman, ghosts):
        # à redéfinir dans chaque sous-classe
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        return (pacman.x, pacman.y)

    def get_action(self, environment, **context):
        pacman = context.get("pacman")
        ghosts = context.get("ghosts", [])

        if self.mode == GhostMode.FRIGHTENED:
            return self._random_direction(environment)

        if self.mode == GhostMode.EATEN:
            # retour au point de départ
            return bfs_direction(
                environment.walls, environment.width, environment.height,
                (self.x, self.y), (self.start_x, self.start_y)
            )

        target = self.get_target(environment, pacman, ghosts)
        return bfs_direction(
            environment.walls, environment.width, environment.height,
            (self.x, self.y), target
        )

    def _random_direction(self, environment):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        reverse = (-self.direction[0], -self.direction[1])
        valid = []
        for d in directions:
            nx, ny = self.x + d[0], self.y + d[1]
            if environment.is_corridor(nx, ny) and d != reverse:
                valid.append(d)
        if not valid:
            for d in directions:
                nx, ny = self.x + d[0], self.y + d[1]
                if environment.is_corridor(nx, ny):
                    valid.append(d)
        return valid[0] if valid else (0, 0)

    def set_frightened(self, duration=480):
        # passe en mode effrayé (quand pacman mange un power pellet)
        if self.mode != GhostMode.EATEN:
            self.mode = GhostMode.FRIGHTENED
            self.frightened_timer = duration

    def update_mode(self, global_mode):
        # synchronise avec le mode global (cycle scatter/chase)
        if self.mode == GhostMode.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = global_mode
        elif self.mode == GhostMode.EATEN:
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.mode = global_mode
        else:
            self.mode = global_mode


class BlinkyGhost(GhostAgent):
    # rouge — cible directement la position de pacman (chasseur)
    COLOR = (255, 0, 0)
    NAME = "Blinky"

    def __init__(self, x, y, maze_width, maze_height):
        super().__init__(x, y, maze_width, maze_height)
        self.scatter_target = (maze_width - 2, 1)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        return (pacman.x, pacman.y)


class PinkyGhost(GhostAgent):
    # rose — cible 4 cases devant pacman (embuscade)
    COLOR = (255, 184, 255)
    NAME = "Pinky"

    def __init__(self, x, y, maze_width, maze_height):
        super().__init__(x, y, maze_width, maze_height)
        self.scatter_target = (1, 1)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        tx = max(0, min(environment.width - 1, pacman.x + pacman.direction[0] * 4))
        ty = max(0, min(environment.height - 1, pacman.y + pacman.direction[1] * 4))
        return (tx, ty)


class InkyGhost(GhostAgent):
    # cyan — utilise la position de blinky + pacman (imprévisible)
    COLOR = (0, 255, 255)
    NAME = "Inky"

    def __init__(self, x, y, maze_width, maze_height):
        super().__init__(x, y, maze_width, maze_height)
        self.scatter_target = (maze_width - 2, maze_height - 2)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        blinky = None
        for g in ghosts:
            if isinstance(g, BlinkyGhost):
                blinky = g
                break
        if not blinky:
            return (pacman.x, pacman.y)
        ax = pacman.x + pacman.direction[0] * 2
        ay = pacman.y + pacman.direction[1] * 2
        tx = max(0, min(environment.width - 1, 2 * ax - blinky.x))
        ty = max(0, min(environment.height - 1, 2 * ay - blinky.y))
        return (tx, ty)


class ClydeGhost(GhostAgent):
    # orange — chasse quand loin, fuit quand proche (timide)
    COLOR = (255, 184, 82)
    NAME = "Clyde"

    def __init__(self, x, y, maze_width, maze_height):
        super().__init__(x, y, maze_width, maze_height)
        self.scatter_target = (1, maze_height - 2)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        dist = abs(self.x - pacman.x) + abs(self.y - pacman.y)
        if dist > 8:
            return (pacman.x, pacman.y)
        return self.scatter_target
