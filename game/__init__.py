"""Pac-Man game module - Environment, Agents, Engine, Recorder, Renderer."""

from game.environment import Environment
from game.agents import HumanAgent, BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost, GhostMode
from game.engine import GameEngine
from game.recorder import GameRecorder

try:
    from game.renderer import PacmanRenderer
except ImportError:
    PacmanRenderer = None
