screen interaction_screen(target_id=None, area_id=None):
    tag menu
    default typed_response = player_response or ""
    on "show" action [SetVariable("player_response", ""), SetScreenVariable("typed_response", "")]

    if area_id is not None and current_area != area_id:
        $ current_area = area_id
    if target_id is not None and current_target != target_id:
        $ current_target = target_id

    $ active_area_id = current_area
    $ background = get_area_background(active_area_id)
    $ interaction = get_interaction(current_target)
    $ header = interaction.get("title") or get_dialogue_header(current_target)
    $ body = get_dialogue_text(current_target)
    $ sprite = interaction.get("sprite") or "images/characters/npc.png"

    add background
    add Solid("#00000066")
    add sprite xpos 0.22 xanchor 0.5 yalign 0.98 yanchor 1.0

    textbutton "Back to Area" action ShowMenu('area_exploration', area_id=active_area_id) xalign 0.02 yalign 0.04

    window:
        style "say_window"
        xalign 0.5
        yalign 1.0
        xsize 1180
        ysize 300
        vbox:
            spacing 16
            text header style "say_label"
            text body style "say_dialogue"
            hbox:
                spacing 12
                input:
                    value ScreenVariableInputValue("typed_response")
                    allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.?!'"
                    length 48
                    xminimum 720
                textbutton "Send" action [
                    SetVariable("player_response", typed_response),
                    Function(process_input, typed_response),
                    SetScreenVariable("typed_response", ""),
                ]
            text "[get_feedback()]" style "say_thought"

    if debug_clickables:
        $ rect = interaction.get("rect") if isinstance(interaction, dict) else None
        if rect:
            add Solid("#00ff0055") xpos rect.get("x", 0) ypos rect.get("y", 0) xysize (rect.get("w", 96), rect.get("h", 96))