#ikram
# generation de labyrinthe avec DFS + boucles pour pac-man
import random

def generate_maze(width, height):
    # cree un labyrinthe parfait avec dfs
    maze = [[0 for _ in range(width)] for _ in range(height)]
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    
    def dfs(y, x):
        maze[y][x] = 1
        random.shuffle(directions)
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 0:
                maze[y + dy//2][x + dx//2] = 1
                dfs(ny, nx)
    
    dfs(1, 1)
    return maze

def print_maze(maze):
    # affiche le labyrinthe en ascii
    for row in maze:
        print("".join("  " if cell == 1 else "██" for cell in row))

def add_loops(maze, loop_percent=20):
    # supprime des murs pour creer des boucles
    height, width = len(maze), len(maze[0])
    walls = []
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 0:
                # mur entre deux couloirs = peut etre supprime
                if (maze[y-1][x] == 1 and maze[y+1][x] == 1) or \
                   (maze[y][x-1] == 1 and maze[y][x+1] == 1):
                    walls.append((y, x))
    
    n_remove = int(len(walls) * loop_percent / 100)
    for y, x in random.sample(walls, min(n_remove, len(walls))):
        maze[y][x] = 1
    
    return maze

def generate_pacman_maze(width=15, height=15, loop_percent=25):
    # genere un labyrinthe jouable (dimensions impaires)
    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1
    
    maze = generate_maze(width, height)
    maze = add_loops(maze, loop_percent)
    return maze

# test
if __name__ == "__main__":
    print(" exemple de labyrinthe pac-man\n")
    maze = generate_pacman_maze(15, 15, loop_percent=25)
    print_maze(maze)
