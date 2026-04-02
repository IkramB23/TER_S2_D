import json
import sqlite3
import time
from pathlib import Path

import pygame
import requests

from Proto.maze_Prim_loops import generate_pacman_maze
from game.environment import Environment
from game.agents import HumanAgent, BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost
from game.engine import GameEngine
from game.recorder import GameRecorder
from game.renderer import PacmanRenderer


DB_PATH = Path(__file__).parent / "mazes.db"
API_URL = "https://ter-s2-d.onrender.com"
RECORDINGS_DIR = Path(__file__).parent / "recordings"


class MazeRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mazes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                loop_percent INTEGER NOT NULL,
                maze_json TEXT NOT NULL,
                cloud_id TEXT
            )
            """
        )
        try:
            self.conn.execute("ALTER TABLE mazes ADD COLUMN cloud_id TEXT")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def save_maze(self, maze, width: int, height: int, loop_percent: int, cloud_id: str = None) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO mazes(created_at, width, height, loop_percent, maze_json, cloud_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (int(time.time()), width, height, loop_percent, json.dumps(maze), cloud_id),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def list_ids(self):
        rows = self.conn.execute("SELECT id FROM mazes ORDER BY id").fetchall()
        return [int(r["id"]) for r in rows]

    def get_maze(self, maze_id: int):
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
        }

    def ensure_one_default(self):
        count = self.conn.execute("SELECT COUNT(*) AS c FROM mazes").fetchone()["c"]
        if count == 0:
            maze = generate_pacman_maze(21, 21, 25)
            self.save_maze(maze, len(maze[0]), len(maze), 25, None)


class LocalPacmanGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pac-Man - TER S2")

        self.repo = MazeRepository(DB_PATH)
        self.repo.ensure_one_default()
        self.maze_ids = self.repo.list_ids()
        self.current_index = len(self.maze_ids) - 1
        self.current = self.repo.get_maze(self.maze_ids[self.current_index])

        self.window_w = 960
        self.window_h = 800
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))
        self.clock = pygame.time.Clock()

        self.target_size = 21
        self.target_loop = self.current["loop_percent"]

        self.renderer = PacmanRenderer(self.screen, self.window_w, self.window_h)

        self._start_game()

    # ------------------------------------------------------------------
    #  lancement du jeu
    # ------------------------------------------------------------------

    def _start_game(self):
        # initialise le moteur de jeu avec le labyrinthe courant
        maze = self.current["maze"]
        self.env = Environment(maze)

        # pacman apparaît en bas
        pac_pos = self.env.find_pacman_spawn()
        self.pacman = HumanAgent(*pac_pos)

        # les fantômes apparaissent au centre
        ghost_spawns = self.env.find_ghost_spawns(4)
        w, h = self.env.width, self.env.height
        ghost_classes = [BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost]
        self.ghosts = []
        for i, cls in enumerate(ghost_classes):
            if i < len(ghost_spawns):
                gx, gy = ghost_spawns[i]
            else:
                gx, gy = ghost_spawns[0]
            self.ghosts.append(cls(gx, gy, w, h))

        # enregistreur
        self.recorder = GameRecorder()
        self.recorder.set_metadata(
            maze, w, h,
            cloud_id=self.current.get("cloud_id"),
            agent_type="human",
        )

        # moteur de jeu
        self.engine = GameEngine(self.env, self.pacman, self.ghosts, self.recorder)

    # ------------------------------------------------------------------
    #  gestion des labyrinthes (api + stockage local)
    # ------------------------------------------------------------------

    def _update_target_size(self, delta: int):
        self.target_size = max(11, min(41, self.target_size + delta))
        self._create_new_maze()

    def _set_target_loop(self, value: int):
        self.target_loop = value
        self._create_new_maze()

    def _load_index(self, index: int):
        self.maze_ids = self.repo.list_ids()
        if not self.maze_ids:
            return
        self.current_index = max(0, min(index, len(self.maze_ids) - 1))
        self.current = self.repo.get_maze(self.maze_ids[self.current_index])
        self.target_size = self.current["width"]
        self.target_loop = self.current["loop_percent"]
        self._start_game()

    def _create_new_maze(self):
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
            print(f"API error: {e}. Generating locally...")
            maze = generate_pacman_maze(self.target_size, self.target_size, self.target_loop)
            width = len(maze[0])
            height = len(maze)
            new_id = self.repo.save_maze(maze, width, height, self.target_loop, None)

        self.maze_ids = self.repo.list_ids()
        self.current_index = self.maze_ids.index(new_id)
        self.current = self.repo.get_maze(new_id)
        self._start_game()

    def _rate_current_maze(self, rating):
        cloud_id = self.current.get("cloud_id")
        if not cloud_id:
            print("Cannot rate: this maze has no cloud ID.")
            return
        try:
            url = f"{API_URL}/maze/{cloud_id}/rate"
            response = requests.post(url, json={"rating": rating}, timeout=3)
            if response.status_code == 200:
                print(f"Maze {cloud_id} rated: {rating}/5 !")
            else:
                print(f"Rating error: {response.json()}")
        except Exception as e:
            print(f"Rating send error: {e}")

    def _save_recording(self):
        # sauvegarde l'enregistrement de la partie
        RECORDINGS_DIR.mkdir(exist_ok=True)
        filename = f"game_{int(time.time())}.json"
        filepath = RECORDINGS_DIR / filename
        self.recorder.save(filepath)
        print(f"Game saved to {filepath}")

    # ------------------------------------------------------------------
    #  boucle principale
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    running = self._handle_key(event, running)

            # avancer la logique du jeu
            self.engine.tick()

            # rendu graphique
            self.renderer.render(self.engine)
            self.clock.tick(60)

        # sauvegarder l'enregistrement en quittant
        if self.recorder.total_frames > 0:
            self._save_recording()

        pygame.quit()

    def _handle_key(self, event, running):
        char = event.unicode

        # déplacement (entrée de l'agent pacman)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.pacman.set_direction(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.pacman.set_direction(1, 0)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.pacman.set_direction(0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pacman.set_direction(0, 1)

        # nouveau labyrinthe
        elif event.key == pygame.K_n:
            self._create_new_maze()

        # relancer le labyrinthe courant
        elif event.key == pygame.K_r:
            self._start_game()

        # parcourir les labyrinthes
        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_p, pygame.K_PAGEUP) or char == "[":
            self._load_index(self.current_index - 1)
        elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_m, pygame.K_PAGEDOWN) or char == "]":
            self._load_index(self.current_index + 1)

        # taille du labyrinthe
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS) or char == "-":
            self._update_target_size(-2)
        elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS) or char == "+":
            self._update_target_size(2)

        # pourcentage de boucles (pavé numérique)
        elif event.key == pygame.K_KP0:
            self._set_target_loop(0)
        elif event.key == pygame.K_KP2:
            self._set_target_loop(25)
        elif event.key == pygame.K_KP4:
            self._set_target_loop(40)

        # noter le labyrinthe (F1-F5)
        elif event.key == pygame.K_F1:
            self._rate_current_maze(1)
        elif event.key == pygame.K_F2:
            self._rate_current_maze(2)
        elif event.key == pygame.K_F3:
            self._rate_current_maze(3)
        elif event.key == pygame.K_F4:
            self._rate_current_maze(4)
        elif event.key == pygame.K_F5:
            self._rate_current_maze(5)

        # quitter
        elif event.key == pygame.K_ESCAPE:
            return False

        return running


def main():
    game = LocalPacmanGame()
    game.run()


if __name__ == "__main__":
    main()
