# analyse de labyrinthe : metriques pour comparer les algos
# sert a justifier le choix d'un algo vs un autre
from collections import deque

def count_corridors(maze):
    # compte le nombre total de cases couloir
    return sum(cell == 1 for row in maze for cell in row)

def count_dead_ends(maze):
    # compte les culs-de-sac (1 seul voisin couloir)
    height, width = len(maze), len(maze[0])
    dead_ends = 0
    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 1:
                voisins = sum([
                    maze[y-1][x] == 1,
                    maze[y+1][x] == 1,
                    maze[y][x-1] == 1,
                    maze[y][x+1] == 1
                ])
                if voisins == 1:
                    dead_ends += 1
    return dead_ends

def count_intersections(maze):
    # compte les intersections (3+ voisins couloir)
    height, width = len(maze), len(maze[0])
    intersections = 0
    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 1:
                voisins = sum([
                    maze[y-1][x] == 1,
                    maze[y+1][x] == 1,
                    maze[y][x-1] == 1,
                    maze[y][x+1] == 1
                ])
                if voisins >= 3:
                    intersections += 1
    return intersections

def longest_path(maze):
    # trouve le plus long chemin depuis (1,1) avec bfs
    height, width = len(maze), len(maze[0])
    start = (1, 1)
    visited = set()
    queue = deque([(start, 0)])
    visited.add(start)
    max_dist = 0

    while queue:
        (y, x), dist = queue.popleft()
        max_dist = max(max_dist, dist)
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y+dy, x+dx
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1 and (ny,nx) not in visited:
                visited.add((ny, nx))
                queue.append(((ny, nx), dist+1))
    
    return max_dist

def count_loops(maze):
    # estime le nombre de boucles : nb_couloirs - nb_couloirs_dans_un_arbre
    # dans un arbre couvrant : edges = nodes - 1
    # boucles = edges_reelles - (nodes - 1)
    height, width = len(maze), len(maze[0])
    corridors = 0
    edges = 0
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 1:
                corridors += 1
                # compter les voisins a droite et en bas pour eviter les doublons
                if x+1 < width and maze[y][x+1] == 1:
                    edges += 1
                if y+1 < height and maze[y+1][x] == 1:
                    edges += 1
    
    loops = edges - (corridors - 1)
    return max(0, loops)

def analyze_maze(maze):
    # lance toutes les metriques et affiche un resume
    height, width = len(maze), len(maze[0])
    total_cases = (height - 2) * (width - 2)  # sans les bords
    corridors = count_corridors(maze)
    dead_ends = count_dead_ends(maze)
    intersections = count_intersections(maze)
    loops = count_loops(maze)
    max_path = longest_path(maze)
    
    print(f"taille           : {width}x{height}")
    print(f"cases totales    : {total_cases}")
    print(f"couloirs         : {corridors}")
    print(f"ratio couloirs   : {corridors/total_cases*100:.1f}%")
    print(f"culs-de-sac      : {dead_ends}")
    print(f"intersections    : {intersections}")
    print(f"boucles          : {loops}")
    print(f"plus long chemin : {max_path} cases")
    print(f"jouabilite       : {'bonne' if dead_ends < intersections else 'moyenne'} (moins de culs-de-sac = mieux)")

# comparaison dfs vs prim sur plusieurs generations
if __name__ == "__main__":
    from maze_dfs import generate_pacman_maze as dfs_maze, print_maze
    from maze_prim import generate_pacman_maze as prim_maze
    
    n_tests = 10
    width, height = 31, 31
    loop_percent = 25
    
    def average_metrics(generator, n, w, h, lp):
        # fait n generations et calcule les moyennes
        totals = {"corridors": 0, "dead_ends": 0, "intersections": 0, "loops": 0, "longest": 0}
        for _ in range(n):
            maze = generator(w, h, loop_percent=lp)
            totals["corridors"] += count_corridors(maze)
            totals["dead_ends"] += count_dead_ends(maze)
            totals["intersections"] += count_intersections(maze)
            totals["loops"] += count_loops(maze)
            totals["longest"] += longest_path(maze)
        return {k: v / n for k, v in totals.items()}
    
    print(f"=== comparaison DFS vs PRIM ({n_tests} labyrinthes {width}x{height}, {loop_percent}% boucles) ===\n")
    
    print("calcul en cours...")
    dfs_avg = average_metrics(dfs_maze, n_tests, width, height, loop_percent)
    prim_avg = average_metrics(prim_maze, n_tests, width, height, loop_percent)
    
    print(f"{'metrique':<20} {'DFS':>10} {'PRIM':>10} {'meilleur':>12}")
    print("-" * 55)
    
    for key in dfs_avg:
        d, p = dfs_avg[key], prim_avg[key]
        if key == "dead_ends":
            best = "DFS" if d < p else "PRIM"  # moins = mieux
        elif key in ("intersections", "loops"):
            best = "DFS" if d > p else "PRIM"  # plus = mieux pour pacman
        elif key == "longest":
            best = "DFS" if d > p else "PRIM"  # plus = mieux
        else:
            best = "-"
        print(f"{key:<20} {d:>10.1f} {p:>10.1f} {best:>12}")
    
    # jouabilite
    dfs_jouable = "bonne" if dfs_avg["dead_ends"] < dfs_avg["intersections"] else "moyenne"
    prim_jouable = "bonne" if prim_avg["dead_ends"] < prim_avg["intersections"] else "moyenne"
    print(f"\n{'jouabilite':<20} {'':>4}{dfs_jouable:>6} {'':>4}{prim_jouable:>6}")
    
    # affiche un exemple prim
    print("\n=== exemple labyrinthe PRIM ===\n")
    maze = prim_maze(width, height, loop_percent=loop_percent)
    print_maze(maze)
    print()
    analyze_maze(maze)
