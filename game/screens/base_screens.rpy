################################################################################
## Essential Ren'Py Screens (minimal set)
################################################################################

## Say screen ##################################################################
screen say(who, what):
    style_prefix "say"
    window:
        id "window"
        style "say_window"
        
        text what id "what":
            style "say_dialogue"
            
        if who:
            text who id "who":
                style "say_label"

## Confirm screen #############################################################
screen confirm(message, yes_action, no_action):
    modal True
    frame:
        style_prefix "confirm"
        xalign 0.5
        yalign 0.5
        vbox:
            xalign 0.5
            spacing 30
            label _(message):
                xalign 0.5
            hbox:
                xalign 0.5
                spacing 100
                textbutton _("Yes") action yes_action:
                    style_prefix "interactive_button"
                    at interactive_hover_zoom
                textbutton _("No") action no_action:
                    style_prefix "interactive_button"
                    at interactive_hover_zoom

## Quick Menu screen #########################################################
screen quick_menu():
    # Essential quick menu for development
    hbox:
        style_prefix "quick"
        xalign 0.5
        yalign 0.95
        textbutton _("Back") action Rollback() at interactive_hover_zoom
        textbutton _("Q.Save") action QuickSave() at interactive_hover_zoom
        textbutton _("Q.Load") action QuickLoad() at interactive_hover_zoom
        textbutton _("Skip") action Skip() at interactive_hover_zoom
        textbutton _("F.Skip") action Skip(fast=True, confirm=True) at interactive_hover_zoom
        textbutton _("Auto") action Preference("auto-forward", "toggle") at interactive_hover_zoom
    textbutton _("Menu") action ShowMenu() at interactive_hover_zoom
    textbutton _("Prefs") action ShowMenu("preferences") at interactive_hover_zoom

# Basic styles for the confirm screen
style confirm_frame:
    background Solid("#000000B0")
    xpadding 60
    ypadding 40
    xalign 0.5
    yalign 0.5

style confirm_prompt:
    xalign 0.5
    yalign 0.5

style confirm_prompt_text:
    text_align 0.5
    size 22
    color "#ffffff"

style confirm_button:
    xalign 0.5
    yalign 0.5
    padding (20, 5)

style confirm_button_text:
    size 24
    color "#ffffff"
    hover_color "#ffff00"