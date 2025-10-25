################################################################################
## Styles
################################################################################

init -1 python:
    # Basic GUI configuration
    gui = renpy.store.gui
    
    # Font settings
    gui.text_font = "DejaVuSans.ttf"
    gui.name_text_font = "DejaVuSans.ttf"
    
    # Text sizes
    gui.text_size = 22
    gui.name_text_size = 24
    
    # Helper function for text properties
    def text_properties(accent=False):
        return {
            "font": gui.text_font,
            "size": gui.text_size,
            "color": "#ffffff",
            "outlines": [ (1, "#000000", 0, 0) ],
            "kerning": 2,
        }
    
    # Attach to gui for use in styles
    gui.text_properties = text_properties

# Default style (used as base for others)
style default:
    properties gui.text_properties()

# Window and button styles
style window is default
style say_window is window:
    background Solid("#000000cc")
    xalign 0.5
    yalign 1.0
    xsize 800
    ysize 150
    padding (15, 15)

style say_label is default:
    color "#ffff00"

style say_dialogue is default:
    color "#ffffff"

style menu_choice_button is default:
    xfill True

style menu_choice_button_text is default:
    color "#ffffff"
    hover_color "#ffff00"

# Quick menu styles
style quick_button is default:
    background None
    padding (10, 0)

style quick_button_text is default:
    color "#ffffff"
    hover_color "#ffff00"
    size 14