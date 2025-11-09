import json
import os
from copy import deepcopy
from typing import Dict, List, Optional


def _default_data() -> Dict[str, object]:
    """Fallback payload used when the primary data file is missing or invalid."""
    return {
        "world_map": {
            "title": "World Map",
            "image": "images/maps/world_map.png",
            "stages": [
                {
                    "id": "rome",
                    "title": "Ancient Rome",
                    "description": "Rome, 44 BCE. Political tension, urban life.",
                    "rect": {"x": 200, "y": 180, "w": 160, "h": 140},
                    "default_unlocked": True,
                    "map_image": "images/maps/rome_map.png",
                    "areas": [
                        {
                            "id": "rome_forum",
                            "title": "Forum",
                            "summary": "Political heart of the Republic.",
                            "rect": {"x": 320, "y": 220, "w": 140, "h": 120},
                            "background": "images/backgrounds/forum.png",
                            "interactions": [
                                {
                                    "id": "rome_forum_orator",
                                    "title": "Passionate Orator",
                                    "sprite": "images/characters/npc.png",
                                    "rect": {"x": 420, "y": 260, "w": 100, "h": 100},
                                    "dialogue": {
                                        "header": "Passionate Orator",
                                        "text": "Citizens! The Senate teeters on the edge of conspiracy...",
                                        "keywords": ["senate", "conspiracy", "caesar"],
                                        "success_feedback": "You touched on the Senate's turmoil.",
                                        "failure_feedback": "Try mentioning the Senate or Caesar's fate."
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


class GameData:
    """Loads and indexes static game content for quick lookup."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.data_path = os.path.abspath(data_path or os.path.join(base_dir, "game_content.json"))
        self._raw: Dict[str, object] = self._load()
        self._world: Dict[str, object] = self._raw.get("world_map", {}) if isinstance(self._raw, dict) else {}
        self._stages: List[Dict[str, object]] = list(self._world.get("stages", [])) if isinstance(self._world, dict) else []
        self._stage_index: Dict[str, Dict[str, object]] = {}
        self._area_index: Dict[str, Dict[str, object]] = {}
        self._interaction_index: Dict[str, Dict[str, object]] = {}
        self._area_to_stage: Dict[str, str] = {}
        self._interaction_to_area: Dict[str, str] = {}
        self._canonical_area_ids: Dict[str, str] = {}
        self._primary_stage_id: Optional[str] = None
        self._index_data()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load(self) -> Dict[str, object]:
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    try:
                        import renpy  # type: ignore

                        renpy.log(
                            f"GameData: loaded data from {self.data_path} with keys {list(data.keys())}"
                        )
                    except Exception:
                        pass
                    return data
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass
        return _default_data()

    def _index_data(self) -> None:
        for stage in self._stages:
            if not isinstance(stage, dict):
                continue
            stage_id_value = stage.get("id")
            if not stage_id_value:
                continue
            stage_id = str(stage_id_value)
            self._stage_index[stage_id] = stage
            if self._primary_stage_id is None and stage.get("default_unlocked", False):
                self._primary_stage_id = stage_id
            areas_list = stage.get("areas", [])
            if not isinstance(areas_list, list):
                continue
            for area in areas_list or []:
                if not isinstance(area, dict):
                    continue
                area_id_value = area.get("id")
                if not area_id_value:
                    continue
                area_id = str(area_id_value)
                self._area_index[area_id] = area
                self._area_to_stage[area_id] = stage_id
                self._register_area_alias(area_id, stage_id, area)
                if isinstance(area_id, str) and "_" in area_id:
                    alias = area_id.split("_", 1)[1]
                    self._register_area_alias(alias, stage_id, area)
                for interaction in area.get("interactions", []) or []:
                    if not isinstance(interaction, dict):
                        continue
                    interaction_id_value = interaction.get("id")
                    if not interaction_id_value:
                        continue
                    interaction_id = str(interaction_id_value)
                    self._interaction_index[interaction_id] = interaction
                    self._interaction_to_area[interaction_id] = area_id
        if self._primary_stage_id is None and self._stages:
            first_stage = self._stages[0]
            if isinstance(first_stage, dict):
                first_id = first_stage.get("id")
                self._primary_stage_id = str(first_id) if first_id else None

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------
    @property
    def world_title(self) -> str:
        return str(self._world.get("title", "World Map"))

    @property
    def world_image(self) -> str:
        return str(self._world.get("image", "images/maps/world_map.png"))

    @property
    def primary_stage_id(self) -> Optional[str]:
        return self._primary_stage_id

    def stages(self) -> List[Dict[str, object]]:
        return deepcopy(self._stages)

    def iter_stage_entries(self) -> List[Dict[str, object]]:
        entries: List[Dict[str, object]] = []
        for stage in self._stages:
            if not isinstance(stage, dict):
                continue
            stage_id = stage.get("id")
            if not stage_id:
                continue
            entry = {
                "id": stage_id,
                "title": stage.get("title", stage_id),
                "description": stage.get("description", ""),
                "rect": deepcopy(stage.get("rect", {})),
                "map_image": stage.get("map_image", ""),
                "default_unlocked": stage.get("default_unlocked", False),
            }
            entries.append(entry)
        return entries

    def get_stage(self, stage_id: str) -> Optional[Dict[str, object]]:
        stage = self._stage_index.get(stage_id)
        if stage is None:
            try:
                import renpy  # type: ignore

                renpy.log(
                    "GameData:get_stage missing %r. Available=%s" % (
                        stage_id,
                        list(self._stage_index.keys()),
                    )
                )
            except Exception:
                pass
        return deepcopy(stage) if stage else None

    def get_stage_areas(self, stage_id: str) -> List[Dict[str, object]]:
        stage = self._stage_index.get(stage_id)
        results: List[Dict[str, object]] = []
        if not stage:
            return results
        areas_list = stage.get("areas", [])
        if not isinstance(areas_list, list):
            return results
        for area in areas_list or []:
            if isinstance(area, dict):
                results.append(deepcopy(area))
        return results

    def get_stage_context_cards(self, stage_id: str) -> List[Dict[str, object]]:
        stage = self._stage_index.get(stage_id)
        results: List[Dict[str, object]] = []
        if not stage:
            return results
        raw_cards = stage.get("context_cards", [])
        if not isinstance(raw_cards, list):
            return results
        for card in raw_cards:
            if isinstance(card, dict):
                results.append(deepcopy(card))
        return results

    def get_area(self, area_id: str) -> Optional[Dict[str, object]]:
        canonical = self.resolve_area_id(area_id)
        lookup_id = canonical or area_id
        area = self._area_index.get(lookup_id)
        return deepcopy(area) if area else None

    def get_area_stage(self, area_id: str) -> Optional[str]:
        canonical = self.resolve_area_id(area_id)
        lookup_id = canonical or area_id
        return self._area_to_stage.get(lookup_id)

    def get_interactions(self, area_id: str) -> List[Dict[str, object]]:
        canonical = self.resolve_area_id(area_id)
        lookup_id = canonical or area_id
        area = self._area_index.get(lookup_id)
        results: List[Dict[str, object]] = []
        if not area:
            return results
        interactions_list = area.get("interactions", [])
        if isinstance(interactions_list, list):
            for interaction in interactions_list or []:
                if isinstance(interaction, dict):
                    results.append(deepcopy(interaction))
        return results

    def get_interaction(self, interaction_id: str) -> Optional[Dict[str, object]]:
        interaction = self._interaction_index.get(interaction_id)
        if not interaction:
            return None
        result = deepcopy(interaction)
        area_id = self._interaction_to_area.get(interaction_id)
        if area_id:
            result.setdefault("area_id", area_id)
            stage_id = self._area_to_stage.get(area_id)
            if stage_id:
                result.setdefault("stage_id", stage_id)
        return result

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------
    def _register_area_alias(self, alias: str, stage_id: str, area: Dict[str, object]) -> None:
        if not alias:
            return
        alias_str = str(alias)
        canonical_id = str(area.get("id", alias_str))
        self._canonical_area_ids.setdefault(alias_str, canonical_id)
        self._canonical_area_ids.setdefault(alias_str.lower(), canonical_id)
        self._area_to_stage.setdefault(alias_str, stage_id)
        self._area_to_stage.setdefault(alias_str.lower(), stage_id)
        self._area_index.setdefault(alias_str, area)

    def resolve_area_id(self, area_id: Optional[str]) -> Optional[str]:
        if not area_id:
            return None
        if area_id in self._canonical_area_ids:
            return self._canonical_area_ids[area_id]
        lowered = str(area_id).lower()
        return self._canonical_area_ids.get(lowered)