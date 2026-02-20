from collections import deque


def count_corridors(maze):
    # compte le nombre total de cases couloir
    return sum(cell == 0 for row in maze for cell in row)


def count_dead_ends(maze):
    height, width = len(maze), len(maze[0])
    dead_ends = 0

    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 0:
                voisins = sum([
                    maze[y-1][x] == 0,
                    maze[y+1][x] == 0,
                    maze[y][x-1] == 0,
                    maze[y][x+1] == 0
                ])
                if voisins == 1:
                    dead_ends += 1
    return dead_ends


def count_intersections(maze):
    height, width = len(maze), len(maze[0])
    intersections = 0

    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 0:
                voisins = sum([
                    maze[y-1][x] == 0,
                    maze[y+1][x] == 0,
                    maze[y][x-1] == 0,
                    maze[y][x+1] == 0
                ])
                if voisins >= 3:
                    intersections += 1
    return intersections


def longest_path(maze):
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
            if 0 <= ny < height and 0 <= nx < width:
                if maze[ny][nx] == 0 and (ny, nx) not in visited:
                    visited.add((ny, nx))
                    queue.append(((ny, nx), dist+1))

    return max_dist


def count_loops(maze):
    height, width = len(maze), len(maze[0])
    corridors = 0
    edges = 0

    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 0:
                corridors += 1

                if x+1 < width and maze[y][x+1] == 0:
                    edges += 1
                if y+1 < height and maze[y+1][x] == 0:
                    edges += 1

    loops = edges - (corridors - 1)
    return max(0, loops)


def analyze_maze(maze):
    height, width = len(maze), len(maze[0])
    total_cases = (height - 2) * (width - 2)

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
    print(f"jouabilite       : {'bonne' if dead_ends < intersections else 'moyenne'}")


# ===== TEST AVEC PRIM =====

if __name__ == "__main__":

    from maze_Prim import Maze

    print("=== analyse du labyrinthe PRIM ===\n")

    maze_obj = Maze(31, 31)
    maze_obj.generate_prim()

    # Afficher le labyrinthe
    print("=== Maze généré ===\n")
    maze_obj.display()
    print("\n")

    analyze_maze(maze_obj.maze)
