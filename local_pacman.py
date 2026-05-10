import json
import sqlite3
import time
from pathlib import Path

import pygame
import requests

from Proto.maze_Prim_loops import generate_pacman_maze
from game.environment import Environment
from game.agents import (
    HumanAgent, AIPacmanAgent, MinimaxPacmanAgent, ExpectimaxPacmanAgent,
    BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost, GhostAgent
)
from game.engine import GameEngine
from game.recorder import GameRecorder
from game.renderer import PacmanRenderer
from game.framework import ReplayPacmanAgent, pacman_route_from_recording_frames


DB_PATH = Path(__file__).parent / "mazes.db"
API_URL = "https://ter-s2-d-85u5.onrender.com"
RECORDINGS_DIR = Path(__file__).parent / "recordings"

# --- configuration des niveaux ---
LEVEL_CONFIG = {
    1: {
        "label": "Facile",
        "pathfinder": "bfs",
        "prediction_steps": 0,
        "ghost_speed": 14,        # 1 mouvement toutes les 14 ticks (très lent)
        "pacman_speed": 12,       # pac-man aussi plus lent
        "frightened_duration": 600,  # 10s de protection
        "caged_ticks": 600,       # 10s en cage
    },
    2: {
        "label": "Moyen",
        "pathfinder": "astar",
        "prediction_steps": 0,
        "ghost_speed": 8,         # vitesse normale
        "pacman_speed": 8,
        "frightened_duration": 360,  # 6s
        "caged_ticks": 420,       # 7s
    },
    3: {
        "label": "Difficile",
        "pathfinder": "astar",
        "prediction_steps": 3,    # blinky anticipe 3 cases
        "ghost_speed": 6,         # plus rapide
        "pacman_speed": 8,
        "frightened_duration": 200,  # ~3s
        "caged_ticks": 180,       # 3s
    },
}


def show_ai_pacman_menu(screen, clock):
    """Menu de choix d'algorithme pour le mode Pac-Man IA.
    Retourne 'bfs', 'astar', 'avoid', 'minimax', 'expectimax' ou None."""
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_opt   = pygame.font.SysFont("monospace", 24, bold=True)
    font_desc  = pygame.font.SysFont("monospace", 15)

    options = [
        ("B", "bfs",        (80,  180, 255), "BFS",        "Parcours en largeur – optimal et sûr"),
        ("A", "astar",      (130, 230,  80), "A*",         "A* heuristique – plus rapide sur grands labyrinthes"),
        ("E", "avoid",      (255, 180,  40), "Évitement",  "BFS + évitement des fantômes proches"),
        ("M", "minimax",    (220,  80, 220), "Minimax+AB", "Minimax avec élagage Alpha-Beta (adversarial)"),
        ("X", "expectimax", (80,  220, 200), "Expectimax", "Expectimax – fantômes modélisés comme agents probabilistes"),
    ]
    key_map = {
        pygame.K_b: "bfs",
        pygame.K_a: "astar",
        pygame.K_e: "avoid",
        pygame.K_m: "minimax",
        pygame.K_x: "expectimax",
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    return key_map[event.key]
                elif event.key == pygame.K_ESCAPE:
                    return None

        W, H = screen.get_size()
        screen.fill((0, 0, 0))

        title = font_title.render("Pac-Man IA – Choisir l'algo", True, (255, 220, 40))
        screen.blit(title, (W // 2 - title.get_width() // 2, 45))

        for i, (key, _, color, name, desc) in enumerate(options):
            y = 115 + i * 90
            box = pygame.Rect(W // 2 - 310, y, 620, 78)
            pygame.draw.rect(screen, (15, 15, 15), box, border_radius=10)
            pygame.draw.rect(screen, color, box, width=2, border_radius=10)
            label = font_opt.render(f"[{key}]  {name}", True, color)
            screen.blit(label, (box.x + 18, box.y + 10))
            d = font_desc.render(desc, True, (200, 200, 200))
            screen.blit(d, (box.x + 18, box.y + 46))

        hint = font_desc.render("ESC pour revenir", True, (80, 80, 80))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 40))

        pygame.display.flip()
        clock.tick(30)


def show_replay_browser(screen, clock):
    """Affiche la liste des enregistrements depuis MongoDB.
    Retourne le chemin local (str) du fichier téléchargé, ou None pour annuler."""
    import threading, datetime
    font_title = pygame.font.SysFont("monospace", 38, bold=True)
    font_item  = pygame.font.SysFont("monospace", 20)
    font_hint  = pygame.font.SysFont("monospace", 16)

    # --- requête dans un thread pour ne pas bloquer pygame ---
    result = {"entries": None, "error": None}

    def _fetch():
        try:
            resp = requests.get(f"{API_URL}/recordings", timeout=60)
            if resp.status_code == 200:
                entries = []
                for rec in resp.json().get("recordings", []):
                    cid   = rec.get("id", "")
                    meta  = rec.get("metadata", {})
                    score = meta.get("score_final", "?")
                    agent = meta.get("agent_type", "?")
                    ts    = meta.get("recorded_at", 0)
                    nb    = rec.get("total_frames", meta.get("nb_frames", "?"))
                    date_str = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M") if ts else "?"
                    label = f"{date_str}   {agent:<16}  score {score:<6}  frames {nb}"
                    entries.append({"cloud_id": cid, "label": label})
                result["entries"] = entries
            else:
                result["error"] = f"Erreur serveur : {resp.status_code}"
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=_fetch, daemon=True)
    t.start()

    # --- écran de chargement animé pendant la requête ---
    dots = 0
    dot_timer = 0
    while t.is_alive():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
        W, H = screen.get_size()
        screen.fill((0, 0, 0))
        dot_timer += 1
        if dot_timer % 20 == 0:
            dots = (dots + 1) % 4
        loading = font_title.render("Chargement" + "." * dots, True, (255, 220, 40))
        screen.blit(loading, (W // 2 - loading.get_width() // 2, H // 2 - 30))
        sub = font_hint.render("Connexion à MongoDB en cours…", True, (120, 120, 120))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))
        hint = font_hint.render("ESC pour annuler", True, (60, 60, 60))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 50))
        pygame.display.flip()
        clock.tick(30)

    entries = result["entries"] or []
    error   = result["error"]

    if not entries:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    waiting = False
            W, H = screen.get_size()
            screen.fill((0, 0, 0))
            if error:
                msg = font_title.render("Erreur de connexion", True, (220, 80, 80))
                screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 40))
                err_surf = font_hint.render(error[:70], True, (200, 100, 100))
                screen.blit(err_surf, (W // 2 - err_surf.get_width() // 2, H // 2 + 5))
            else:
                msg = font_title.render("Aucun enregistrement disponible", True, (220, 80, 80))
                screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 20))
            hint = font_hint.render("Appuyez sur une touche pour revenir", True, (80, 80, 80))
            screen.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 50))
            pygame.display.flip()
            clock.tick(30)
        return None

    selected = 0
    scroll_offset = 0
    ROW_H = 48
    VISIBLE = 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(0, selected - 1)
                    if selected < scroll_offset:
                        scroll_offset = selected
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = min(len(entries) - 1, selected + 1)
                    if selected >= scroll_offset + VISIBLE:
                        scroll_offset = selected - VISIBLE + 1
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # télécharger depuis MongoDB et jouer
                    return _download_cloud_recording(entries[selected]["cloud_id"], screen, clock)

        W, H = screen.get_size()
        screen.fill((0, 0, 0))

        title = font_title.render("Replays disponibles", True, (255, 220, 40))
        screen.blit(title, (W // 2 - title.get_width() // 2, 20))

        list_top = 80
        for i in range(VISIBLE):
            idx = scroll_offset + i
            if idx >= len(entries):
                break
            e = entries[idx]
            y = list_top + i * ROW_H
            box = pygame.Rect(W // 2 - 380, y, 760, ROW_H - 4)
            is_sel = (idx == selected)
            bg     = (30, 50, 80) if is_sel else (15, 15, 15)
            border = (100, 160, 255) if is_sel else (50, 50, 50)
            pygame.draw.rect(screen, bg, box, border_radius=6)
            pygame.draw.rect(screen, border, box, width=1, border_radius=6)
            color = (200, 230, 255) if is_sel else (180, 180, 180)
            text = font_item.render(e["label"], True, color)
            screen.blit(text, (box.x + 8, box.y + (ROW_H - 4 - text.get_height()) // 2))

        if len(entries) > VISIBLE:
            bar_h = max(20, int((H - list_top - 60) * VISIBLE / len(entries)))
            bar_y = list_top + int((H - list_top - 60 - bar_h) * scroll_offset / max(1, len(entries) - VISIBLE))
            pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(W - 16, list_top, 8, H - list_top - 60))
            pygame.draw.rect(screen, (160, 160, 160), pygame.Rect(W - 16, bar_y, 8, bar_h))

        count_txt = font_hint.render(
            f"{len(entries)} replay(s) sur MongoDB – ↑↓ naviguer, Entrée sélectionner, ESC annuler",
            True, (90, 90, 90)
        )
        screen.blit(count_txt, (W // 2 - count_txt.get_width() // 2, H - 36))
        pygame.display.flip()
        clock.tick(30)


def _download_cloud_recording(cloud_id, screen=None, clock=None):
    """Télécharge un enregistrement cloud et le sauvegarde localement. Retourne le chemin local."""
    import threading
    result = {"path": None, "error": None}

    def _fetch():
        try:
            resp = requests.get(f"{API_URL}/recording/{cloud_id}", timeout=60)
            resp.raise_for_status()
            data = resp.json()
            RECORDINGS_DIR.mkdir(exist_ok=True)
            ts = data.get("metadata", {}).get("recorded_at", int(time.time()))
            filepath = RECORDINGS_DIR / f"game_{ts}_cloud.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)
            result["path"] = str(filepath)
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=_fetch, daemon=True)
    t.start()

    if screen and clock:
        font = pygame.font.SysFont("monospace", 32, bold=True)
        hint = pygame.font.SysFont("monospace", 16)
        dots = 0
        timer = 0
        while t.is_alive():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
            W, H = screen.get_size()
            screen.fill((0, 0, 0))
            timer += 1
            if timer % 20 == 0:
                dots = (dots + 1) % 4
            msg = font.render("Téléchargement" + "." * dots, True, (255, 220, 40))
            screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 20))
            sub = hint.render("Récupération depuis MongoDB…", True, (120, 120, 120))
            screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))
            pygame.display.flip()
            clock.tick(30)
    else:
        t.join()

    if result["error"]:
        print(f"Erreur téléchargement cloud: {result['error']}")
    return result["path"]


def show_main_menu(screen, clock):
    """Affiche le menu principal. Retourne un dict d'action ou None pour quitter."""
    font_title = pygame.font.SysFont("monospace", 48, bold=True)
    font_level = pygame.font.SysFont("monospace", 26, bold=True)
    font_desc  = pygame.font.SysFont("monospace", 17)

    LEVEL_COLORS = {1: (80, 220, 80), 2: (255, 165, 0), 3: (220, 50, 50)}
    level_descriptions = {
        1: ("Facile",    "BFS · fantômes lents · bonus 10s"),
        2: ("Moyen",     "A* · vitesse normale · bonus 6s"),
        3: ("Difficile", "A* prédictif · fantômes rapides · bonus 3s"),
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return {"action": "play", "level": 1}
                elif event.key == pygame.K_2:
                    return {"action": "play", "level": 2}
                elif event.key == pygame.K_3:
                    return {"action": "play", "level": 3}
                elif event.key == pygame.K_4:
                    return {"action": "ai_pacman"}
                elif event.key == pygame.K_5:
                    return {"action": "replay_browser"}
                elif event.key == pygame.K_ESCAPE:
                    return None

        W, H = screen.get_size()
        screen.fill((0, 0, 0))

        title = font_title.render("PAC-MAN  IA", True, (255, 220, 40))
        screen.blit(title, (W // 2 - title.get_width() // 2, 40))

        sub = font_desc.render("Choisissez un mode de jeu", True, (160, 160, 160))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 108))

        # --- niveaux joueur (1/2/3) ---
        for i, (num, (name, desc)) in enumerate(level_descriptions.items()):
            y = 145 + i * 85
            color = LEVEL_COLORS[num]
            box = pygame.Rect(W // 2 - 280, y, 560, 74)
            pygame.draw.rect(screen, (20, 20, 20), box, border_radius=8)
            pygame.draw.rect(screen, color, box, width=2, border_radius=8)
            label = font_level.render(f"{num} -  {name}", True, color)
            screen.blit(label, (box.x + 18, box.y + 10))
            d = font_desc.render(desc, True, (200, 200, 200))
            screen.blit(d, (box.x + 18, box.y + 46))

        # --- Pac-Man IA (4) ---
        y4 = 145 + 3 * 85 + 10
        box4 = pygame.Rect(W // 2 - 280, y4, 560, 58)
        pygame.draw.rect(screen, (20, 20, 30), box4, border_radius=8)
        pygame.draw.rect(screen, (100, 160, 255), box4, width=2, border_radius=8)
        screen.blit(font_level.render("4 -  Pac-Man IA", True, (100, 160, 255)), (box4.x + 18, box4.y + 8))
        screen.blit(font_desc.render("L'IA joue Pac-Man  (BFS / A* / Évitement)", True, (200, 200, 200)), (box4.x + 18, box4.y + 38))

        # --- Voir les replays (5) ---
        y5 = y4 + 68
        box5 = pygame.Rect(W // 2 - 280, y5, 560, 58)
        pygame.draw.rect(screen, (20, 20, 30), box5, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 255), box5, width=2, border_radius=8)
        screen.blit(font_level.render("5 -  Voir les replays", True, (180, 100, 255)), (box5.x + 18, box5.y + 8))
        screen.blit(font_desc.render("Parcourir et rejouer les parties enregistrées", True, (200, 200, 200)), (box5.x + 18, box5.y + 38))

        hint = font_desc.render("ESC pour quitter", True, (80, 80, 80))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 40))

        pygame.display.flip()
        clock.tick(30)


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
    def __init__(self, screen=None, clock=None, level=1):
        pygame.init()
        pygame.display.set_caption("Pac-Man - TER S2")

        self.level = level

        self.repo = MazeRepository(DB_PATH)
        self.repo.ensure_one_default()
        self.maze_ids = self.repo.list_ids()
        self.current_index = len(self.maze_ids) - 1
        self.current = self.repo.get_maze(self.maze_ids[self.current_index])

        self.window_w = 860
        self.window_h = 720
        if screen is not None:
            self.screen = screen
        else:
            self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
        if clock is not None:
            self.clock = clock
        else:
            self.clock = pygame.time.Clock()

        self.target_size = 21
        self.target_loop = self.current["loop_percent"]

        self.renderer = PacmanRenderer(self.screen, self.window_w, self.window_h)

        # mode du jeu : "normal", "solo", "replay"
        self.game_mode = "normal"
        self.replay_ai = "bfs"
        self.capture_tick = None
        self.solo_recording_path = None
        self.rating_message = None
        self.rating_message_time = 0

        self._start_game()

    # ------------------------------------------------------------------
    #  lancement du jeu
    # ------------------------------------------------------------------

    def _start_game(self):
        # initialise le moteur de jeu avec le labyrinthe courant
        self.game_mode = "normal"
        self.capture_tick = None
        maze = self.current["maze"]
        self.env = Environment(maze)

        # pacman apparaît en bas
        pac_pos = self.env.find_pacman_spawn()
        self.pacman = HumanAgent(*pac_pos)

        # les fantômes apparaissent au centre
        ghost_spawns = self.env.find_ghost_spawns(4)
        w, h = self.env.width, self.env.height
        ghost_classes = [BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost]
        cfg = LEVEL_CONFIG[self.level]
        self.ghosts = []
        for i, cls in enumerate(ghost_classes):
            if i < len(ghost_spawns):
                gx, gy = ghost_spawns[i]
            else:
                gx, gy = ghost_spawns[0]
            if cls == BlinkyGhost:
                self.ghosts.append(cls(gx, gy, w, h,
                    pathfinder=cfg["pathfinder"],
                    prediction_steps=cfg["prediction_steps"]))
            else:
                self.ghosts.append(cls(gx, gy, w, h,
                    pathfinder=cfg["pathfinder"]))

        # enregistreur
        self.recorder = GameRecorder()
        self.recorder.set_metadata(
            maze, w, h,
            cloud_id=self.current.get("cloud_id"),
            agent_type="human",
            level=self.level,
        )

        # moteur de jeu
        self.engine = GameEngine(self.env, self.pacman, self.ghosts, self.recorder)

        # appliquer la configuration du niveau
        cfg = LEVEL_CONFIG[self.level]
        self.engine.pacman_speed = cfg["pacman_speed"]
        self.engine.ghost_speed = cfg["ghost_speed"]
        self.engine.frightened_duration = cfg["frightened_duration"]
        self.engine.ghost_mode_timer = cfg["caged_ticks"]

    def _start_solo_game(self):
        # lance une partie sans fantômes pour enregistrer le trajet
        self.game_mode = "solo"
        self.capture_tick = None
        maze = self.current["maze"]
        self.env = Environment(maze)

        pac_pos = self.env.find_pacman_spawn()
        self.pacman = HumanAgent(*pac_pos)
        self.ghosts = []

        self.recorder = GameRecorder()
        w, h = self.env.width, self.env.height
        self.recorder.set_metadata(
            maze, w, h,
            cloud_id=self.current.get("cloud_id"),
            agent_type="human_solo",
            level=self.level,
        )
        self.engine = GameEngine(self.env, self.pacman, self.ghosts, self.recorder)
        print("mode solo : explorez le labyrinthe sans fantômes (enregistrement en cours)")

    def _start_ai_pacman_game(self, strategy="bfs"):
        """Lance une partie où l'IA contrôle Pac-Man (pas de fantômes en cage)."""
        self.game_mode = "ai_pacman"
        self.capture_tick = None
        maze = self.current["maze"]
        self.env = Environment(maze)

        pac_pos = self.env.find_pacman_spawn()
        if strategy == "minimax":
            self.pacman = MinimaxPacmanAgent(*pac_pos, depth=0)
        elif strategy == "expectimax":
            self.pacman = ExpectimaxPacmanAgent(*pac_pos, depth=0)
        else:
            self.pacman = AIPacmanAgent(*pac_pos, strategy=strategy)
        self.ai_strategy = strategy

        ghost_spawns = self.env.find_ghost_spawns(4)
        w, h = self.env.width, self.env.height
        cfg = LEVEL_CONFIG[self.level]
        ghost_classes = [BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost]
        self.ghosts = []
        for i, cls in enumerate(ghost_classes):
            gx, gy = ghost_spawns[i] if i < len(ghost_spawns) else ghost_spawns[0]
            if cls == BlinkyGhost:
                self.ghosts.append(cls(gx, gy, w, h,
                    pathfinder=cfg["pathfinder"],
                    prediction_steps=cfg["prediction_steps"]))
            else:
                self.ghosts.append(cls(gx, gy, w, h,
                    pathfinder=cfg["pathfinder"]))

        self.recorder = GameRecorder()
        self.recorder.set_metadata(
            maze, w, h,
            cloud_id=self.current.get("cloud_id"),
            agent_type=f"ai_{strategy}",
            level=self.level,
        )
        self.engine = GameEngine(self.env, self.pacman, self.ghosts, self.recorder)
        cfg = LEVEL_CONFIG[self.level]
        self.engine.pacman_speed = cfg["pacman_speed"]
        self.engine.ghost_speed = cfg["ghost_speed"]
        self.engine.frightened_duration = cfg["frightened_duration"]
        self.engine.ghost_mode_timer = cfg["caged_ticks"]
        print(f"mode IA Pac-Man : stratégie {strategy}, niveau {cfg['label']}")

    def _start_replay_game(self, pathfinder="bfs", filepath=None):
        # charge un enregistrement (filepath ou le dernier) et le rejoue avec des fantômes
        RECORDINGS_DIR.mkdir(exist_ok=True)
        if filepath is not None:
            rec_path = Path(filepath)
        else:
            files = sorted(RECORDINGS_DIR.glob("game_*.json"))
            if not files:
                print("aucun enregistrement trouvé dans recordings/")
                return
            rec_path = files[-1]
        loaded = GameRecorder.load(rec_path)
        route = pacman_route_from_recording_frames(loaded.frames)
        if len(route) < 2:
            print("enregistrement trop court pour rejouer")
            return

        self.game_mode = "replay"
        self.replay_ai = pathfinder
        self.capture_tick = None

        maze = loaded.metadata.get("maze")
        if not maze:
            print("enregistrement invalide (pas de labyrinthe)")
            return
        self.env = Environment(maze)

        self.pacman = ReplayPacmanAgent(route)
        ghost_spawns = self.env.find_ghost_spawns(4)
        w, h = self.env.width, self.env.height
        ghost_classes = [BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost]
        self.ghosts = []
        for i, cls in enumerate(ghost_classes):
            gx, gy = ghost_spawns[i] if i < len(ghost_spawns) else ghost_spawns[0]
            self.ghosts.append(cls(gx, gy, w, h, pathfinder=pathfinder))

        self.recorder = GameRecorder()
        self.recorder.set_metadata(
            maze, w, h,
            cloud_id=loaded.metadata.get("cloud_id"),
            agent_type=f"replay_{pathfinder}",
            level=loaded.metadata.get("level"),
        )
        self.engine = GameEngine(self.env, self.pacman, self.ghosts, self.recorder)
        self.engine.no_death = True   # les fantômes ne tuent pas pac-man en replay
        self.solo_recording_path = str(rec_path)
        print(f"mode replay : {rec_path.name} avec IA {pathfinder}")

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
            self.rating_message = "Pas de cloud ID - appuyer N d'abord"
            self.rating_message_time = time.time()
            print("Cannot rate: this maze has no cloud ID.")
            return
        try:
            url = f"{API_URL}/maze/{cloud_id}/rate"
            response = requests.post(url, json={"rating": rating}, timeout=3)
            if response.status_code == 200:
                self.rating_message = f"Note {rating}/5 envoyee !"
                self.rating_message_time = time.time()
                print(f"Maze {cloud_id} rated: {rating}/5 !")
            else:
                err = response.json().get("error", "inconnue")
                self.rating_message = f"Erreur {response.status_code}: {err[:40]}"
                self.rating_message_time = time.time()
                print(f"Rating error {response.status_code}: {err}")
        except Exception as e:
            self.rating_message = f"Erreur connexion"
            self.rating_message_time = time.time()
            print(f"Rating send error: {e}")

    def _save_recording(self):
        # sauvegarde l'enregistrement de la partie localement puis upload
        RECORDINGS_DIR.mkdir(exist_ok=True)
        filename = f"game_{int(time.time())}.json"
        filepath = RECORDINGS_DIR / filename
        self.recorder.save(filepath)
        print(f"Game saved to {filepath}")
        self._upload_recording(filepath)

    def _upload_recording(self, filepath):
        """Envoie l'enregistrement au serveur et stocke son cloud_id dans le fichier local."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            response = requests.post(f"{API_URL}/recording", json=data, timeout=30)
            if response.status_code == 200:
                cloud_id = response.json().get("id")
                data["cloud_id"] = cloud_id
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                print(f"Recording uploaded: {cloud_id}")
            else:
                print(f"Upload failed ({response.status_code})")
        except Exception as e:
            print(f"Upload error: {e}")

    # ------------------------------------------------------------------
    #  boucle principale
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.VIDEORESIZE:
                    self.window_w, self.window_h = event.w, event.h
                    self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
                    self.renderer = PacmanRenderer(self.screen, self.window_w, self.window_h)

                if event.type == pygame.KEYDOWN:
                    running = self._handle_key(event, running)

            # avancer la logique du jeu
            self.engine.tick()

            # détecter le tick de capture en mode replay
            if self.game_mode == "replay" and self.capture_tick is None:
                if self.engine.game_over:
                    self.capture_tick = self.engine.tick_count

            # effacer le message de notation apres 3 secondes
            rating_msg = None
            if self.rating_message and (time.time() - self.rating_message_time) < 3:
                rating_msg = self.rating_message

            # rendu graphique
            self.renderer.render(
                self.engine,
                game_mode=self.game_mode,
                capture_tick=self.capture_tick,
                replay_ai=self.replay_ai,
                rating_message=rating_msg,
            )
            self.clock.tick(60)

        # sauvegarder l'enregistrement en quittant
        if self.recorder.total_frames > 0:
            self._save_recording()

        pygame.quit()

    def _handle_key(self, event, running):
        char = event.unicode

        # deplacement (entree de l'agent pacman - seulement en mode humain)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            if hasattr(self.pacman, 'set_direction'):
                self.pacman.set_direction(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if hasattr(self.pacman, 'set_direction'):
                self.pacman.set_direction(1, 0)
        elif event.key in (pygame.K_UP, pygame.K_w):
            if hasattr(self.pacman, 'set_direction'):
                self.pacman.set_direction(0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if hasattr(self.pacman, 'set_direction'):
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

        # noter le labyrinthe (touches 0-5 : 0=bad, 5=good)
        elif event.key == pygame.K_0:
            self._rate_current_maze(0)
        elif event.key in (pygame.K_3, pygame.K_F1):
            self._rate_current_maze(1)
        elif event.key in (pygame.K_4, pygame.K_F2):
            self._rate_current_maze(2)
        elif event.key in (pygame.K_5, pygame.K_F3):
            self._rate_current_maze(3)
        elif event.key in (pygame.K_6, pygame.K_F4):
            self._rate_current_maze(4)
        elif event.key in (pygame.K_7, pygame.K_F5):
            self._rate_current_maze(5)

        # mode solo (sans fantomes) - touche 1 ou F6
        elif event.key in (pygame.K_1, pygame.K_F6):
            # sauvegarder la partie en cours avant de passer en solo
            if self.recorder.total_frames > 0:
                self._save_recording()
            self._start_solo_game()

        # mode replay (avec fantomes et IA) - touche 2 ou F7
        elif event.key in (pygame.K_2, pygame.K_F7):
            # sauvegarder la partie solo en cours avant le replay
            if self.recorder.total_frames > 0:
                self._save_recording()
            algos = ["bfs", "astar", "dfs", "ucs", "mcts"]
            idx = algos.index(self.replay_ai) if self.replay_ai in algos else -1
            self.replay_ai = algos[(idx + 1) % len(algos)]
            self._start_replay_game(self.replay_ai)

        # quitter
        elif event.key == pygame.K_ESCAPE:
            return False

        return running


def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man - TER S2")
    screen = pygame.display.set_mode((860, 720), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    while True:
        action = show_main_menu(screen, clock)
        if action is None:
            break

        if action["action"] == "play":
            game = LocalPacmanGame(screen=screen, clock=clock, level=action["level"])
            game.run()

        elif action["action"] == "ai_pacman":
            strategy = show_ai_pacman_menu(screen, clock)
            if strategy is not None:
                game = LocalPacmanGame(screen=screen, clock=clock, level=1)
                game._start_ai_pacman_game(strategy=strategy)
                game.run()

        elif action["action"] == "replay_browser":
            filepath = show_replay_browser(screen, clock)
            if filepath is not None:
                game = LocalPacmanGame(screen=screen, clock=clock, level=1)
                game._start_replay_game(filepath=filepath)
                game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
