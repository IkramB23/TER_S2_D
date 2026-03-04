# Tests du generateur de labyrinthe (execution locale, pas de Render)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Proto.maze_Prim_loops import generate_maze, add_loops, generate_pacman_maze


# ============ Tests fonctionnels : dimensions ============

def test_maze_dimensions_basic():
    """Un maze 21x21 doit retourner exactement 21 lignes de 21 colonnes."""
    maze = generate_maze(21, 21)
    assert len(maze) == 99, "ERREUR VOLONTAIRE : on attend 99 au lieu de 21"
    assert all(len(row) == 21 for row in maze)


def test_maze_dimensions_various():
    """Tester plusieurs tailles."""
    for size in [11, 15, 21, 31]:
        maze = generate_maze(size, size)
        assert len(maze) == size
        assert len(maze[0]) == size


def test_pacman_maze_forces_odd():
    """generate_pacman_maze doit forcer des dimensions impaires."""
    maze = generate_pacman_maze(20, 20)  # pair → doit devenir 21x21
    assert len(maze) % 2 == 1
    assert len(maze[0]) % 2 == 1


# ============ Tests structurels : contenu du maze ============

def test_maze_has_walls_and_corridors():
    """Le maze doit contenir des murs (0) et des couloirs (1)."""
    maze = generate_maze(21, 21)
    flat = [cell for row in maze for cell in row]
    assert 0 in flat, "Pas de murs"
    assert 1 in flat, "Pas de couloirs"


def test_maze_border_is_walls():
    """Les bords du maze doivent etre des murs (0)."""
    maze = generate_maze(21, 21)
    h, w = len(maze), len(maze[0])
    # premiere et derniere ligne
    assert all(cell == 0 for cell in maze[0]), "Bord haut pas mur"
    assert all(cell == 0 for cell in maze[h-1]), "Bord bas pas mur"
    # premiere et derniere colonne
    assert all(maze[y][0] == 0 for y in range(h)), "Bord gauche pas mur"
    assert all(maze[y][w-1] == 0 for y in range(h)), "Bord droit pas mur"


def test_maze_only_0_and_1():
    """Le maze ne doit contenir que des 0 et des 1."""
    maze = generate_maze(21, 21)
    for row in maze:
        for cell in row:
            assert cell in (0, 1), f"Valeur inattendue: {cell}"


# ============ Tests des boucles (add_loops) ============

def test_add_loops_increases_corridors():
    """add_loops doit creer plus de couloirs que le maze parfait."""
    maze = generate_maze(21, 21)
    corridors_before = sum(cell == 1 for row in maze for cell in row)
    maze = add_loops(maze, loop_percent=30)
    corridors_after = sum(cell == 1 for row in maze for cell in row)
    assert corridors_after > corridors_before, "add_loops n'a pas ouvert de murs"


def test_add_loops_preserves_borders():
    """add_loops ne doit pas casser les murs de bordure."""
    maze = generate_pacman_maze(21, 21, loop_percent=50)
    h, w = len(maze), len(maze[0])
    assert all(cell == 0 for cell in maze[0])
    assert all(cell == 0 for cell in maze[h-1])
    assert all(maze[y][0] == 0 for y in range(h))
    assert all(maze[y][w-1] == 0 for y in range(h))


# ============ Tests des proprietes du labyrinthe ============

def test_maze_connectivity():
    """Le maze doit etre connexe (tous les couloirs accessibles depuis un point)."""
    maze = generate_pacman_maze(21, 21, loop_percent=25)
    h, w = len(maze), len(maze[0])

    # trouver un premier couloir
    start = None
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 1:
                start = (y, x)
                break
        if start:
            break

    assert start is not None, "Pas de couloir"

    # BFS
    visited = set()
    queue = [start]
    visited.add(start)
    while queue:
        cy, cx = queue.pop(0)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and (ny, nx) not in visited and maze[ny][nx] == 1:
                visited.add((ny, nx))
                queue.append((ny, nx))

    total_corridors = sum(cell == 1 for row in maze for cell in row)
    assert len(visited) == total_corridors, f"Maze non connexe: {len(visited)}/{total_corridors} couloirs accessibles"


def test_maze_has_dead_ends():
    """Un maze Prim (meme avec loops) doit avoir des dead-ends."""
    maze = generate_pacman_maze(21, 21, loop_percent=25)
    h, w = len(maze), len(maze[0])
    dead_ends = 0
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if maze[y][x] == 1:
                neighbors = sum(1 for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                                if maze[y + dy][x + dx] == 1)
                if neighbors == 1:
                    dead_ends += 1
    assert dead_ends > 0, "Pas de dead-ends"
