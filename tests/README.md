# Tests du projet TER S2

Ce dossier contient les tests actifs du projet.

## Structure actuelle

```text
tests/
├── test_app_local.py        # Tests API locale Flask
├── test_maze_generator.py   # Tests du générateur Prim + loops
├── curl_examples.sh         # Exemples curl (Linux/macOS)
├── curl_examples.bat        # Exemples curl (Windows)
└── README.md
```

## État réel des tests

Actuellement, la suite active dans ce dossier est:
- `tests/test_maze_generator.py` (10 tests)
- `tests/test_app_local.py` (5 tests)

Total actuel: 15 tests.

## Lancer les tests

Depuis la racine du projet:

```bash
python -m pytest tests/ -q
```

Pour lancer uniquement les tests du générateur:

```bash
python -m pytest tests/test_maze_generator.py -v
```

Pour lancer uniquement les tests API locaux:

```bash
python -m pytest tests/test_app_local.py -v
```

## Ce que vérifie `test_maze_generator.py`

- dimensions du labyrinthe
- correction des bords (murs)
- présence murs/couloirs
- valeurs limitées à `0` et `1`
- effet de `add_loops`
- conservation des bordures après ajout de boucles
- connexité globale du labyrinthe
- présence de dead-ends

## API et exemples curl

Si vous démarrez `app.py`, les scripts `curl_examples.sh` et `curl_examples.bat` restent utilisables pour tester la route `/maze`.

## CI

Le workflow GitHub Actions exécute:

```bash
python -m pytest tests/ -v --tb=short
```

Donc, tant que les deux suites actives passent, la CI liée aux tests de ce dossier passe aussi.
