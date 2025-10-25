import json
import os

from python.game_data import GameData

try:
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "save_state.json")
except NameError:
    DATA_PATH = os.path.join("data", "save_state.json")


def _baseline_state():
    primary = GameData().primary_stage_id or "rome"
    unlocked = [primary] if primary else []
    return {"unlocked_stages": unlocked, "completed_areas": []}


class Progression:
    def __init__(self):
        self.path = os.path.abspath(DATA_PATH)
        self.data = self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return _baseline_state()
                data.setdefault("unlocked_stages", [])
                data.setdefault("completed_areas", [])
                if not data["unlocked_stages"]:
                    data["unlocked_stages"] = _baseline_state()["unlocked_stages"]
                return data
        except FileNotFoundError:
            return _baseline_state()

    def unlock_stage(self, stage_id):
        if stage_id not in self.data.get("unlocked_stages", []):
            self.data.setdefault("unlocked_stages", []).append(stage_id)
            self.save()

    def mark_area_complete(self, area_id):
        if area_id not in self.data.get("completed_areas", []):
            self.data.setdefault("completed_areas", []).append(area_id)
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)