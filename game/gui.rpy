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
    hover_background Solid("#ffffff10")

style quick_button_text is default:
    color "#ffffff"
    hover_color "#ffff00"
    size 14
    hover_outlines [ (1, "#000000e0", 0, 0) ]

transform interactive_hover_zoom:
    on idle:
        ease 0.12 zoom 1.0
    on hover:
        ease 0.12 zoom 1.08

style interactive_button_button is button:
    background Solid("#ffffff14")
    hover_background Solid("#ffd96633")
    padding (12, 18)
    focus_mask True

style interactive_button_button_text is default:
    color "#ffffff"
    outlines [ (1, "#000000c0", 0, 0) ]
    hover_outlines [ (3, "#000000ff", 0, 0) ]
    hover_color "#ffd966"

style interaction_hotspot is button:
    background Solid("#ffffff0a")
    hover_background Solid("#ffd96628")
    padding (4, 4)
    focus_mask True