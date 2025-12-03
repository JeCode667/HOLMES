################################################################################
# Preferences screen
################################################################################

screen preferences():
    tag menu
    modal True
    frame:
        xalign 0.5
        yalign 0.5
        padding (30, 30)
        vbox:
            spacing 12
            label _("Preferences")
            textbutton _("Fullscreen") action Function(renpy.fullscreen, True):
                style_prefix "interactive_button"
                at interactive_hover_zoom
            textbutton _("Windowed") action Function(renpy.fullscreen, False):
                style_prefix "interactive_button"
                at interactive_hover_zoom
            textbutton _("Return") action Return():
                style_prefix "interactive_button"
                at interactive_hover_zoom
