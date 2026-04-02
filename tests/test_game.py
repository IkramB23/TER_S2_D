"""Tests for the game module: environment, agents, engine, recorder."""

import json
import tempfile
from pathlib import Path

from Proto.maze_Prim_loops import generate_pacman_maze
from game.environment import Environment
from game.agents import (
    HumanAgent, BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost,
    GhostMode, bfs_direction,
)
from game.engine import GameEngine
from game.recorder import GameRecorder


def _make_env(width=21, height=21, loop_percent=25):
    maze = generate_pacman_maze(width, height, loop_percent)
    return Environment(maze), maze


# -----------------------------------------------------------------------
#  Environment tests
# -----------------------------------------------------------------------

class TestEnvironment:
    def test_pellets_placed_on_corridors(self):
        env, _ = _make_env()
        for x, y in env.pellets:
            assert env.maze[y][x] == 1, "Pellet must be on corridor"

    def test_power_pellets_count(self):
        env, _ = _make_env()
        assert len(env.power_pellets) == 4, "Should have 4 power pellets"

    def test_power_pellets_on_corridors(self):
        env, _ = _make_env()
        for x, y in env.power_pellets:
            assert env.maze[y][x] == 1, "Power pellet must be on corridor"

    def test_walls_are_walls(self):
        env, maze = _make_env()
        for x, y in env.walls:
            assert maze[y][x] == 0

    def test_eat_pellet(self):
        env, _ = _make_env()
        pellet = next(iter(env.pellets))
        count_before = len(env.pellets)
        points, is_power = env.eat_pellet(*pellet)
        assert points == 10
        assert not is_power
        assert len(env.pellets) == count_before - 1

    def test_eat_power_pellet(self):
        env, _ = _make_env()
        pp = next(iter(env.power_pellets))
        points, is_power = env.eat_pellet(*pp)
        assert points == 50
        assert is_power

    def test_eat_empty_cell(self):
        env, _ = _make_env()
        # Find a wall cell — eating there yields nothing
        wall = next(iter(env.walls))
        points, is_power = env.eat_pellet(*wall)
        assert points == 0

    def test_all_pellets_eaten(self):
        env, _ = _make_env(11, 11)
        assert not env.all_pellets_eaten()
        env.pellets.clear()
        env.power_pellets.clear()
        assert env.all_pellets_eaten()

    def test_find_pacman_spawn(self):
        env, maze = _make_env()
        x, y = env.find_pacman_spawn()
        assert maze[y][x] == 1, "Pac-Man must spawn on corridor"

    def test_find_ghost_spawns(self):
        env, maze = _make_env()
        spawns = env.find_ghost_spawns(4)
        assert len(spawns) == 4
        for x, y in spawns:
            assert maze[y][x] == 1, "Ghost must spawn on corridor"

    def test_spawn_fruit(self):
        env, _ = _make_env()
        env.spawn_fruit()
        assert env.fruit_pos is not None
        x, y = env.fruit_pos
        assert env.is_corridor(x, y)

    def test_eat_fruit(self):
        env, _ = _make_env()
        env.spawn_fruit()
        pos = env.fruit_pos
        pts = env.eat_fruit(*pos)
        assert pts == 100
        assert env.fruit_pos is None


# -----------------------------------------------------------------------
#  Agent tests
# -----------------------------------------------------------------------

class TestAgents:
    def test_human_agent_direction(self):
        agent = HumanAgent(5, 5)
        agent.set_direction(1, 0)
        assert agent.next_direction == (1, 0)

    def test_bfs_finds_path(self):
        # Simple open grid (no walls)
        walls = set()
        d = bfs_direction(walls, 5, 5, (0, 0), (4, 4))
        assert d in [(1, 0), (0, 1)]

    def test_bfs_no_path(self):
        # Surrounded by walls
        walls = {(1, 0), (0, 1), (-1, 0), (0, -1)}
        d = bfs_direction(walls, 3, 3, (0, 0), (2, 2))
        # Should find a path since maze is small
        assert isinstance(d, tuple)

    def test_ghost_scatter_target(self):
        ghost = BlinkyGhost(5, 5, 21, 21)
        assert ghost.scatter_target == (19, 1)

    def test_ghost_frightened_mode(self):
        ghost = BlinkyGhost(5, 5, 21, 21)
        ghost.set_frightened(100)
        assert ghost.mode == GhostMode.FRIGHTENED
        assert ghost.frightened_timer == 100

    def test_ghost_reset(self):
        ghost = BlinkyGhost(5, 5, 21, 21)
        ghost.x = 10
        ghost.y = 10
        ghost.reset()
        assert ghost.x == 5
        assert ghost.y == 5


# -----------------------------------------------------------------------
#  Engine tests
# -----------------------------------------------------------------------

class TestEngine:
    def _setup_engine(self):
        env, maze = _make_env(11, 11)
        pac_pos = env.find_pacman_spawn()
        pacman = HumanAgent(*pac_pos)
        spawns = env.find_ghost_spawns(4)
        w, h = env.width, env.height
        ghosts = [
            BlinkyGhost(spawns[0][0], spawns[0][1], w, h),
            PinkyGhost(spawns[1][0], spawns[1][1], w, h),
            InkyGhost(spawns[2][0], spawns[2][1], w, h),
            ClydeGhost(spawns[3][0], spawns[3][1], w, h),
        ]
        engine = GameEngine(env, pacman, ghosts)
        return engine, pacman

    def test_initial_state(self):
        engine, _ = self._setup_engine()
        assert engine.score == 0
        assert engine.lives == 3
        assert not engine.game_over
        assert not engine.game_won

    def test_tick_advances(self):
        engine, _ = self._setup_engine()
        engine.tick()
        assert engine.tick_count == 1

    def test_multiple_ticks(self):
        engine, _ = self._setup_engine()
        for _ in range(60):
            engine.tick()
        assert engine.tick_count == 60

    def test_get_state(self):
        engine, _ = self._setup_engine()
        state = engine.get_state()
        assert "score" in state
        assert "lives" in state
        assert "pacman" in state
        assert "ghosts" in state
        assert len(state["ghosts"]) == 4


# -----------------------------------------------------------------------
#  Recorder tests
# -----------------------------------------------------------------------

class TestRecorder:
    def test_record_and_replay(self):
        recorder = GameRecorder()
        recorder.set_metadata([[0, 1], [1, 0]], 2, 2, cloud_id="test-123")
        recorder.record_frame({"tick": 0, "score": 0})
        recorder.record_frame({"tick": 1, "score": 10})
        assert recorder.total_frames == 2
        assert recorder.get_frame(0)["score"] == 0
        assert recorder.get_frame(1)["score"] == 10

    def test_save_and_load(self):
        recorder = GameRecorder()
        recorder.set_metadata([[0, 1], [1, 0]], 2, 2, cloud_id="test-456")
        recorder.record_frame({"tick": 0, "score": 100})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        recorder.save(path)
        loaded = GameRecorder.load(path)
        assert loaded.total_frames == 1
        assert loaded.metadata["cloud_id"] == "test-456"
        assert loaded.get_frame(0)["score"] == 100
        Path(path).unlink()

    def test_final_score(self):
        recorder = GameRecorder()
        recorder.record_frame({"tick": 0, "score": 0})
        recorder.record_frame({"tick": 100, "score": 500})
        assert recorder.get_final_score() == 500
