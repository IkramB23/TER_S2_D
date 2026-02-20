import random
import argparse
import json

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate_prim(self):
        start_x = random.randrange(1, self.width, 2)
        start_y = random.randrange(1, self.height, 2)

        self.maze[start_y][start_x] = 0
        walls = []

        walls.extend(self.get_walls(start_x, start_y))

        while walls:
            wx, wy, px, py = random.choice(walls)
            walls.remove((wx, wy, px, py))

            if self.maze[wy][wx] == 1:
                self.maze[wy][wx] = 0
                self.maze[py][px] = 0
                walls.extend(self.get_walls(wx, wy))

    def get_walls(self, x, y):
        walls = []
        directions = [(2,0), (-2,0), (0,2), (0,-2)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < self.width and 0 < ny < self.height:
                if self.maze[ny][nx] == 1:
                    walls.append((nx, ny, x + dx//2, y + dy//2))

        return walls

    def display(self):
        for row in self.maze:
            print("".join("  " if cell == 0 else "██" for cell in row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générateur de labyrinthe - Algorithme de Prim")
    parser.add_argument("--width", type=int, required=True, help="Largeur du labyrinthe")
    parser.add_argument("--height", type=int, required=True, help="Hauteur du labyrinthe")

    args = parser.parse_args()

    maze = Maze(args.width, args.height)
    maze.generate_prim()
    maze.display()

    print(json.dumps(maze.maze))

