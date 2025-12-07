init python:
    import sys
    import os
    python_dir = os.path.join(config.gamedir, "python")
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
    
    from dialogue_helpers import (
        dialogue_start_exchange,
        get_current_dialogue_exchange,
        get_current_dialogue_option,
        get_current_option_index,
        get_total_dialogue_options,
        is_dialogue_generating,
        navigate_dialogue_next_option,
        navigate_dialogue_prev_option,
        navigate_dialogue_next_exchange,
        navigate_dialogue_prev_exchange,
        is_viewing_past_dialogue,
        dialogue_select_option,
        resolve_agent_for_target,
        switch_to_agent,
    )

screen interaction_screen(target_id=None, area_id=None):
    """
    Écran de dialogue au style roman visuel classique avec agent IA.
    Le personnage parle, le joueur écrit sa réponse, le personnage répond.
    """
    tag menu
    default typed_response = ""

    on "show" action [
        SetScreenVariable("typed_response", ""),
    ]

    if area_id is not None and current_area != area_id:
        $ current_area = area_id
    if target_id is not None and current_target != target_id:
        $ current_target = target_id

    $ active_area_id = current_area
    $ background = get_area_background(active_area_id)
    $ interaction = get_interaction(current_target)
    $ header = interaction.get("title") or get_dialogue_header(current_target)
    $ sprite = interaction.get("sprite") or "images/characters/npc.png"

    # Résoudre l'agent pour cette cible et basculer vers lui
    $ agent_id = resolve_agent_for_target(current_target)
    $ switch_to_agent(agent_id)

    add background
    add Solid("#00000066")
    add sprite xpos 0.22 xanchor 0.5 yalign 0.98 yanchor 1.0

    textbutton "Back to Area" action ShowMenu('area_exploration', area_id=active_area_id):
        xalign 0.02
        yalign 0.04
        style_prefix "interactive_button"
        at interactive_hover_zoom

    # Navigation buttons for dialogue history (top right)
    hbox:
        xalign 0.98
        yalign 0.04
        spacing 8
        
        $ dialogue_history_count = len(get_current_dialogue_exchange().get("player_input", "") and [1] or [])
        
        textbutton "← Previous" action [
            Function(navigate_dialogue_prev_exchange),
            Function(renpy.restart_interaction),
        ]:
            style_prefix "interactive_button"
            at interactive_hover_zoom
        
        textbutton "Next →" action [
            Function(navigate_dialogue_next_exchange),
            Function(renpy.restart_interaction),
        ]:
            style_prefix "interactive_button"
            at interactive_hover_zoom

    # Fenêtre principale de dialogue - Style roman visuel classique
    window:
        style "say_window"
        xalign 0.5
        yalign 1.0
        xsize 1180
        ysize 450
        vbox:
            spacing 12

            # En-tête du personnage
            text header style "say_label"

            # Récupérer l'état du dialogue
            $ current_exchange = get_current_dialogue_exchange()
            $ is_generating = is_dialogue_generating()
            $ is_viewing_past = is_viewing_past_dialogue()
            
            # AFFICHAGE CLASSIQUE : Le personnage parle, le joueur écrit sa réponse
            if is_generating:
                # En attente de réponse - affichage d'attente
                text "Waiting for response..." style "say_dialogue"
                # Force a screen update to allow async generation to progress
            
            elif current_exchange and current_exchange.get("agent_response"):
                # Affichage du message du personnage (réponse de l'agent)
                $ agent_response = current_exchange.get("agent_response", "")
                $ player_input = current_exchange.get("player_input", "")
                $ agent_name = current_exchange.get("agent_name", header)
                
                # Afficher la réponse du joueur (toujours quand on regarde le passé)
                if player_input:
                    hbox:
                        xsize 1100
                        text "You: " style "say_label" size 24 color "#87CEEB"
                        text str(player_input).replace("[", "").replace("]", "") style "say_dialogue"
                
                # Afficher la réponse de l'agent
                if agent_response:
                    hbox:
                        xsize 1100
                        text (str(agent_name) + ": ") style "say_label" size 24
                        text str(agent_response).replace("[", "").replace("]", "") style "say_dialogue"
                
                # Zone d'entrée pour la réponse du joueur - SEULEMENT si c'est la conversation actuelle
                if not is_viewing_past:
                    text "Your response:" style "say_thought" size 20
                    hbox:
                        spacing 12
                        xalign 0.5
                        
                        input:
                            value ScreenVariableInputValue("typed_response")
                            allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.?!'-\""
                            length 128
                            xminimum 800
                        
                        textbutton "Send" action [
                            Function(dialogue_start_exchange, typed_response, agent_id, current_target),
                            SetScreenVariable("typed_response", ""),
                            Function(renpy.restart_interaction),
                        ]:
                            style_prefix "interactive_button"
                            at interactive_hover_zoom
                    
                    key "enter" action [
                        Function(dialogue_start_exchange, typed_response, agent_id, current_target),
                        SetScreenVariable("typed_response", ""),
                        Function(renpy.restart_interaction),
                    ]
            
            else:
                # Premier message du personnage - commencer le dialogue
                text "..." style "say_dialogue"
                
                hbox:
                    spacing 12
                    xalign 0.5
                    
                    textbutton "Start Conversation" action [
                        Function(dialogue_start_exchange, "Hello", agent_id, current_target),
                        Function(renpy.restart_interaction),
                    ]:
                        style_prefix "interactive_button"
                        at interactive_hover_zoom

    if debug_clickables:
        $ rect = interaction.get("rect") if isinstance(interaction, dict) else None
        if rect:
            add Solid("#00ff0055") xpos rect.get("x", 0) ypos rect.get("y", 0) xysize (rect.get("w", 96), rect.get("h", 96))
