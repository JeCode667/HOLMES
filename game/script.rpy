# Main script for HOLMES prototype (English)

# Initialize basic images
init:
    image bg black = Solid("#000")
    # Initialize empty variables that screens will use
    default current_stage = None
    default current_area = None
    default current_target = None
    default player_response = ""
    # Toggle to show debug outlines for clickable areas while testing
    default debug_clickables = True
    
    # Initialize dialogue system
    python:
        import sys
        import os
        python_dir = os.path.join(config.gamedir, "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)
        
        from dialogue_helpers import init_dialogue_system
        init_dialogue_system()

# Main game startup
label start:
    scene bg black
    # Jump straight into the first available stage map for easier testing
    $ stages = get_world_stage_entries()
    $ primary_stage = get_primary_stage_id()
    if not primary_stage and stages:
        $ primary_stage = stages[0].get("id")

    if primary_stage:
        $ current_stage = primary_stage
        show screen stage_map(stage_id=primary_stage)
    else:
        show screen world_map
    
    # The game loop is handled by screen navigation,
    # but we need to stay in script context
    while True:
        pause
            
    return