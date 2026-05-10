#!/usr/bin/env python3
"""
Script de benchmark IA vs Humain (Facile/Difficile)
Génère les données
"""

import json
import copy
import random
from pathlib import Path
from statistics import mean, stdev

from Proto.maze_Prim_loops import generate_pacman_maze
from game.environment import Environment
from game.agents import (
    BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost, 
    GhostMode, AIPacmanAgent, MinimaxPacmanAgent, ExpectimaxPacmanAgent
)
from game.engine import GameEngine
from game.recorder import GameRecorder
from game.framework import ReplayPacmanAgent, generate_random_route


# Configurations des niveaux
LEVEL_CONFIG = {
    "easy": {
        "label": "Facile (Humain)",
        "pathfinder": "bfs",
        "prediction_steps": 0,
        "ghost_speed": 14,
        "pacman_speed": 12,
        "frightened_duration": 600,
        "caged_ticks": 600,
    },
    "hard": {
        "label": "Difficile (Humain)",
        "pathfinder": "astar",
        "prediction_steps": 3,
        "ghost_speed": 6,
        "pacman_speed": 8,
        "frightened_duration": 200,
        "caged_ticks": 180,
    },
    "ai_easy": {
        "label": "IA Pac-Man (Facile)",
        "pacman_strategy": "astar",
        "pathfinder": "bfs",
        "prediction_steps": 0,
        "ghost_speed": 14,
        "pacman_speed": 12,
        "frightened_duration": 600,
        "caged_ticks": 600,
    },
    "ai_hard": {
        "label": "IA Pac-Man (Difficile)",
        "pacman_strategy": "astar",
        "pathfinder": "astar",
        "prediction_steps": 3,
        "ghost_speed": 6,
        "pacman_speed": 8,
        "frightened_duration": 200,
        "caged_ticks": 180,
    },
    "ai_minimax": {
        "label": "IA Minimax+AB (Difficile)",
        "pacman_strategy": "minimax",
        "depth": 0,
        "pathfinder": "astar",
        "prediction_steps": 3,
        "ghost_speed": 6,
        "pacman_speed": 8,
        "frightened_duration": 200,
        "caged_ticks": 180,
    },
    "ai_expectimax": {
        "label": "IA Expectimax (Difficile)",
        "pacman_strategy": "expectimax",
        "depth": 0,
        "pathfinder": "astar",
        "prediction_steps": 3,
        "ghost_speed": 6,
        "pacman_speed": 8,
        "frightened_duration": 200,
        "caged_ticks": 180,
    },
}


def load_real_human_data():
    """Charge les données des parties humaines réelles depuis les recordings."""
    import glob
    import os

    files = sorted(glob.glob("recordings/*.json"), key=os.path.getmtime, reverse=True)

    easy_games = []
    hard_games = []
    easy_mazes = []  # labyrinthes facile pour l'IA facile
    hard_mazes = []  # labyrinthes difficile pour l'IA difficile

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            meta   = data.get("metadata", {})
            frames = data.get("frames", [])
            agent  = meta.get("agent_type", "")

            # ignorer les replays et parties solo (garder uniquement les parties humaines normales)
            if agent not in ("human",):
                continue
            if not frames:
                continue

            score = meta.get("score_final")
            if score is None:
                score = frames[-1].get("score", 0)

            ticks = len(frames)

            # trouver le vrai tick de la première mort (première frame où lives diminue)
            capture_tick = None
            prev_lives = frames[0].get("lives", 3)
            for i, fr in enumerate(frames[1:], start=1):
                cur_lives = fr.get("lives", prev_lives)
                if cur_lives < prev_lives:
                    capture_tick = fr.get("tick", i)
                    break
                prev_lives = cur_lives

            captured = capture_tick is not None

            # pellets_eaten directement lisible depuis le moteur (stocké dans les frames)
            pellets = frames[-1].get("pellets_remaining", None)
            if pellets is not None:
                total = meta.get("width", 21) * meta.get("height", 21)  # approximation
                pellets_eaten = max(0, total - pellets)
            else:
                # fallback : compter uniquement les pellets normaux (10 pts chacun)
                pellets_eaten = sum(1 for fr in frames
                                    if fr.get("pellets_remaining", 999) <
                                    frames[max(0, frames.index(fr) - 1)].get("pellets_remaining", 999)
                                    ) if False else score // 10  # simple fallback

            game_data = {
                "capture_tick": capture_tick,
                "score": score,
                "pellets_eaten": pellets_eaten,
                "captured": captured,
                "ticks_played": ticks,
                "lives_left": frames[-1].get("lives", 0),
                "maze": meta.get("maze"),  # labyrinthe réel pour comparer avec l'IA
            }

            # classement par niveau stocké dans les métadonnées
            level = meta.get("level")
            if level == 1:
                easy_games.append(game_data)
                if meta.get("maze"):
                    easy_mazes.append(meta["maze"])
            elif level in (2, 3):
                hard_games.append(game_data)
                if meta.get("maze"):
                    hard_mazes.append(meta["maze"])
            else:
                # pas de niveau stocké : fallback sur le score
                if score >= 1000:
                    easy_games.append(game_data)
                    if meta.get("maze"):
                        easy_mazes.append(meta["maze"])
                else:
                    hard_games.append(game_data)
                    if meta.get("maze"):
                        hard_mazes.append(meta["maze"])

        except Exception:
            pass

    return {"easy": easy_games, "hard": hard_games,
            "easy_mazes": easy_mazes, "hard_mazes": hard_mazes}

def run_single_game_ai(maze, level_key="ai", max_ticks=1800):
    """Lance une partie uniquement pour la VRAIE configuration IA."""
    cfg = LEVEL_CONFIG[level_key]
    env = Environment(copy.deepcopy(maze))
    
    # Créer le Pac-Man IA
    pac_pos = env.find_pacman_spawn()
    pac_strategy = cfg.get("pacman_strategy", "astar")
    depth = cfg.get("depth", 2)
    if pac_strategy == "minimax":
        pacman = MinimaxPacmanAgent(pac_pos[0], pac_pos[1], depth=depth)
    elif pac_strategy == "expectimax":
        pacman = ExpectimaxPacmanAgent(pac_pos[0], pac_pos[1], depth=depth)
    else:
        pacman = AIPacmanAgent(pac_pos[0], pac_pos[1], strategy=pac_strategy)
    
    # Créer fantômes
    ghost_spawns = env.find_ghost_spawns(4)
    w, h = env.width, env.height
    ghost_classes = [BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost]
    ghosts = []
    for i, cls in enumerate(ghost_classes):
        gx, gy = ghost_spawns[i] if i < len(ghost_spawns) else ghost_spawns[0]
        if cls == BlinkyGhost:
            ghosts.append(cls(gx, gy, w, h,
                pathfinder=cfg["pathfinder"],
                prediction_steps=cfg.get("prediction_steps", 0)))
        else:
            ghosts.append(cls(gx, gy, w, h,
                pathfinder=cfg["pathfinder"]))
    
    # Créer moteur
    engine = GameEngine(env, pacman, ghosts)
    engine.pacman_speed = cfg["pacman_speed"]
    engine.ghost_speed = cfg["ghost_speed"]
    engine.ghost_frightened_speed = 12
    engine.frightened_duration = cfg.get("frightened_duration", 360)
    engine.ghost_mode_timer = cfg.get("caged_ticks", 420)
    
    # Lancer la partie
    capture_tick = None
    prev_lives = engine.lives

    for tick in range(max_ticks):
        engine.tick()

        # détecter la première mort (première fois que lives diminue)
        if capture_tick is None and engine.lives < prev_lives:
            capture_tick = engine.tick_count
        prev_lives = engine.lives

        # fin de partie
        if engine.game_over or engine.game_won:
            break
    
    return {
        "capture_tick": capture_tick,
        "score": engine.score,
        "pellets_eaten": engine.pellets_eaten,
        "captured": capture_tick is not None,
        "ticks_played": engine.tick_count,
        "lives_left": engine.lives,
    }


def _run_ia_level(results, level_key, mazes, num_games, maze_size):
    """Lance num_games parties IA pour un niveau donné (level_key = 'ai_easy' ou 'ai_hard')."""
    cfg = LEVEL_CONFIG[level_key]
    results[level_key] = []
    print(f"\ntest {cfg['label']} ({num_games} parties)")

    for game_num in range(1, num_games + 1):
        if mazes:
            maze = mazes[(game_num - 1) % len(mazes)]
        else:
            maze = generate_pacman_maze(maze_size, maze_size, loop_percent=25)

        result = run_single_game_ai(maze, level_key=level_key)
        results[level_key].append(result)

        status = "capture" if result["captured"] else "pas capture"
        tick_str = str(result['capture_tick']) if result['capture_tick'] else 'N/A'
        print(f"  [{game_num:2d}/{num_games}] {status} | tick: {tick_str:>4} | score: {result['score']:5} | pellets: {result['pellets_eaten']:3}")


def run_benchmark(num_games=20, maze_size=21):
    """Lance le benchmark complet.

    Pour chaque niveau (Facile / Difficile) l'IA joue avec exactement les mêmes
    paramètres que les humains (même vitesse fantômes, même durée frightened, etc.).
    Retourne un dict avec les résultats pour chaque config.
    """
    print(f"\n{'='*60}")
    print(f"benchmark: IA vs Vraies parties Humaines")
    print(f"parties IA par niveau : {num_games}")
    print(f"{'='*60}\n")

    # 1. Charger les stats humaines
    print("analyse des parties humaines enregistrées...")
    results = load_real_human_data()
    print(f"  trouvé {len(results['easy'])} parties (niveau facile, débutant)")
    print(f"  trouvé {len(results['hard'])} parties (niveau difficile, expert)")
    print(f"  labyrinthes facile : {len(results['easy_mazes'])} | difficile : {len(results['hard_mazes'])}")

    # 2. IA facile (mêmes params que humains facile)
    _run_ia_level(results, "ai_easy", results["easy_mazes"], num_games, maze_size)

    # 3. IA difficile A* (mêmes params que humains difficile)
    _run_ia_level(results, "ai_hard", results["hard_mazes"], num_games, maze_size)

    # 4. IA Minimax+Alpha-Beta (params difficile)
    _run_ia_level(results, "ai_minimax", results["hard_mazes"], num_games, maze_size)

    # 5. IA Expectimax (params difficile)
    _run_ia_level(results, "ai_expectimax", results["hard_mazes"], num_games, maze_size)

    return results


def save_results_json(stats, filepath=None):
    """Sauvegarde les résultats du benchmark dans un fichier JSON horodaté."""
    from datetime import datetime
    if filepath is None:
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"benchmark_results_{date_str}.json"

    output = {
        "generated_at": datetime.now().isoformat(),
        "results": stats,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nrésultats sauvegardés dans : {filepath}")
    return filepath


def compute_stats(results):
    """Calcule les statistiques pour chaque niveau"""
    stats = {}

    INTERNAL_KEYS = {"easy_mazes", "hard_mazes"}
    for level_key, games in results.items():
        if level_key in INTERNAL_KEYS:   # clés internes, pas des niveaux
            continue
        cfg = LEVEL_CONFIG[level_key]
        
        # Filtrer les parties capturées pour les stats de ticks
        capture_ticks = [g["capture_tick"] for g in games if g["captured"] and g["capture_tick"] is not None]
        scores = [g["score"] for g in games]
        pellets = [g["pellets_eaten"] for g in games]
        
        capture_rate = sum(1 for g in games if g["captured"]) / len(games) * 100

        stats[level_key] = {
            "label": cfg["label"],
            "total_games": len(games),
            "capture_rate": round(capture_rate, 1),
            "avg_capture_tick": round(mean(capture_ticks), 1) if capture_ticks else None,
            "min_capture_tick": min(capture_ticks) if capture_ticks else None,
            "max_capture_tick": max(capture_ticks) if capture_ticks else None,
            "std_capture_tick": round(stdev(capture_ticks), 1) if len(capture_ticks) > 1 else None,
            "avg_score": round(mean(scores), 1),
            "min_score": min(scores),
            "max_score": max(scores),
            "std_score": round(stdev(scores), 1) if len(scores) > 1 else None,
            "avg_pellets": round(mean(pellets), 1),
            "min_pellets": min(pellets),
            "max_pellets": max(pellets),
        }
    
    return stats


def main():
    """Fonction principale."""
    import sys
    
    # Nombre de parties IA par niveau (argument optionnel, défaut 20)
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    print("\n--- debut du benchmark ---")

    # lancer le benchmark
    results = run_benchmark(num_games=num_games, maze_size=21)

    # calculer les stats
    stats = compute_stats(results)

    # afficher le tableau récapitulatif (4 lignes : humain/IA × facile/difficile)
    print("\n--- resultats finaux ---")
    print(f"{'- niveau -':<26} | {'parties':>7} | {'capture':>8} | {'avg ticks':>9} | {'std ticks':>9} | {'avg score':>9} | {'std score':>9}")
    print("-" * 95)

    row_order = [
        ("easy",          "humain facile"),
        ("ai_easy",       "ia facile (A*)"),
        ("hard",          "humain difficile"),
        ("ai_hard",       "ia difficile (A*)"),
        ("ai_minimax",    "ia minimax+ab"),
        ("ai_expectimax", "ia expectimax"),
    ]
    for k, label in row_order:
        if k not in stats or stats[k]["total_games"] == 0:
            continue
        s = stats[k]
        tick_str  = f"{s['avg_capture_tick']:.0f}"  if s['avg_capture_tick']  is not None else "N/A"
        std_t_str = f"{s['std_capture_tick']:.0f}"  if s['std_capture_tick']  is not None else "N/A"
        std_s_str = f"{s['std_score']:.0f}"          if s['std_score']         is not None else "N/A"
        print(f"{label:<26} | {s['total_games']:>7} | {s['capture_rate']:>7.1f}% | {tick_str:>9} | {std_t_str:>9} | {s['avg_score']:>9.0f} | {std_s_str:>9}")

    print("-" * 95)

    # exporter en JSON pour le rapport
    save_results_json(stats)
    


if __name__ == "__main__":
    main()