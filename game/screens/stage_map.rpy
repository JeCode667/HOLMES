screen stage_map(stage_id=None):
    tag menu
    default hovered_area = None
    if stage_id is not None and current_stage != stage_id:
        $ current_stage = stage_id
    $ active_stage_id = current_stage
    $ stage = get_stage(active_stage_id)
    $ areas = get_stage_areas(active_stage_id)
    $ map_image = get_stage_map_image(active_stage_id)

    frame:
        xalign 0.02
        yalign 0.02
        xsize 360
        ysize 140
        vbox:
            text "[stage.get('title', 'Stage Map')]" xalign 0.5
            text "Areas available: [len(areas)]" size 16 xalign 0.5

    imagemap:
        xpos 0
        ypos 0
        ground map_image
        for area in areas:
            $ rect = area.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 100)
            $ h = rect.get("h", 100)
            hotspot (x, y, w, h):
                action [SetVariable("current_area", area["id"]), ShowMenu("area_exploration", area_id=area["id"])]
                hovered SetScreenVariable("hovered_area", area)
                unhovered SetScreenVariable("hovered_area", None)

    if debug_clickables:
        for area in areas:
            $ rect = area.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 100)
            $ h = rect.get("h", 100)
            add Solid("#ff00ff44") xpos x ypos y xysize (w, h)
        frame:
            xalign 0.98
            yalign 0.02
            background None
            vbox:
                text "Area coords:" size 18
                for area in areas:
                    $ rect = area.get("rect", {})
                    text "[area['id']] @ ([rect.get('x')], [rect.get('y')])" size 14

    if hovered_area:
        frame:
            xalign 0.5
            yalign 0.95
            text "[hovered_area.get('title', hovered_area['id'])]\n[hovered_area.get('summary', '')]"
    else:
        text "Select an area to begin exploration." xalign 0.5 yalign 0.95

    textbutton "Back to Stage Context" action ShowMenu('stage_context', stage_id=active_stage_id) xalign 0.02 yalign 0.95
