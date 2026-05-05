# enregistreur de parties - sauvegarde et rejoue les parties en json

import json
import time
from pathlib import Path


class GameRecorder:

    def __init__(self):
        self.frames = []
        self.metadata = {}

    def set_metadata(self, maze, width, height, cloud_id=None, agent_type="human", level=None):
        self.metadata = {
            "maze": maze,
            "width": width,
            "height": height,
            "cloud_id": cloud_id,
            "agent_type": agent_type,
            "level": level,
            "recorded_at": int(time.time()),
        }

    def record_frame(self, state):
        self.frames.append(state)

    def save(self, filepath):
        # sauvegarde l'enregistrement dans un fichier json
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        # enrichit les métadonnées avec le score final et le nombre de frames
        self.metadata["score_final"] = self.get_final_score()
        self.metadata["nb_frames"] = len(self.frames)
        # convertit les tuples/frozensets en listes pour json
        data = {
            "metadata": self.metadata,
            "total_frames": len(self.frames),
            "frames": self.frames,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, default=_json_default)

    @classmethod
    def load(cls, filepath):
        # charge un enregistrement depuis un fichier json
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        recorder = cls()
        recorder.metadata = data["metadata"]
        recorder.frames = data["frames"]
        return recorder

    def get_frame(self, index):
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None

    @property
    def total_frames(self):
        return len(self.frames)

    def get_final_score(self):
        if self.frames:
            return self.frames[-1].get("score", 0)
        return 0


def _json_default(obj):
    # gère les types non sérialisables
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
