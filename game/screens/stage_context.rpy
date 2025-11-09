screen stage_context(stage_id=None):
    tag menu
    modal True

    python:
        import renpy

        active_stage_id = stage_id
        stage_data = get_stage(active_stage_id)

        if active_stage_id is None:
            stage_data = {
                "title": "Unknown Stage",
                "description": "",
                "map_image": get_world_image(),
            }
        else:
            renpy.store.current_stage = active_stage_id

        areas = get_stage_areas(active_stage_id) if active_stage_id else []
        cards = []
        raw_cards = stage_data.get("context_cards", []) or []
        print(stage_data.get("context_cards"))
        print("stage_context raw_cards:", raw_cards)
        for entry in raw_cards:
            cards.append({
                "title": entry.get("title", "Unknown Area"),
                "text": entry.get("text", ""),
                "image": entry.get("image"),
            })
            print("  added context card:", cards[-1])
        if not cards and areas:
            for area in areas[:3]:
                if isinstance(area, dict):
                    cards.append({
                        "title": area.get("title", "Unknown Area"),
                        "text": area.get("summary", ""),
                        "image": area.get("context_image") or area.get("background") or area.get("image"),
                    })
        cards = cards[:3]
        while len(cards) < 3:
            cards.append(None)

        debug_cards_summary = ", ".join(
            c.get("title", "Unknown Area")
            for c in cards
            if isinstance(c, dict)
        ) or "None"

        try:
            debug_log(
                "stage_context resolved id=%r stage_keys=%s cards=%s areas=%d" % (
                    active_stage_id,
                    list(stage_data.keys()) if isinstance(stage_data, dict) else None,
                    [c.get("title") if isinstance(c, dict) else None for c in cards],
                    len(areas) if areas else 0,
                )
            )
        except Exception:
            pass

        stage = stage_data
        active_stage = active_stage_id

    $ stage_map_image = stage.get('map_image') if isinstance(stage, dict) else None
    $ screen_w = config.screen_width
    $ screen_h = config.screen_height
    $ card_width = max(1, screen_w // 3)
    $ card_height = max(360, screen_h - 200)
    $ overlay_height = card_height // 2
    $ header_width = min(screen_w, max(400, screen_w - 160))

    frame:
        background None
        xalign 0.5
        yalign 0.05
        xsize header_width
        ysize 200
        vbox:
            spacing 6
            text "[stage.get('title', 'Unknown Stage')]" size 36 xalign 0.5
            text "[stage.get('description', '')]" size 20 xalign 0.5
            text "Areas available: [len(areas)]" size 18 xalign 0.5
            if config.developer:
                text "Debug stage id: [active_stage]" size 14 xalign 0.5
                text "Debug cards: [debug_cards_summary]" size 12 xalign 0.5

    hbox:
        spacing 0
        xalign 0.5
        yalign 0.55
        for card in cards:
            fixed:
                xsize card_width
                ysize card_height
                $ image_path = None
                if card:
                    $ image_path = card.get('image') or stage_map_image
                else:
                    $ image_path = stage_map_image
                if image_path:
                    add Transform(image_path, xysize=(card_width, card_height))
                else:
                    add Solid("#333333") xysize (card_width, card_height)
                frame:
                    background Solid("#000000d8")
                    yalign 1.0
                    xfill True
                    ysize overlay_height
                    padding (18, 18, 18, 18)
                    vbox:
                        spacing 10
                        if card:
                            text "[card.get('title', 'Unknown Area')]" size 28
                            $ card_text = card.get('text', '') or 'Details a venir.'
                            text "[card_text]" size 18
                        else:
                            text "Coming soon" size 28
                            text "New area information will appear here." size 18

    hbox:
        spacing 40
        xalign 0.5
        yalign 0.93
        textbutton "Enter Stage" action ShowMenu('stage_map', stage_id=active_stage)
        textbutton "Back to World Map" action ShowMenu('world_map')