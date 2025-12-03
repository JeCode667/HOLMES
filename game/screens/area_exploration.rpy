screen area_exploration(area_id=None):
    tag menu
    default hovered_object = None

    if area_id is not None and current_area != area_id:
        $ current_area = area_id

    $ active_area_id = current_area
    $ area = get_area(active_area_id)
    $ interactions = get_interactive_objects(active_area_id)
    $ background = get_area_background(active_area_id)
    $ parent_stage = get_area_stage(active_area_id)

    add background

    frame:
        xalign 0.02
        yalign 0.02
        xsize 360
        ysize 160
        vbox:
            text "[area.get('title', 'Area')]" xalign 0.5
            text "[area.get('summary', '')]" size 16 xalign 0.5
            text "Points of interest: [len(interactions)]" size 14 xalign 0.5
            text "Debug id: [active_area_id]" size 12 xalign 0.5
            text "Stage: [parent_stage or 'unknown']" size 12 xalign 0.5

    if not interactions:
        text "No points of interest available." xalign 0.5 yalign 0.5 size 22

    for obj in interactions:
        $ rect = obj.get("rect", {})
        $ x = rect.get("x", 0)
        $ y = rect.get("y", 0)
        $ w = rect.get("w", 96)
        $ h = rect.get("h", 96)
        $ sprite = obj.get("sprite") or "images/characters/npc.png"
        button:
            xpos x
            ypos y
            xsize w
            ysize h
            style "interaction_hotspot"
            hovered SetScreenVariable("hovered_object", obj)
            unhovered SetScreenVariable("hovered_object", None)
            action [
                SetVariable("current_area", active_area_id),
                SetVariable("current_target", obj["id"]),
                ShowMenu("interaction_screen", target_id=obj["id"], area_id=active_area_id),
            ]
            add Transform(sprite, fit="contain", xysize=(w, h)) at interactive_hover_zoom xalign 0.5 yalign 0.5

    if debug_clickables:
        for obj in interactions:
            $ rect = obj.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 96)
            $ h = rect.get("h", 96)
            add Solid("#ff00ff44") xpos x ypos y xysize (w, h)
        
    if hovered_object:
        frame:
            xalign 0.5
            yalign 0.95
            text "[hovered_object.get('title', hovered_object['id'])]"
    elif interactions:
        text "Choose a point of interest." xalign 0.5 yalign 0.95

    textbutton "Back to Stage Map" action ShowMenu('stage_map', stage_id=parent_stage):
        xalign 0.02
        yalign 0.95
        style_prefix "interactive_button"
        at interactive_hover_zoom
