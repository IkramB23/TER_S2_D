"""cadre simple pour comparer les méthodes"""

import copy
import inspect
import random
from pathlib import Path

from game.agents import (
    Agent,
    BlinkyGhost,
    ClydeGhost,
    GhostAgent,
    GhostMode,
    InkyGhost,
    PinkyGhost,
)
from game.engine import GameEngine
from game.environment import Environment
from game.recorder import GameRecorder


class ReplayPacmanAgent(Agent):
    """pac-man qui rejoue un trajet déjà connu"""

    def __init__(self, route):
        if not route:
            raise ValueError("le trajet ne peut pas être vide")
        super().__init__(route[0][0], route[0][1])
        self.route = route
        self.route_index = 0

    def reset(self):
        super().reset()
        self.route_index = 0

    def get_action(self, environment, **context):
        if self.route_index >= len(self.route) - 1:
            return (0, 0)

        nx, ny = self.route[self.route_index + 1]
        dx, dy = nx - self.x, ny - self.y
        if abs(dx) + abs(dy) != 1:
            return (0, 0)
        if not environment.is_corridor(nx, ny):
            return (0, 0)

        self.route_index += 1
        return (dx, dy)


def generate_random_route(environment, start, steps=250, seed=0):
    """crée un trajet valide avec un hasard répétable"""
    rnd = random.Random(seed)
    x, y = start
    route = [(x, y)]
    direction = (0, 0)

    for _ in range(max(0, steps)):
        candidates = []
        reverse = (-direction[0], -direction[1])
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if environment.is_corridor(nx, ny):
                candidates.append((dx, dy))

        if not candidates:
            break

        non_reverse = [d for d in candidates if d != reverse]
        options = non_reverse if non_reverse else candidates
        direction = rnd.choice(options)
        x += direction[0]
        y += direction[1]
        route.append((x, y))

    return route


def _run_single_experiment(maze, pacman_route, ghost_specs, max_ticks=1200):
    env = Environment(copy.deepcopy(maze))
    # garder seulement la phase de chasse (pas de billes à manger)
    env.pellets.clear()
    env.power_pellets.clear()
    # mettre une fausse bille pour éviter une victoire immédiate
    env.pellets.add((-1, -1))

    pacman = ReplayPacmanAgent(pacman_route)
    ghosts = []
    for spec in ghost_specs:
        ghost_cls = spec.get("ghost_class", GhostAgent)
        spawn = spec.get("spawn")
        if spawn is None:
            spawn = env.find_ghost_spawns(1)[0]

        ctor_params = inspect.signature(ghost_cls.__init__).parameters
        kwargs = {
            "pathfinder": spec.get("pathfinder", "bfs"),
            "cooperative": spec.get("cooperative", False),
        }
        if "prediction_steps" in ctor_params:
            kwargs["prediction_steps"] = spec.get("prediction_steps", 0)

        ghosts.append(
            ghost_cls(
                spawn[0],
                spawn[1],
                env.width,
                env.height,
                **kwargs,
            )
        )

    engine = GameEngine(env, pacman, ghosts)
    engine.pacman_speed = 1
    engine.ghost_speed = 1
    engine.ghost_frightened_speed = 1

    # forcer les fantômes en mode chase (poursuite)
    engine.current_ghost_mode = GhostMode.CHASE
    engine.ghost_mode_timer = -1
    for ghost in engine.ghosts:
        ghost.mode = GhostMode.CHASE

    capture_tick = None
    start_lives = engine.lives

    for tick in range(max_ticks):
        engine.tick()
        if capture_tick is None and engine.lives < start_lives:
            capture_tick = tick + 1
        if engine.game_over:
            break
        if pacman.route_index >= len(pacman.route) - 1:
            break

    return {
        "captured": capture_tick is not None,
        "capture_tick": capture_tick,
        "ticks_played": engine.tick_count,
        "lives_left": engine.lives,
        "score": engine.score,
    }


def compare_day6_strategies(maze, route_steps=250, seed=0):
    """compare plusieurs méthodes sur le même trajet"""
    env = Environment(copy.deepcopy(maze))
    pacman_start = env.find_pacman_spawn()
    route = generate_random_route(env, pacman_start, steps=route_steps, seed=seed)
    team_spawns = env.find_ghost_spawns(4)
    ghost_spawn = team_spawns[0]

    team4_astar_coop = []
    for i in range(4):
        team4_astar_coop.append(
            {
                "spawn": team_spawns[i % len(team_spawns)],
                "pathfinder": "astar",
                "prediction_steps": 3,
                "cooperative": True,
            }
        )

    team4_roles_astar = [
        {
            "spawn": team_spawns[0 % len(team_spawns)],
            "ghost_class": BlinkyGhost,
            "pathfinder": "astar",
            "cooperative": False,
        },
        {
            "spawn": team_spawns[1 % len(team_spawns)],
            "ghost_class": PinkyGhost,
            "pathfinder": "astar",
            "cooperative": False,
        },
        {
            "spawn": team_spawns[2 % len(team_spawns)],
            "ghost_class": InkyGhost,
            "pathfinder": "astar",
            "cooperative": False,
        },
        {
            "spawn": team_spawns[3 % len(team_spawns)],
            "ghost_class": ClydeGhost,
            "pathfinder": "astar",
            "cooperative": False,
        },
    ]

    experiments = {
        "bfs_reactive": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "bfs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "astar_reactive": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "astar",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "dfs_reactive": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "dfs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "ucs_reactive": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "ucs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "mcts_reactive": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "mcts",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "bfs_predictive_k3": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "bfs",
                "prediction_steps": 3,
                "cooperative": False,
            }
        ],
        "astar_predictive_k3": [
            {
                "spawn": ghost_spawn,
                "pathfinder": "astar",
                "prediction_steps": 3,
                "cooperative": False,
            }
        ],
        "team4_bfs_coop": [
            {
                "spawn": team_spawns[i % len(team_spawns)],
                "pathfinder": "bfs",
                "prediction_steps": 2,
                "cooperative": True,
            }
            for i in range(4)
        ],
        "team4_astar_coop_k3": team4_astar_coop,
        "team4_astar_roles": team4_roles_astar,
    }

    results = {}
    for name, ghost_specs in experiments.items():
        results[name] = _run_single_experiment(
            maze=maze,
            pacman_route=route,
            ghost_specs=ghost_specs,
        )

    return {
        "seed": seed,
        "route_length": len(route),
        "results": results,
    }


def pacman_route_from_recording_frames(frames):
    """récupère le trajet de pac-man depuis un enregistrement"""
    route = []
    for frame in frames:
        pacman = frame.get("pacman", {})
        x = pacman.get("x")
        y = pacman.get("y")
        if x is None or y is None:
            continue
        pos = (x, y)
        if not route or route[-1] != pos:
            route.append(pos)
    return route


def _default_experiments_for_spawn(spawn):
    team_spawns = [spawn, spawn, spawn, spawn]
    return {
        "bfs_reactive": [
            {
                "spawn": spawn,
                "pathfinder": "bfs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "astar_reactive": [
            {
                "spawn": spawn,
                "pathfinder": "astar",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "dfs_reactive": [
            {
                "spawn": spawn,
                "pathfinder": "dfs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "ucs_reactive": [
            {
                "spawn": spawn,
                "pathfinder": "ucs",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "mcts_reactive": [
            {
                "spawn": spawn,
                "pathfinder": "mcts",
                "prediction_steps": 0,
                "cooperative": False,
            }
        ],
        "bfs_predictive_k3": [
            {
                "spawn": spawn,
                "pathfinder": "bfs",
                "prediction_steps": 3,
                "cooperative": False,
            }
        ],
        "astar_predictive_k3": [
            {
                "spawn": spawn,
                "pathfinder": "astar",
                "prediction_steps": 3,
                "cooperative": False,
            }
        ],
        "team4_bfs_coop": [
            {
                "spawn": team_spawns[i],
                "pathfinder": "bfs",
                "prediction_steps": 2,
                "cooperative": True,
            }
            for i in range(4)
        ],
        "team4_astar_coop_k3": [
            {
                "spawn": team_spawns[i],
                "pathfinder": "astar",
                "prediction_steps": 3,
                "cooperative": True,
            }
            for i in range(4)
        ],
        "team4_astar_roles": [
            {
                "spawn": team_spawns[0],
                "ghost_class": BlinkyGhost,
                "pathfinder": "astar",
                "cooperative": False,
            },
            {
                "spawn": team_spawns[1],
                "ghost_class": PinkyGhost,
                "pathfinder": "astar",
                "cooperative": False,
            },
            {
                "spawn": team_spawns[2],
                "ghost_class": InkyGhost,
                "pathfinder": "astar",
                "cooperative": False,
            },
            {
                "spawn": team_spawns[3],
                "ghost_class": ClydeGhost,
                "pathfinder": "astar",
                "cooperative": False,
            },
        ],
    }


def rank_strategy_results(results):
    """classe les méthodes selon la vitesse de capture"""
    items = list(results.items())

    def _key(item):
        _, metrics = item
        captured = metrics.get("captured", False)
        capture_tick = metrics.get("capture_tick")
        if capture_tick is None:
            capture_tick = float("inf")
        # on préfère les méthodes qui capturent, puis les plus rapides
        return (0 if captured else 1, capture_tick)

    return sorted(items, key=_key)


def compare_day6_strategies_on_recording(recording_path, max_ticks=1200):
    """compare les méthodes sur une partie enregistrée"""
    recorder = GameRecorder.load(recording_path)
    maze = recorder.metadata.get("maze")
    if not maze:
        raise ValueError("les données enregistrées ne contiennent pas le labyrinthe")

    route = pacman_route_from_recording_frames(recorder.frames)
    if len(route) < 2:
        raise ValueError("l'enregistrement ne contient pas assez de mouvements de pac-man")

    default_spawn = None
    first_frame = recorder.frames[0] if recorder.frames else {}
    ghosts = first_frame.get("ghosts", [])
    if ghosts:
        gx = ghosts[0].get("x")
        gy = ghosts[0].get("y")
        if gx is not None and gy is not None:
            default_spawn = (gx, gy)
    if default_spawn is None:
        env = Environment(copy.deepcopy(maze))
        default_spawn = env.find_ghost_spawns(1)[0]

    experiments = _default_experiments_for_spawn(default_spawn)

    results = {}
    for name, ghost_specs in experiments.items():
        results[name] = _run_single_experiment(
            maze=maze,
            pacman_route=route,
            ghost_specs=ghost_specs,
            max_ticks=max_ticks,
        )

    ranking = [name for name, _ in rank_strategy_results(results)]
    return {
        "recording": str(Path(recording_path)),
        "route_length": len(route),
        "results": results,
        "ranking": ranking,
    }


def summarize_strategy_runs(run_reports):
    """fait un résumé sur plusieurs seeds"""
    if not run_reports:
        return {}

    strategy_names = list(run_reports[0]["results"].keys())
    summary = {}

    for name in strategy_names:
        captures = 0
        capture_ticks = []
        ticks_played_total = 0

        for report in run_reports:
            metrics = report["results"][name]
            if metrics.get("captured"):
                captures += 1
            tick = metrics.get("capture_tick")
            if tick is not None:
                capture_ticks.append(tick)
            ticks_played_total += metrics.get("ticks_played", 0)

        total_runs = len(run_reports)
        summary[name] = {
            "runs": total_runs,
            "captures": captures,
            "capture_rate": captures / max(1, total_runs),
            "avg_capture_tick": (
                sum(capture_ticks) / len(capture_ticks)
                if capture_ticks
                else None
            ),
            "avg_ticks_played": ticks_played_total / max(1, total_runs),
        }

    ranking = sorted(
        summary.items(),
        key=lambda item: (
            -item[1]["capture_rate"],
            item[1]["avg_capture_tick"]
            if item[1]["avg_capture_tick"] is not None
            else float("inf"),
        ),
    )

    return {
        "strategies": summary,
        "ranking": [name for name, _ in ranking],
    }


def compare_strategies_over_seeds(
    maze,
    seeds,
    route_steps=250,
):
    """lance plusieurs essais et fait un résumé"""
    run_reports = []
    for seed in seeds:
        run_reports.append(
            compare_day6_strategies(
                maze=maze,
                route_steps=route_steps,
                seed=seed,
            )
        )

    aggregated = summarize_strategy_runs(run_reports)
    return {
        "seeds": list(seeds),
        "runs": run_reports,
        "summary": aggregated,
    }
