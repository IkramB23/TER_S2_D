# Pac-Man TER S2 - Groupe D


## Installation

```bash
pip install flask pygame requests pymongo dnspython pytest
```

## Lancer le jeu (local, avec interface graphique)

```bash
python local_pacman.py
```

### Controles

| Touche | Action |
|--------|--------|
| Fleches / WASD | Deplacer Pac-Man |
| N | Nouveau labyrinthe (depuis le cloud) |
| R | Relancer la partie |
| P / M | Parcourir les labyrinthes sauvegardes |
| +/- | Changer la taille du labyrinthe |
| 0, 3-7 | Noter le labyrinthe (0=bad a 5=good) |
| 1 | Mode solo (sans fantomes, enregistre le trajet) |
| 2 | Mode replay (rejoue le trajet avec fantomes IA) |
| ESC | Quitter |

### Mode solo et replay

1. Appuyer sur **1** pour jouer sans fantomes. Le trajet est enregistre automatiquement.
2. Appuyer sur **2** pour rejouer ce trajet avec des fantomes pilotes par une IA.
   Appuyer plusieurs fois sur **2** pour changer l'algorithme (BFS, A*, DFS, UCS, MCTS).
3. Le nombre de ticks avant capture est affiche a l'ecran.

## Lancer le serveur API

```bash
python app.py
```

Ou via le deploiement Render : https://ter-s2-d-85u5.onrender.com

### Routes API

| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Page d'accueil |
| GET | `/maze` | Generer un labyrinthe (params: width, height, loop_percent) |
| POST | `/maze/<id>/rate` | Noter un labyrinthe (body: {"rating": 0-5}) |
| GET | `/ai/algorithms` | Liste des algorithmes disponibles |
| POST | `/ai/benchmark` | Lancer un benchmark (body: {"maze", "route", "strategies"}) |

## Lancer les tests

```bash
python -m pytest tests/ -v
```

51 tests couvrent : generation de labyrinthes, API Flask, environnement de jeu, agents,
moteur de jeu, enregistrement, et les 5 algorithmes de poursuite.

## Structure du projet

```
TER_S2_D/
  app.py                  # serveur Flask (API REST + MongoDB Atlas)
  local_pacman.py          # client pygame (jeu local + modes solo/replay)
  requirements.txt         # dependances Python
  Procfile                 # deploiement Render
  game/
    environment.py         # plateau de jeu (murs, pellets, fruits, power pellets)
    agents.py              # agents Pac-Man + 4 fantomes (Blinky, Pinky, Inky, Clyde)
    engine.py              # moteur de jeu (tick, collisions, score, vies, modes)
    renderer.py            # rendu pygame (dessin du labyrinthe, HUD, overlays)
    recorder.py            # enregistrement/chargement de parties en JSON
    framework.py           # benchmark : compare les strategies IA sur un trajet
  Proto/
    maze_Prim_loops.py     # generateur de labyrinthes (Prim + boucles)
    maze_dfs.py            # generateur DFS (prototype)
    maze_Prim.py           # generateur Prim (prototype)
  tests/
    test_maze_generator.py # 10 tests generation de labyrinthes
    test_app_local.py      # 5 tests API Flask
    test_game.py           # 24 tests environnement, agents, engine, recorder
    test_framework.py      # 12 tests algorithmes et benchmark
  recordings/              # parties enregistrees (JSON)
  .github/workflows/       # CI GitHub Actions
```

## Algorithmes de poursuite (fantomes)

Le module `game/agents.py` implemente 5 algorithmes de pathfinding pour les fantomes :

| Algorithme | Description |
|------------|-------------|
| BFS | Parcours en largeur, baseline qui trouve le chemin le plus court |
| A* | Recherche informee avec heuristique Manhattan, optimal et plus rapide que BFS |
| DFS | Parcours en profondeur, non-optimal mais comportement de poursuite different |
| UCS | Recherche a cout uniforme, equivalent a BFS sur grille uniforme |
| MCTS | Monte Carlo Tree Search, exploration aleatoire avec simulation |

La difficulte du niveau determine l'algorithme utilise par les fantomes :

| Niveau | Pathfinding | Vitesse fantome | Anticipation |
|--------|-------------|-----------------|---------------|
| Facile | BFS | lente (14 ticks) | aucune |
| Moyen | A* | normale (8 ticks) | aucune |
| Difficile | A* | rapide (6 ticks) | 3 pas en avance |

## Agents IA pour Pac-Man

Trois agents IA pilotent Pac-Man automatiquement, accessibles en mode replay (touche **2**) :

| Agent | Description |
|-------|-------------|
| AStarPacmanAgent | Pac-Man suit le chemin A* vers la pastille la plus proche |
| MinimaxPacmanAgent | Minimax avec elagage Alpha-Beta, depth=0, 4 fantomes actifs |
| ExpectimaxPacmanAgent | Expectimax (noeuds chance), depth=0, modelise le comportement aleatoire des fantomes |

## Lancer les benchmarks

Benchmark IA vs humains (6 configurations : 2 niveaux humains + 4 agents IA) :

```bash
python benchmark_ia_vs_humain.py
```

Benchmark algorithmes de poursuite sur un trajet enregistre :

```bash
python -m pytest tests/test_framework.py -v
```

Ou directement via l'API :

```
POST /ai/benchmark
{
  "maze": [...],
  "route": [...],
  "strategies": ["bfs", "astar", "dfs", "ucs", "mcts"]
}
```

## Base de donnees

- **MongoDB Atlas** : stockage des labyrinthes generes et des notes
  - Cluster : cluster0.inawb.mongodb.net
  - Base : pacman_db
  - Collection : mazes
- **SQLite** (mazes.db) : cache local des labyrinthes telecharges

## CI/CD

- GitHub Actions execute les 51 tests a chaque push
- Deploiement automatique sur Render (https://ter-s2-d-85u5.onrender.com)
