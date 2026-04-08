import tempfile
from pathlib import Path

from game.agents import (
    astar_direction,
    bfs_direction,
    dfs_direction,
    ucs_direction,
    mcts_direction,
    predict_pacman_position,
    HumanAgent,
)
from game.environment import Environment
from game.framework import (
    compare_day6_strategies,
    compare_day6_strategies_on_recording,
    compare_strategies_over_seeds,
    pacman_route_from_recording_frames,
)
from game.recorder import GameRecorder


def _simple_env():
    maze = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    return Environment(maze), maze


def test_astar_direction_returns_valid_step():
    env, _ = _simple_env()
    step = astar_direction(env.walls, env.width, env.height, (1, 1), (3, 3))
    assert step in [(1, 0), (0, 1)]


def test_dfs_direction_returns_valid_step():
    env, _ = _simple_env()
    step = dfs_direction(env.walls, env.width, env.height, (1, 1), (3, 3))
    assert step in [(1, 0), (0, 1)]


def test_ucs_direction_returns_valid_step():
    env, _ = _simple_env()
    step = ucs_direction(env.walls, env.width, env.height, (1, 1), (3, 3))
    assert step in [(1, 0), (0, 1)]


def test_mcts_direction_returns_valid_step():
    env, _ = _simple_env()
    step = mcts_direction(env.walls, env.width, env.height, (1, 1), (3, 3))
    assert step in [(1, 0), (0, 1)]


def test_dfs_direction_no_path():
    env, _ = _simple_env()
    step = dfs_direction(env.walls, env.width, env.height, (1, 1), (1, 1))
    assert step == (0, 0)


def test_ucs_direction_no_path():
    env, _ = _simple_env()
    step = ucs_direction(env.walls, env.width, env.height, (1, 1), (1, 1))
    assert step == (0, 0)


def test_predict_pacman_position_moves_forward():
    env, _ = _simple_env()
    pacman = HumanAgent(1, 2)
    pacman.direction = (1, 0)
    target = predict_pacman_position(env, pacman, steps=2)
    assert target == (3, 2)


def test_compare_day6_strategies_returns_expected_shape():
    _, maze = _simple_env()
    report = compare_day6_strategies(maze, route_steps=20, seed=7)
    assert "results" in report
    assert "bfs_reactive" in report["results"]
    assert "astar_reactive" in report["results"]
    assert "dfs_reactive" in report["results"]
    assert "ucs_reactive" in report["results"]
    assert "mcts_reactive" in report["results"]
    assert "astar_predictive_k3" in report["results"]
    assert "team4_astar_coop_k3" in report["results"]
    assert "team4_astar_roles" in report["results"]
    assert isinstance(report["results"]["bfs_reactive"]["captured"], bool)


def test_pacman_route_from_recording_frames_filters_duplicates():
    frames = [
        {"pacman": {"x": 1, "y": 1}},
        {"pacman": {"x": 1, "y": 1}},
        {"pacman": {"x": 2, "y": 1}},
        {"pacman": {"x": 2, "y": 2}},
    ]
    route = pacman_route_from_recording_frames(frames)
    assert route == [(1, 1), (2, 1), (2, 2)]


def test_compare_day6_strategies_on_recording_returns_ranking():
    _, maze = _simple_env()
    recorder = GameRecorder()
    recorder.set_metadata(maze, 5, 5, agent_type="replay")
    recorder.record_frame(
        {
            "pacman": {"x": 1, "y": 1, "dir": [1, 0]},
            "ghosts": [{"x": 3, "y": 3, "mode": "chase"}],
        }
    )
    recorder.record_frame(
        {
            "pacman": {"x": 2, "y": 1, "dir": [1, 0]},
            "ghosts": [{"x": 3, "y": 3, "mode": "chase"}],
        }
    )
    recorder.record_frame(
        {
            "pacman": {"x": 3, "y": 1, "dir": [1, 0]},
            "ghosts": [{"x": 3, "y": 2, "mode": "chase"}],
        }
    )

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        recorder.save(path)
        report = compare_day6_strategies_on_recording(path, max_ticks=100)
        assert "results" in report
        assert "ranking" in report
        assert report["ranking"]
    finally:
        Path(path).unlink(missing_ok=True)


def test_compare_strategies_over_seeds_returns_summary():
    _, maze = _simple_env()
    report = compare_strategies_over_seeds(
        maze=maze,
        seeds=[1, 2, 3],
        route_steps=20,
    )
    assert "summary" in report
    assert "ranking" in report["summary"]
    assert "strategies" in report["summary"]
    assert "bfs_reactive" in report["summary"]["strategies"]
    assert "astar_reactive" in report["summary"]["strategies"]
    assert "team4_astar_coop_k3" in report["summary"]["strategies"]
    assert "team4_astar_roles" in report["summary"]["strategies"]
