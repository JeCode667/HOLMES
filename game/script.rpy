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

# Main game startup
label start:
    scene bg black
    # Now that basic screens work, show the world map
    show screen world_map
    
    # The game loop is handled by screen navigation,
    # but we need to stay in script context
    while True:
        pause
            
    return