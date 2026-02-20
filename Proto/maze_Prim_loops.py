# generation de labyrinthe avec prim + boucles pour pac-man
# adapte du code de nada (convention: 0=mur, 1=couloir)
import random

def generate_maze(width, height):
    # cree un labyrinthe parfait avec l'algo de prim
    maze = [[0 for _ in range(width)] for _ in range(height)]
    
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    maze[start_y][start_x] = 1
    
    walls = []
    
    def get_walls(x, y):
        # recupere les murs autour d'une cellule
        result = []
        for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height:
                if maze[ny][nx] == 0:
                    # (cellule voisine, mur entre les deux)
                    result.append((nx, ny, x + dx//2, y + dy//2))
        return result
    
    walls.extend(get_walls(start_x, start_y))
    
    while walls:
        wx, wy, px, py = random.choice(walls)
        walls.remove((wx, wy, px, py))
        
        if maze[wy][wx] == 0:
            maze[wy][wx] = 1  # ouvre la cellule
            maze[py][px] = 1  # ouvre le mur entre
            walls.extend(get_walls(wx, wy))
    
    return maze

def print_maze(maze):
    # affiche le labyrinthe en ascii
    for row in maze:
        print("".join("  " if cell == 1 else "██" for cell in row))

def add_loops(maze, loop_percent=20):
    # supprime des murs pour creer des boucles (meme fonction que dfs)
    height, width = len(maze), len(maze[0])
    walls = []
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if maze[y][x] == 0:
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
    print(" exemple de labyrinthe prim\n")
    maze = generate_pacman_maze(15, 15, loop_percent=25)
    print_maze(maze)
