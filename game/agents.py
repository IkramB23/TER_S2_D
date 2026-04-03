# agents — pacman (humain / futur IA) et fantômes (chacun avec une IA différente)

from abc import ABC, abstractmethod
from collections import deque
import heapq
import random


class GhostMode:
    CAGED = "caged"
    SCATTER = "scatter"
    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


# --- recherche de chemin ---

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def bfs_direction(walls, width, height, start, target):
    # bfs : donne (dx, dy) du premier pas vers la cible
    if start == target:
        return (0, 0)

    visited = {start}
    queue = deque([(start, None)])  # (position, première direction)

    while queue:
        (x, y), first_dir = queue.popleft()
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in visited and (nx, ny) not in walls):
                direction = first_dir if first_dir else (dx, dy)
                if (nx, ny) == target:
                    return direction
                visited.add((nx, ny))
                queue.append(((nx, ny), direction))

    return (0, 0)


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_direction(walls, width, height, start, target):
    # a* : donne (dx, dy) du premier pas vers la cible
    if start == target:
        return (0, 0)

    best_g = {start: 0}
    # (f, g, x, y, first_dir)
    heap = [(_manhattan(start, target), 0, start[0], start[1], None)]

    while heap:
        _, g, x, y, first_dir = heapq.heappop(heap)
        current = (x, y)
        if current == target:
            return first_dir if first_dir else (0, 0)
        if g > best_g.get(current, float("inf")):
            continue

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in walls:
                continue

            ng = g + 1
            neighbor = (nx, ny)
            if ng >= best_g.get(neighbor, float("inf")):
                continue

            best_g[neighbor] = ng
            direction = first_dir if first_dir else (dx, dy)
            nf = ng + _manhattan(neighbor, target)
            heapq.heappush(heap, (nf, ng, nx, ny, direction))

    return (0, 0)


def predict_pacman_position(environment, pacman, steps=3):
    # simple projection de la position future de pac-man
    x, y = pacman.x, pacman.y
    dx, dy = pacman.direction
    if (dx, dy) == (0, 0):
        return (x, y)

    for _ in range(max(0, steps)):
        nx, ny = x + dx, y + dy
        if not environment.is_corridor(nx, ny):
            break
        x, y = nx, ny

    return (x, y)


# --- classe de base des agents ---

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


# --- agent pac-man ---

class HumanAgent(Agent):
    # pac-man contrôlé par le clavier

    def __init__(self, x, y):
        super().__init__(x, y)
        self.next_direction = (0, 0)

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def get_action(self, environment, **context):
        # essaie la direction demandée
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
    # fantôme de base avec ia, chaque sous-classe définit sa cible

    COLOR = (255, 0, 0)
    NAME = "Ghost"

    def __init__(
        self,
        x,
        y,
        maze_width,
        maze_height,
        pathfinder="bfs",
        prediction_steps=0,
        cooperative=False,
    ):
        super().__init__(x, y)
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.mode = GhostMode.SCATTER
        self.frightened_timer = 0
        self.scatter_target = (0, 0)
        self.pathfinder = pathfinder
        self.prediction_steps = prediction_steps
        self.cooperative = cooperative

    def get_target(self, environment, pacman, ghosts):
        # à redéfinir dans chaque sous-classe
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target

        if self.prediction_steps > 0:
            tx, ty = predict_pacman_position(
                environment, pacman, steps=self.prediction_steps
            )
        else:
            tx, ty = pacman.x, pacman.y

        if self.cooperative and ghosts:
            try:
                idx = ghosts.index(self)
            except ValueError:
                idx = 0
            offsets = [(0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)]
            ox, oy = offsets[idx % len(offsets)]
            tx += ox
            ty += oy

        tx = max(0, min(environment.width - 1, tx))
        ty = max(0, min(environment.height - 1, ty))
        return (tx, ty)

    def _pathfind_direction(self, environment, start, target):
        pathfinder = (self.pathfinder or "bfs").lower()
        if pathfinder == "astar":
            return astar_direction(
                environment.walls,
                environment.width,
                environment.height,
                start,
                target,
            )
        return bfs_direction(
            environment.walls,
            environment.width,
            environment.height,
            start,
            target,
        )

    def get_action(self, environment, **context):
        pacman = context.get("pacman")
        ghosts = context.get("ghosts", [])

        if self.mode == GhostMode.CAGED:
            # les fantômes en cage ne bougent pas
            return (0, 0)

        if self.mode == GhostMode.FRIGHTENED:
            return self._random_direction(environment)

        if self.mode == GhostMode.EATEN:
            # retour au point de départ
            return self._pathfind_direction(
                environment,
                (self.x, self.y),
                (self.start_x, self.start_y),
            )

        target = self.get_target(environment, pacman, ghosts)
        return self._pathfind_direction(
            environment,
            (self.x, self.y),
            target,
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
        # passe en mode effrayé (quand pac-man mange une grosse bille)
        if self.mode != GhostMode.EATEN:
            self.mode = GhostMode.FRIGHTENED
            self.frightened_timer = duration

    def update_mode(self, global_mode):
        # se cale sur le mode global (cycle scatter/chase)
        if self.mode == GhostMode.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = global_mode
        elif self.mode == GhostMode.EATEN:
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.mode = global_mode
        elif self.mode == GhostMode.CAGED:
            # reste en cage jusqu'à que global_mode change (fin de la phase CAGED)
            if global_mode != GhostMode.CAGED:
                self.mode = global_mode
        else:
            self.mode = global_mode


class BlinkyGhost(GhostAgent):
    # rouge : cible directement la position de pacman (chasseur)
    COLOR = (255, 0, 0)
    NAME = "Blinky"

    def __init__(
        self,
        x,
        y,
        maze_width,
        maze_height,
        pathfinder="bfs",
        prediction_steps=0,
        cooperative=False,
    ):
        super().__init__(
            x,
            y,
            maze_width,
            maze_height,
            pathfinder=pathfinder,
            prediction_steps=prediction_steps,
            cooperative=cooperative,
        )
        self.scatter_target = (maze_width - 2, 1)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        return (pacman.x, pacman.y)


class PinkyGhost(GhostAgent):
    # rose : cible 4 cases devant pacman (embuscade)
    COLOR = (255, 184, 255)
    NAME = "Pinky"

    def __init__(
        self,
        x,
        y,
        maze_width,
        maze_height,
        pathfinder="bfs",
        cooperative=False,
    ):
        super().__init__(
            x,
            y,
            maze_width,
            maze_height,
            pathfinder=pathfinder,
            prediction_steps=0,
            cooperative=cooperative,
        )
        self.scatter_target = (1, 1)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        tx = max(0, min(environment.width - 1, pacman.x + pacman.direction[0] * 4))
        ty = max(0, min(environment.height - 1, pacman.y + pacman.direction[1] * 4))
        return (tx, ty)


class InkyGhost(GhostAgent):
    # cyan : utilise la position de blinky + pacman (imprévisible)
    COLOR = (0, 255, 255)
    NAME = "Inky"

    def __init__(
        self,
        x,
        y,
        maze_width,
        maze_height,
        pathfinder="bfs",
        cooperative=False,
    ):
        super().__init__(
            x,
            y,
            maze_width,
            maze_height,
            pathfinder=pathfinder,
            prediction_steps=0,
            cooperative=cooperative,
        )
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
    # orange : chasse quand loin, fuit quand proche (timide)
    COLOR = (255, 184, 82)
    NAME = "Clyde"

    def __init__(
        self,
        x,
        y,
        maze_width,
        maze_height,
        pathfinder="bfs",
        cooperative=False,
    ):
        super().__init__(
            x,
            y,
            maze_width,
            maze_height,
            pathfinder=pathfinder,
            prediction_steps=0,
            cooperative=cooperative,
        )
        self.scatter_target = (1, maze_height - 2)

    def get_target(self, environment, pacman, ghosts):
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target
        dist = abs(self.x - pacman.x) + abs(self.y - pacman.y)
        if dist > 8:
            return (pacman.x, pacman.y)
        return self.scatter_target
