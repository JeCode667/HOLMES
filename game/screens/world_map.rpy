screen world_map():
    tag menu
    default hovered_stage = None

    frame:
        xalign 0.02
        yalign 0.02
        xsize 420
        ysize 130
        vbox:
            text "[get_world_title()]" xalign 0.5 yalign 0.2
            text "Unlocked regions are highlighted." size 16 xalign 0.5

    $ world_image = get_world_image()
    $ stages = get_world_stage_entries()

    imagemap:
        xpos 0
        ypos 0
        ground world_image
        for stage in stages:
            if not stage.get("unlocked"):
                continue
            $ rect = stage.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 80)
            $ h = rect.get("h", 80)
            hotspot (x, y, w, h):
                action [SetVariable("current_stage", stage["id"]), ShowMenu("stage_context", stage_id=stage["id"])]
                hovered SetScreenVariable("hovered_stage", stage)
                unhovered SetScreenVariable("hovered_stage", None)

    if debug_clickables:
        for stage in stages:
            if not stage.get("unlocked"):
                continue
            $ rect = stage.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 80)
            $ h = rect.get("h", 80)
            add Solid("#ff00ff44") xpos x ypos y xysize (w, h)
        frame:
            xalign 0.98
            yalign 0.02
            background None
            vbox:
                text "Stage coords:" size 18
                for stage in stages:
                    $ rect = stage.get("rect", {})
                    text "[stage['id']] @ ([rect.get('x')], [rect.get('y')]) unlocked=[stage.get('unlocked')]" size 14

    if hovered_stage:
        frame:
            xalign 0.5
            yalign 0.95
            text "[hovered_stage['title']]\n[hovered_stage['description']]"
    else:
        text "Click a region to open its context." xalign 0.5 yalign 0.95