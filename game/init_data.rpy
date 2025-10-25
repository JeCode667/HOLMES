init python:
    from copy import deepcopy
    from python.game_data import GameData

    _game_data = GameData()
    _dialogue_feedback = [""]
    _areas_data = {"last_action": None, "last_object": None}

    def _resolve_area_identifier(area_id):
        if hasattr(_game_data, "resolve_area_id"):
            resolved = _game_data.resolve_area_id(area_id)
            if resolved:
                return resolved
        if isinstance(area_id, str) and "_" in area_id:
            alias = area_id.split("_", 1)[1]
            if _game_data.get_area(alias):
                return alias
        return area_id

    # ------------------------------------------------------------------
    # World map helpers
    # ------------------------------------------------------------------
    def get_world_title():
        return _game_data.world_title

    def get_world_image():
        return _game_data.world_image

    def get_world_stage_entries():
        from python.progression import Progression

        progression = Progression()
        unlocked_ids = set(progression.data.get("unlocked_stages", []))
        primary = _game_data.primary_stage_id
        if primary:
            unlocked_ids.add(primary)

        entries = []
        for stage in _game_data.iter_stage_entries():
            stage_id = stage["id"]
            entry = deepcopy(stage)
            entry["unlocked"] = bool(entry.get("default_unlocked") or stage_id in unlocked_ids)
            entries.append(entry)
        return entries

    # ------------------------------------------------------------------
    # Stage + area helpers
    # ------------------------------------------------------------------
    def get_stage(stage_id):
        return _game_data.get_stage(stage_id) or {
            "id": stage_id or "unknown",
            "title": "Unknown Stage",
            "description": "",
            "map_image": get_world_image(),
        }

    def get_stage_context(stage_id):
        stage = get_stage(stage_id)
        return {
            "title": stage.get("title", "Unknown Stage"),
            "description": stage.get("description", ""),
        }

    def get_stage_map_image(stage_id):
        stage = get_stage(stage_id)
        return stage.get("map_image") or get_world_image()

    def get_stage_areas(stage_id):
        areas = []
        for area in _game_data.get_stage_areas(stage_id):
            entry = deepcopy(area)
            entry.setdefault("stage_id", stage_id)
            areas.append(entry)
        return areas

    def get_area(area_id):
        resolved_id = _resolve_area_identifier(area_id)
        area = _game_data.get_area(resolved_id or area_id)
        if not area:
            return {
                "id": area_id or "unknown",
                "title": "Unknown Area",
                "summary": "",
                "background": "images/backgrounds/forum.png",
                "interactions": [],
            }
        if resolved_id:
            area.setdefault("id", resolved_id)
        stage_id = get_area_stage(resolved_id or area_id)
        if stage_id:
            area.setdefault("stage_id", stage_id)
        return area

    def get_area_background(area_id):
        area = get_area(area_id)
        return area.get("background", "images/backgrounds/forum.png")

    def get_area_stage(area_id):
        resolved_id = _resolve_area_identifier(area_id)
        stage_id = _game_data.get_area_stage(resolved_id or area_id)
        if not stage_id and isinstance(area_id, str) and "_" in area_id:
            stage_id = area_id.split("_", 1)[0]
        return stage_id

    def get_interactive_objects(area_id):
        resolved_id = _resolve_area_identifier(area_id) or area_id
        interactions = []
        stage_id = get_area_stage(resolved_id)
        for interaction in _game_data.get_interactions(resolved_id):
            entry = deepcopy(interaction)
            entry.setdefault("area_id", resolved_id)
            if stage_id:
                entry.setdefault("stage_id", stage_id)
            entry.setdefault("sprite", "images/characters/npc.png")
            interactions.append(entry)
        _areas_data["last_query"] = {
            "area": area_id,
            "resolved": resolved_id,
            "count": len(interactions),
            "stage": stage_id,
        }
        try:
            import renpy

            renpy.log(
                f"get_interactive_objects({area_id}) resolved={resolved_id} stage={stage_id} -> {len(interactions)} entries"
            )
        except Exception:
            pass
        return interactions

    # ------------------------------------------------------------------
    # Dialogue helpers
    # ------------------------------------------------------------------
    def get_interaction(target_id):
        return _game_data.get_interaction(target_id) or {
            "id": target_id or "unknown",
            "title": "Unknown Target",
            "dialogue": {},
        }

    def get_interaction_dialogue(target_id):
        interaction = get_interaction(target_id)
        return interaction.get("dialogue", {})

    def get_dialogue_header(target_id):
        return get_interaction_dialogue(target_id).get("header", "")

    def get_dialogue_text(target_id):
        return get_interaction_dialogue(target_id).get("text", "")

    def get_dialogue_keywords(target_id):
        dialogue = get_interaction_dialogue(target_id)
        return dialogue.get("keywords", [])

    def get_dialogue_feedback_text(target_id, success=True):
        dialogue = get_interaction_dialogue(target_id)
        key = "success_feedback" if success else "failure_feedback"
        return dialogue.get(key)

    # ------------------------------------------------------------------
    # Player input bridge
    # ------------------------------------------------------------------
    def process_input(text):
        from python.dialogue_logic import process_input as proc

        ok, feedback = proc(text, current_target)
        _dialogue_feedback[0] = feedback
        if ok:
            from python.progression import Progression

            progression = Progression()
            progression.mark_area_complete(current_area)
        return None

    def get_feedback():
        return _dialogue_feedback[0]