import pathlib
p = pathlib.Path('local_pacman.py')
text = p.read_text(encoding='utf-8')

text = text.replace('import time', 'import time\nimport requests')
text = text.replace('DB_PATH = Path(__file__).parent / ""mazes.db""', 'DB_PATH = Path(__file__).parent / ""mazes.db""\nAPI_URL = ""http://127.0.0.1:5000""')

text = text.replace(
'''            CREATE TABLE IF NOT EXISTS mazes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                loop_percent INTEGER NOT NULL,
                maze_json TEXT NOT NULL
            )
            ""\"
        )
        self.conn.commit()''',
'''            CREATE TABLE IF NOT EXISTS mazes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                loop_percent INTEGER NOT NULL,
                maze_json TEXT NOT NULL,
                cloud_id TEXT
            )
            ""\"
        )
        try:
            self.conn.execute("ALTER TABLE mazes ADD COLUMN cloud_id TEXT")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()''')

text = text.replace(
'''    def save_maze(self, maze, width: int, height: int, loop_percent: int) -> int:
        cursor = self.conn.execute(
            ""\"
            INSERT INTO mazes(created_at, width, height, loop_percent, maze_json)
            VALUES (?, ?, ?, ?, ?)
            ""\",
            (int(time.time()), width, height, loop_percent, json.dumps(maze)),
        )
        self.conn.commit()
        return int(cursor.lastrowid)''',
'''    def save_maze(self, maze, width: int, height: int, loop_percent: int, cloud_id: str = None) -> int:
        cursor = self.conn.execute(
            ""\"
            INSERT INTO mazes(created_at, width, height, loop_percent, maze_json, cloud_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ""\",
            (int(time.time()), width, height, loop_percent, json.dumps(maze), cloud_id),
        )
        self.conn.commit()
        return int(cursor.lastrowid)''')

text = text.replace(
'''    def get_maze(self, maze_id: int):
        row = self.conn.execute(
            "SELECT * FROM mazes WHERE id = ?", (maze_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": int(row["id"]),
            "created_at": int(row["created_at"]),
            "width": int(row["width"]),
            "height": int(row["height"]),
            "loop_percent": int(row["loop_percent"]),
            "maze": json.loads(row["maze_json"]),
        }''',
'''    def get_maze(self, maze_id: int):
        row = self.conn.execute(
            "SELECT * FROM mazes WHERE id = ?", (maze_id,)
        ).fetchone()
        if not row:
            return None
        cloud_id = None
        if "cloud_id" in row.keys():
            cloud_id = row["cloud_id"]
        return {
            "id": int(row["id"]),
            "cloud_id": cloud_id,
            "created_at": int(row["created_at"]),
            "width": int(row["width"]),
            "height": int(row["height"]),
            "loop_percent": int(row["loop_percent"]),
            "maze": json.loads(row["maze_json"]),
        }''')

text = text.replace(
'''        if count == 0:
            maze = generate_pacman_maze(21, 21, 25)
            self.save_maze(maze, len(maze[0]), len(maze), 25)''',
'''        if count == 0:
            maze = generate_pacman_maze(21, 21, 25)
            self.save_maze(maze, len(maze[0]), len(maze), 25, None)''')


text = text.replace(
'''    def _create_new_maze(self):
        maze = generate_pacman_maze(self.target_size, self.target_size, self.target_loop)
        width = len(maze[0])
        height = len(maze)
        new_id = self.repo.save_maze(maze, width, height, self.target_loop)
        self.maze_ids = self.repo.list_ids()
        self.current_index = self.maze_ids.index(new_id)
        self.current = self.repo.get_maze(new_id)
        self.player = self._find_start(self.current["maze"])
        self.player_dir = (1, 0)''',
'''    def _create_new_maze(self):
        try:
            url = f"{API_URL}/maze?width={self.target_size}&height={self.target_size}&loop_percent={self.target_loop}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            maze = data["maze"]
            cloud_id = data.get("id")
            width = len(maze[0])
            height = len(maze)
            new_id = self.repo.save_maze(maze, width, height, self.target_loop, cloud_id)
        except Exception as e:
            print(f"Erreur API: {e}. Génération locale hors-ligne...")
            maze = generate_pacman_maze(self.target_size, self.target_size, self.target_loop)
            width = len(maze[0])
            height = len(maze)
            new_id = self.repo.save_maze(maze, width, height, self.target_loop, None)

        self.maze_ids = self.repo.list_ids()
        self.current_index = self.maze_ids.index(new_id)
        self.current = self.repo.get_maze(new_id)
        self.player = self._find_start(self.current["maze"])
        self.player_dir = (1, 0)

    def _rate_current_maze(self, rating):
        cloud_id = self.current.get("cloud_id")
        if not cloud_id:
            print("Impossible de noter: Ce labyrinthe ne provient pas du cloud (aucun cloud_id).")
            return
            
        try:
            url = f"{API_URL}/maze/{cloud_id}/rate"
            response = requests.post(url, json={"rating": rating}, timeout=3)
            if response.status_code == 200:
                print(f"Labyrinthe {cloud_id} noté: {rating}/5 étoile(s) ! ⭐")
            else:
                print(f"Erreur de notation: {response.json()}")
        except Exception as e:
            print(f"Erreur d'envoi de la note: {e}")''')

text = text.replace(
'''                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS) or char == "+":
                        self._update_target_size(2)
                    elif event.key == pygame.K_0:
                        self._set_target_loop(0)
                    elif event.key == pygame.K_2:
                        self._set_target_loop(25)
                    elif event.key == pygame.K_4:
                        self._set_target_loop(40)''',
'''                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS) or char == "+":
                        self._update_target_size(2)
                    elif event.key == pygame.K_KP0:
                        self._set_target_loop(0)
                    elif event.key == pygame.K_KP2:
                        self._set_target_loop(25)
                    elif event.key == pygame.K_KP4:
                        self._set_target_loop(40)
                    elif event.key == pygame.K_0:
                        self._rate_current_maze(0)
                    elif event.key == pygame.K_1:
                        self._rate_current_maze(1)
                    elif event.key == pygame.K_2:
                        self._rate_current_maze(2)
                    elif event.key == pygame.K_3:
                        self._rate_current_maze(3)
                    elif event.key == pygame.K_4:
                        self._rate_current_maze(4)
                    elif event.key == pygame.K_5:
                        self._rate_current_maze(5)''')

text = text.replace(
'''    def _draw_hud(self):
        title = self.font.render("Pac-Man Local (sans fantÃ´mes)", True, (235, 235, 235))
        self.screen.blit(title, (24, 20))

        info = (
            f"Maze ID: {self.current['id']}   "
            f"Taille: {self.current['width']}x{self.current['height']}   "
            f"Boucles: {self.current['loop_percent']}%"
        )
        line = self.small.render(info, True, (210, 210, 210))
        self.screen.blit(line, (24, 55))

        pending = self.small.render(
            f"ParamÃ¨tres courants: taille {self.target_size} | boucles {self.target_loop}%",
            True,
            (210, 210, 210),
        )
        self.screen.blit(pending, (24, 80))

        controls = (
            "FlÃ¨ches/WASD: bouger | N: nouveau | P/M: prÃ©cÃ©dent/suivant | +/-: taille | 0/2/4: boucles"
        )
        controls_surface = self.small.render(controls, True, (180, 180, 180))
        self.screen.blit(controls_surface, (24, self.window_h - 34))''',
'''    def _draw_hud(self):
        title = self.font.render("Pac-Man Local (sans fantômes)", True, (235, 235, 235))
        self.screen.blit(title, (24, 20))

        cid = self.current.get('cloud_id')
        disp_id = cid if cid else self.current['id']
        info = (
            f"Maze ID: {disp_id}   "
            f"Taille: {self.current['width']}x{self.current['height']}   "
            f"Boucles: {self.current['loop_percent']}%"
        )
        line = self.small.render(info, True, (210, 210, 210))
        self.screen.blit(line, (24, 55))

        pending = self.small.render(
            f"Paramètres courants: taille {self.target_size} | boucles {self.target_loop}%",
            True,
            (210, 210, 210),
        )
        self.screen.blit(pending, (24, 80))

        controls = (
            "Flèches/WASD: bouger | N: nouveau | P/M: précédent/suivant | +/-: taille"
        )
        controls_surface = self.small.render(controls, True, (180, 180, 180))
        self.screen.blit(controls_surface, (24, self.window_h - 54))
        
        controls2 = "Pavé Num 0/2/4: boucles | Touches 0 à 5: Noter ce labyrinthe !"
        controls_surface2 = self.small.render(controls2, True, (180, 180, 180))
        self.screen.blit(controls_surface2, (24, self.window_h - 30))''')

p.write_text(text, encoding='utf-8')
