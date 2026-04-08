# Tests du projet TER S2

## Structure

```text
tests/
  test_maze_generator.py   # 10 tests generateur Prim + boucles
  test_app_local.py        # 5 tests API Flask locale
  test_game.py             # 24 tests environnement, agents, engine, recorder
  test_framework.py        # 12 tests algorithmes DFS/UCS/MCTS + benchmark
```

Total : 51 tests.

## Lancer les tests

Depuis la racine du projet :

```bash
python -m pytest tests/ -v
```

Un fichier seul :

```bash
python -m pytest tests/test_framework.py -v
```

## Ce que couvrent les tests

- **test_maze_generator** : dimensions, bordures, murs/couloirs, valeurs 0/1, boucles, connexite
- **test_app_local** : routes Flask /, /maze, format JSON, contenu du labyrinthe
- **test_game** : pellets, power pellets, spawn pacman/fantomes, fruits, directions, BFS, modes fantomes, engine tick/state, recorder save/load
- **test_framework** : DFS/UCS/MCTS direction + no-path, prediction, benchmark shape, route extraction, comparaison multi-seeds

## CI

GitHub Actions execute `python -m pytest tests/ -v --tb=short` a chaque push.
