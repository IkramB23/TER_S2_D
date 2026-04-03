"""lanceur simple pour comparer les méthodes"""

import argparse
from pprint import pprint

from Proto.maze_Prim_loops import generate_pacman_maze
from game.framework import (
    compare_day6_strategies,
    compare_day6_strategies_on_recording,
    compare_strategies_over_seeds,
)


def main():
    parser = argparse.ArgumentParser(description="lanceur de tests des méthodes")
    parser.add_argument("--recording", help="chemin vers une partie enregistrée")
    parser.add_argument("--size", type=int, default=21, help="taille du labyrinthe")
    parser.add_argument("--loops", type=int, default=25, help="pourcentage de boucles")
    parser.add_argument("--steps", type=int, default=300, help="longueur du trajet de pac-man")
    parser.add_argument("--seed", type=int, default=42, help="graine du hasard")
    parser.add_argument("--seeds", type=int, default=1, help="nombre de seeds à lancer")
    args = parser.parse_args()

    if args.recording:
        benchmark = compare_day6_strategies_on_recording(args.recording)
        print("=== test des méthodes en mode replay ===")
    else:
        maze = generate_pacman_maze(args.size, args.size, loop_percent=args.loops)
        if args.seeds <= 1:
            benchmark = compare_day6_strategies(maze, route_steps=args.steps, seed=args.seed)
            print("=== test des méthodes en mode hasard ===")
        else:
            seed_values = range(args.seed, args.seed + args.seeds)
            benchmark = compare_strategies_over_seeds(
                maze=maze,
                seeds=seed_values,
                route_steps=args.steps,
            )
            print("=== test des méthodes sur plusieurs seeds ===")

            summary = benchmark["summary"]
            print("\n--- Summary ---")
            for name in summary["ranking"]:
                metrics = summary["strategies"][name]
                rate = 100.0 * metrics["capture_rate"]
                avg_tick = metrics["avg_capture_tick"]
                tick_str = f"{avg_tick:.2f}" if avg_tick is not None else "None"
                print(
                    f"{name}: capture_rate={rate:.1f}% "
                    f"avg_capture_tick={tick_str}"
                )

    pprint(benchmark)


if __name__ == "__main__":
    main()
