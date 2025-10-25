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
            textbutton _("Fullscreen") action Function(renpy.fullscreen, True)
            textbutton _("Windowed") action Function(renpy.fullscreen, False)
            textbutton _("Return") action Return()
