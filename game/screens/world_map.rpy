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

    add world_image

    for stage in stages:
        if not stage.get("unlocked"):
            continue
        $ rect = stage.get("rect", {})
        $ x = rect.get("x", 0)
        $ y = rect.get("y", 0)
        $ w = rect.get("w", 80)
        $ h = rect.get("h", 80)
        $ icon_path = stage.get("icon")
        $ is_hovered = hovered_stage and hovered_stage.get("id") == stage["id"]
        button:
            xpos x
            ypos y
            xsize w
            ysize h
            background None
            padding (0, 0)
            focus_mask True
            hovered SetScreenVariable("hovered_stage", stage)
            unhovered SetScreenVariable("hovered_stage", None)
            action [SetVariable("current_stage", stage["id"]), ShowMenu("stage_context", stage_id=stage["id"]) ]
            if is_hovered:
                add Solid("#ffd96640") xysize (w, h)
            if icon_path:
                add Transform(icon_path, fit="contain", xysize=(w, h)) at interactive_hover_zoom:
                    xalign 0.5
                    yalign 0.5
            else:
                add Transform(Solid("#ffd96628"), xysize=(w, h)) at interactive_hover_zoom

    if hovered_stage:
        $ rect = hovered_stage.get("rect", {})
        $ hx = rect.get("x", 0)
        $ hy = rect.get("y", 0)
        $ hw = rect.get("w", 80)
        $ hh = rect.get("h", 80)
        add Solid("#ffd9663c") xpos hx ypos hy xysize (hw, hh)

    if debug_clickables:
        for stage in stages:
            if not stage.get("unlocked"):
                continue
            $ rect = stage.get("rect", {})
            $ x = rect.get("x", 0)
            $ y = rect.get("y", 0)
            $ w = rect.get("w", 80)
            $ h = rect.get("h", 80)
            add Solid("#ff0000ff") xpos x ypos y xysize (w, h)
        
    if hovered_stage:
        frame:
            xalign 0.5
            yalign 0.95
            text "[hovered_stage['title']]\n[hovered_stage['description']]"
    else:
        text "Click a region to open its context." xalign 0.5 yalign 0.95