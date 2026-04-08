# environment - plateau de jeu dynamique (maze + pellets + fruits)


class Environment:

    def __init__(self, maze_data):
        # maze_data : liste 2D, 0=mur, 1=couloir
        self.height = len(maze_data)
        self.width = len(maze_data[0])
        self.maze = maze_data

        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.fruit_pos = None
        self.fruit_timer = 0
        self.fruit_points = 100
        self.total_pellets = 0

        self._init_from_maze(maze_data)

    def _init_from_maze(self, maze_data):
        corridors = []
        for y in range(self.height):
            for x in range(self.width):
                if maze_data[y][x] == 0:
                    self.walls.add((x, y))
                else:
                    corridors.append((x, y))

        pp_positions = set(self._find_power_pellet_positions(corridors))
        self.power_pellets = pp_positions

        # pellets sur tous les couloirs sauf power pellets, zone fantômes et spawn pacman
        ghost_area = self._get_ghost_house_area()
        pac_spawn = self.find_pacman_spawn()
        excluded = pp_positions | ghost_area | {pac_spawn}

        self.pellets = set(c for c in corridors if c not in excluded)
        self.total_pellets = len(self.pellets) + len(self.power_pellets)

    def _find_power_pellet_positions(self, corridors):
        # place 4 power pellets proches des 4 coins
        corners = [
            (2, 2),
            (self.width - 3, 2),
            (2, self.height - 3),
            (self.width - 3, self.height - 3),
        ]
        positions = []
        for cx, cy in corners:
            best = min(corridors, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
            if best not in positions:
                positions.append(best)
        return positions

    def _get_ghost_house_area(self):
        # zone centrale où les fantômes apparaissent
        cx, cy = self.width // 2, self.height // 2
        area = set()
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if self.is_corridor(x, y):
                    area.add((x, y))
        return area

    def is_wall(self, x, y):
        return (x, y) in self.walls

    def is_corridor(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.walls

    def eat_pellet(self, x, y):
        # mange un pellet, retourne (points, is_power)
        if (x, y) in self.power_pellets:
            self.power_pellets.discard((x, y))
            return 50, True
        if (x, y) in self.pellets:
            self.pellets.discard((x, y))
            return 10, False
        return 0, False

    def all_pellets_eaten(self):
        return len(self.pellets) == 0 and len(self.power_pellets) == 0

    def pellets_remaining(self):
        return len(self.pellets) + len(self.power_pellets)

    def spawn_fruit(self):
        # fait apparaître un fruit bonus au centre
        cx, cy = self.width // 2, self.height // 2
        for r in range(max(self.width, self.height)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = cx + dx, cy + dy
                    if self.is_corridor(nx, ny):
                        self.fruit_pos = (nx, ny)
                        self.fruit_timer = 600  # 10 secondes à 60fps
                        return

    def update_fruit(self):
        if self.fruit_timer > 0:
            self.fruit_timer -= 1
            if self.fruit_timer <= 0:
                self.fruit_pos = None

    def eat_fruit(self, x, y):
        # mange le fruit, retourne les points
        if self.fruit_pos and self.fruit_pos == (x, y):
            self.fruit_pos = None
            self.fruit_timer = 0
            return self.fruit_points
        return 0

    def find_pacman_spawn(self):
        # trouve un spawn pour pacman en bas du maze
        cx = self.width // 2
        for y in range(self.height - 2, 0, -1):
            for offset in range(self.width):
                x = cx + (offset + 1) // 2 * (1 if offset % 2 == 0 else -1)
                if 0 <= x < self.width and self.maze[y][x] == 1:
                    return (x, y)
        return (1, 1)

    def find_ghost_spawns(self, count=4):
        # trouve des positions de spawn pour les fantômes au centre
        cx, cy = self.width // 2, self.height // 2
        positions = []
        for r in range(max(self.width, self.height)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    x, y = cx + dx, cy + dy
                    if self.is_corridor(x, y) and (x, y) not in positions:
                        positions.append((x, y))
                        if len(positions) >= count:
                            return positions
        # fallback : prend n'importe quel couloir
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 1 and (x, y) not in positions:
                    positions.append((x, y))
                    if len(positions) >= count:
                        return positions
        return positions

    def get_state_snapshot(self):
        # retourne un snapshot de l'état de l'environnement
        return {
            "pellets_count": len(self.pellets),
            "power_pellets_count": len(self.power_pellets),
            "fruit_pos": self.fruit_pos,
        }
