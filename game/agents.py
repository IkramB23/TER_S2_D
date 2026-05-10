# agents - pac-man (humain / futur ia) et fantomes (chacun avec une ia differente)

from abc import ABC, abstractmethod
from collections import deque
import heapq
import math
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
    # bfs: donne (dx, dy) du premier pas vers la cible
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
    # a*: donne (dx, dy) du premier pas vers la cible
    if start == target:
        return (0, 0)

    best_g = {start: 0}
    # (f=cout_total, g=cout_reel, x, y, first_dir)
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


def dfs_direction(walls, width, height, start, target):
    # dfs : parcours en profondeur, donne le premier pas vers la cible
    if start == target:
        return (0, 0)

    visited = {start}
    stack = [(start, None)]

    while stack:
        (x, y), first_dir = stack.pop()
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in visited and (nx, ny) not in walls):
                direction = first_dir if first_dir else (dx, dy)
                if (nx, ny) == target:
                    return direction
                visited.add((nx, ny))
                stack.append(((nx, ny), direction))

    return (0, 0)


def ucs_direction(walls, width, height, start, target):
    # ucs (uniform cost search) : cherche le chemin de coût minimal (dijkstra)
    if start == target:
        return (0, 0)

    best_g = {start: 0}
    heap = [(0, start[0], start[1], None)]

    while heap:
        g, x, y, first_dir = heapq.heappop(heap)
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
            heapq.heappush(heap, (ng, nx, ny, direction))

    return (0, 0)


def mcts_direction(walls, width, height, start, target, simulations=80):
    # monte carlo tree search : simule des chemins aléatoires pour choisir le meilleur premier pas
    if start == target:
        return (0, 0)

    first_moves = {}
    for dx, dy in DIRECTIONS:
        nx, ny = start[0] + dx, start[1] + dy
        if (0 <= nx < width and 0 <= ny < height
                and (nx, ny) not in walls):
            first_moves[(dx, dy)] = {"visits": 0, "total_score": 0.0}

    if not first_moves:
        return (0, 0)

    max_depth = width + height

    for _ in range(simulations):
        move = random.choice(list(first_moves.keys()))
        x, y = start[0] + move[0], start[1] + move[1]
        visited = {start, (x, y)}

        for depth in range(1, max_depth):
            if (x, y) == target:
                break
            neighbors = []
            for ddx, ddy in DIRECTIONS:
                nnx, nny = x + ddx, y + ddy
                if (0 <= nnx < width and 0 <= nny < height
                        and (nnx, nny) not in walls and (nnx, nny) not in visited):
                    neighbors.append((nnx, nny))
            if not neighbors:
                break
            x, y = random.choice(neighbors)
            visited.add((x, y))

        dist = _manhattan((x, y), target)
        score = 1.0 / (1.0 + dist)
        first_moves[move]["visits"] += 1
        first_moves[move]["total_score"] += score

    best_move = (0, 0)
    best_avg = -1.0
    for move, stats in first_moves.items():
        if stats["visits"] > 0:
            avg = stats["total_score"] / stats["visits"]
            if avg > best_avg:
                best_avg = avg
                best_move = move

    return best_move


def predict_pacman_position(environment, pacman, steps=3):
    # projection simple de la position future de pac-man en k pas
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


# --- helpers pour la recherche adversariale ---

def _get_valid_moves(pos, walls, width, height):
    """Retourne les directions valides depuis pos (sans franchir un mur)."""
    x, y = pos
    moves = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
            moves.append((dx, dy))
    return moves if moves else [(0, 0)]


def _eval_heuristic(pac_pos, ghost_states, env):
    """Fonction d'évaluation partagée par Minimax et Expectimax.

    ghost_states : liste de (x, y, mode, frightened_timer)
    Retourne un score flottant (plus élevé = meilleur pour Pac-Man).
    """
    score = 0.0

    # 1. Proximité à la pastille la plus proche (manhattan)
    all_pellets = env.pellets | env.power_pellets
    if all_pellets:
        min_dist = min(_manhattan(pac_pos, p) for p in all_pellets)
        score += 200.0 / (1.0 + min_dist)
    else:
        score += 500.0  # presque en victoire

    # 2. Pénalité pour les fantômes actifs proches
    for gx, gy, gmode, _ in ghost_states:
        if gmode not in (GhostMode.FRIGHTENED, GhostMode.CAGED, GhostMode.EATEN):
            dist = max(1, _manhattan(pac_pos, (gx, gy)))
            if dist <= 2:
                score -= 1000.0 / dist
            elif dist <= 5:
                score -= 150.0 / dist

    # 3. Bonus pour chasser les fantômes effrayés
    for gx, gy, gmode, gtimer in ghost_states:
        if gmode == GhostMode.FRIGHTENED and gtimer > 0:
            dist = max(1, _manhattan(pac_pos, (gx, gy)))
            score += 300.0 / dist

    # 4. Récompense proportionnelle aux pastilles déjà mangées
    remaining = len(env.pellets) + len(env.power_pellets)
    score += (env.total_pellets - remaining) * 10.0

    return score


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
        # remet l'agent à sa position de départ en réinitialisant
        self.x = self.start_x
        self.y = self.start_y
        self.direction = (0, 0)


# --- agent pac-man ---

class HumanAgent(Agent):
    # pac-man contrôlé par le clavier du joueur

    def __init__(self, x, y):
        super().__init__(x, y)
        self.next_direction = (0, 0)

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def get_action(self, environment, **context):
        # essaie d'aller dans la direction demandée par le joueur
        nx = self.x + self.next_direction[0]
        ny = self.y + self.next_direction[1]
        if self.next_direction != (0, 0) and environment.is_corridor(nx, ny):
            self.direction = self.next_direction
            return self.direction

        # sinon continue dans la direction actuelle si c'est possible
        nx = self.x + self.direction[0]
        ny = self.y + self.direction[1]
        if environment.is_corridor(nx, ny):
            return self.direction

        return (0, 0)


# --- agent pac-man ia ---

class AIPacmanAgent(Agent):
    """Pac-Man contrôlé par un algorithme de recherche de chemin.

    Stratégies disponibles :
      - "bfs"   : BFS vers la pastille la plus proche (optimal, sûr)
      - "astar" : A* vers la pastille la plus proche (plus efficace sur grands labyrinthes)
      - "avoid" : BFS mais ignore les cellules adjacentes aux fantômes
    """

    def __init__(self, x, y, strategy="bfs"):
        super().__init__(x, y)
        self.strategy = strategy
        # cache pour éviter de recalculer la cible à chaque tick
        self._target = None

    def get_action(self, environment, **context):
        ghosts = context.get("ghosts", [])
        walls = environment.walls

        # construire l'ensemble des cases dangereuses (fantômes non-effrayés à 1 case)
        if self.strategy == "avoid" and ghosts:
            danger = set()
            for g in ghosts:
                if not getattr(g, "frightened_timer", 0):
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        danger.add((g.x + dx, g.y + dy))
        else:
            danger = set()

        # trouver la pastille (pellet) la plus proche via BFS (ignore les cases dangereuses)
        target = self._find_nearest_pellet(environment, danger)
        if target is None:
            # aucune pastille restante : rester sur place
            return (0, 0)

        # choisir la direction vers la cible
        if self.strategy == "astar":
            direction = astar_direction(
                walls, environment.width, environment.height,
                (self.x, self.y), target
            )
        else:
            # bfs ou avoid : même primitive BFS
            direction = bfs_direction(
                walls, environment.width, environment.height,
                (self.x, self.y), target
            )

        if direction is not None:
            self.direction = direction
            return direction

        # si le chemin est bloqué, essayer d'avancer dans la direction actuelle
        nx, ny = self.x + self.direction[0], self.y + self.direction[1]
        if self.direction != (0, 0) and environment.is_corridor(nx, ny):
            return self.direction

        return (0, 0)

    def _find_nearest_pellet(self, environment, danger):
        """BFS depuis la position actuelle vers la case avec une pastille."""
        from collections import deque
        start = (self.x, self.y)
        if not environment.pellets and not environment.power_pellets:
            return None

        all_pellets = set(environment.pellets) | set(environment.power_pellets)
        visited = {start}
        queue = deque([start])

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in all_pellets:
                return (cx, cy)
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                pos = (nx, ny)
                if pos in visited:
                    continue
                if not environment.is_corridor(nx, ny):
                    continue
                if pos in danger:
                    continue
                visited.add(pos)
                queue.append(pos)

        # si toutes les cases sans danger sont épuisées, essayer sans restriction
        if danger:
            return self._find_nearest_pellet(environment, set())
        return None


# --- agent pac-man ia : minimax avec élagage alpha-beta ---

class MinimaxPacmanAgent(Agent):
    """Pac-Man contrôlé par l'algorithme Minimax avec élagage Alpha-Beta.

    Pac-Man est le joueur MAX.
    Chaque fantôme non-effrayé est un joueur MIN (adversaire parfait).
    L'élagage alpha-beta évite d'explorer les branches inutiles.

    Paramètre depth (défaut 0) :
      depth=0 → Pac-Man regarde 1 round de décision en avant
                 (1 coup Pac + tous les fantômes une fois via alpha-beta) ~ 27–243 évaluations.
      depth=1 → 2 rounds de décision → peut être lent selon l'élagage.
    """

    def __init__(self, x, y, depth=0):
        super().__init__(x, y)
        self.depth = max(0, depth)

    def get_action(self, environment, **context):
        ghosts = context.get("ghosts", [])
        pac_pos = (self.x, self.y)
        ghost_states = [
            (g.x, g.y, g.mode, getattr(g, "frightened_timer", 0))
            for g in ghosts
        ]

        best_val = float("-inf")
        best_dir = (0, 0)
        alpha = float("-inf")
        beta = float("inf")

        for dx, dy in _get_valid_moves(
            pac_pos, environment.walls, environment.width, environment.height
        ):
            nx, ny = pac_pos[0] + dx, pac_pos[1] + dy
            # Évalue cette position en commençant par le tour des fantômes
            val = self._alphabeta(
                (nx, ny), ghost_states, self.depth, 1, alpha, beta, environment
            )
            if val > best_val:
                best_val = val
                best_dir = (dx, dy)
            alpha = max(alpha, val)

        if best_dir != (0, 0):
            self.direction = best_dir
        return best_dir

    def _alphabeta(self, pac_pos, ghost_states, depth, agent_idx, alpha, beta, env):
        """Minimax récursif avec élagage Alpha-Beta.

        agent_idx = 0 → Pac-Man (MAX)
        agent_idx = 1..n → fantôme k (MIN)
        depth → nombre de tours de Pac-Man restants à explorer.
        """
        num_ghosts = len(ghost_states)

        # Détection d'une capture (état terminal immédiat)
        for gx, gy, gmode, _ in ghost_states:
            if (gx, gy) == pac_pos and gmode not in (
                GhostMode.FRIGHTENED, GhostMode.CAGED, GhostMode.EATEN
            ):
                return -99999

        # ---- Tour de Pac-Man (MAX) ----
        if agent_idx == 0:
            if depth == 0:
                return _eval_heuristic(pac_pos, ghost_states, env)
            best = float("-inf")
            for dx, dy in _get_valid_moves(
                pac_pos, env.walls, env.width, env.height
            ):
                nx, ny = pac_pos[0] + dx, pac_pos[1] + dy
                val = self._alphabeta(
                    (nx, ny), ghost_states, depth - 1, 1, alpha, beta, env
                )
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break  # élagage bêta
            return best

        # ---- Tour d'un fantôme (MIN) ----
        g_idx = agent_idx - 1
        gx, gy, gmode, gtimer = ghost_states[g_idx]
        next_agent = 0 if agent_idx == num_ghosts else agent_idx + 1

        # Fantôme inactif : passer son tour sans changer l'état
        if gmode in (GhostMode.FRIGHTENED, GhostMode.CAGED, GhostMode.EATEN):
            return self._alphabeta(
                pac_pos, ghost_states, depth, next_agent, alpha, beta, env
            )

        moves = _get_valid_moves((gx, gy), env.walls, env.width, env.height)
        best = float("inf")
        for dx, dy in moves:
            ngx, ngy = gx + dx, gy + dy
            new_gs = list(ghost_states)
            new_gs[g_idx] = (ngx, ngy, gmode, gtimer)
            val = self._alphabeta(
                pac_pos, new_gs, depth, next_agent, alpha, beta, env
            )
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break  # élagage alpha
        return best


# --- agent pac-man ia : expectimax ---

class ExpectimaxPacmanAgent(Agent):
    """Pac-Man contrôlé par l'algorithme Expectimax.

    Pac-Man est le joueur MAX.
    Les fantômes sont des nœuds CHANCE (distribution uniforme sur leurs
    mouvements valides) — modèle plus réaliste que Minimax car les fantômes
    ne jouent pas de façon parfaitement adversariale.

    Paramètre depth (défaut 0) :
      depth=0 → 1 round (1 coup Pac + 4 fantômes en chance node) ~ 243 éval. (RAPIDE)
      depth=1 → très lent en Python pur (pas d'élagage comme Alpha-Beta).
    """

    def __init__(self, x, y, depth=0):
        super().__init__(x, y)
        self.depth = max(0, depth)

    def get_action(self, environment, **context):
        ghosts = context.get("ghosts", [])
        pac_pos = (self.x, self.y)
        ghost_states = [
            (g.x, g.y, g.mode, getattr(g, "frightened_timer", 0))
            for g in ghosts
        ]

        best_val = float("-inf")
        best_dir = (0, 0)

        for dx, dy in _get_valid_moves(
            pac_pos, environment.walls, environment.width, environment.height
        ):
            nx, ny = pac_pos[0] + dx, pac_pos[1] + dy
            val = self._expectimax((nx, ny), ghost_states, self.depth, 1, environment)
            if val > best_val:
                best_val = val
                best_dir = (dx, dy)

        if best_dir != (0, 0):
            self.direction = best_dir
        return best_dir

    def _expectimax(self, pac_pos, ghost_states, depth, agent_idx, env):
        """Expectimax récursif.

        agent_idx = 0 → Pac-Man (MAX)
        agent_idx = 1..n → fantôme k (CHANCE : moyenne des successeurs)
        """
        num_ghosts = len(ghost_states)

        # Détection d'une capture
        for gx, gy, gmode, _ in ghost_states:
            if (gx, gy) == pac_pos and gmode not in (
                GhostMode.FRIGHTENED, GhostMode.CAGED, GhostMode.EATEN
            ):
                return -99999

        # ---- Tour de Pac-Man (MAX) ----
        if agent_idx == 0:
            if depth == 0:
                return _eval_heuristic(pac_pos, ghost_states, env)
            best = float("-inf")
            for dx, dy in _get_valid_moves(
                pac_pos, env.walls, env.width, env.height
            ):
                nx, ny = pac_pos[0] + dx, pac_pos[1] + dy
                val = self._expectimax(
                    (nx, ny), ghost_states, depth - 1, 1, env
                )
                best = max(best, val)
            return best

        # ---- Tour d'un fantôme (CHANCE) ----
        g_idx = agent_idx - 1
        gx, gy, gmode, gtimer = ghost_states[g_idx]
        next_agent = 0 if agent_idx == num_ghosts else agent_idx + 1

        # Fantôme inactif : passer son tour
        if gmode in (GhostMode.FRIGHTENED, GhostMode.CAGED, GhostMode.EATEN):
            return self._expectimax(pac_pos, ghost_states, depth, next_agent, env)

        moves = _get_valid_moves((gx, gy), env.walls, env.width, env.height)
        total = 0.0
        for dx, dy in moves:
            ngx, ngy = gx + dx, gy + dy
            new_gs = list(ghost_states)
            new_gs[g_idx] = (ngx, ngy, gmode, gtimer)
            total += self._expectimax(pac_pos, new_gs, depth, next_agent, env)
        # Espérance : moyenne uniforme sur les mouvements valides
        return total / len(moves)


# --- agents fantômes ---

class GhostAgent(Agent):
    # fantôme de base avec ia; chaque sous-classe redéfinit sa cible

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
        # redéfinir cette méthode dans les sous-classes pour des comportements spécifiques
        if self.mode == GhostMode.SCATTER:
            return self.scatter_target

        # prédit la position future de pac-man si activé
        if self.prediction_steps > 0:
            tx, ty = predict_pacman_position(
                environment, pacman, steps=self.prediction_steps
            )
        else:
            tx, ty = pacman.x, pacman.y

        # mode coopératif: décale la cible pour éviter que les fantômes se rassemblent
        if self.cooperative and ghosts:
            try:
                idx = ghosts.index(self)
            except ValueError:
                idx = 0
            offsets = [(0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)]
            ox, oy = offsets[idx % len(offsets)]
            tx += ox
            ty += oy

        # clamp la cible pour qu'elle reste dans le labyrinthe
        tx = max(0, min(environment.width - 1, tx))
        ty = max(0, min(environment.height - 1, ty))
        return (tx, ty)

    def _pathfind_direction(self, environment, start, target):
        pathfinder = (self.pathfinder or "bfs").lower()
        args = (environment.walls, environment.width, environment.height, start, target)
        if pathfinder == "astar":
            return astar_direction(*args)
        if pathfinder == "dfs":
            return dfs_direction(*args)
        if pathfinder == "ucs":
            return ucs_direction(*args)
        if pathfinder == "mcts":
            return mcts_direction(*args)
        return bfs_direction(*args)

    def get_action(self, environment, **context):
        pacman = context.get("pacman")
        ghosts = context.get("ghosts", [])

        if self.mode == GhostMode.CAGED:
            # en cage: ne pas bouger
            return (0, 0)

        if self.mode == GhostMode.FRIGHTENED:
            # en mode effrayé: mouvement aléatoire
            return self._random_direction(environment)

        if self.mode == GhostMode.EATEN:
            # retour au point de départ quand mangé
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
        # passer en mode effrayé (quand pac-man mange une grosse bille)
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
            # dés qu'au spawn: revenir au mode global
            if (self.x, self.y) == (self.start_x, self.start_y):
                self.mode = global_mode
        elif self.mode == GhostMode.CAGED:
            # sortir de la cage quand le mode global change
            if global_mode != GhostMode.CAGED:
                self.mode = global_mode
        else:
            self.mode = global_mode


class BlinkyGhost(GhostAgent):
    # rouge: cible directement pac-man (chasseur agressif)
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
    # rose: cible 4 cases devant pac-man (embuscade)
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
    # cyan: utilise la position de blinky + pac-man (imprévisible)
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
    # orange: chasse quand loin, se retire quand proche (timide)
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
