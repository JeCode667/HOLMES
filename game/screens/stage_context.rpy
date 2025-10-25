screen stage_context(stage_id=None):
    tag menu
    modal True
    if stage_id is not None and current_stage != stage_id:
        $ current_stage = stage_id
    $ active_stage = current_stage
    $ stage = get_stage(active_stage)
    $ areas = get_stage_areas(active_stage)
    frame:
        xalign 0.5
        yalign 0.1
        xsize 960
        ysize 220
        vbox:
            text "[stage.get('title', 'Unknown Stage')]" size 30
            text "[stage.get('description', '')]" size 18
            text "Areas available: [len(areas)]" size 16
            hbox:
                spacing 20
                textbutton "Enter Stage" action ShowMenu('stage_map', stage_id=active_stage)
                textbutton "Back to World Map" action ShowMenu('world_map')