package require Tk

wm title . "Magicsplat Tk Test"
wm geometry . "300x150"

# Standard label uses -padx and -pady for internal spacing
label .lbl -text "Tcl/Tk is working!" -font {Consolas 14 bold} -padx 10 -pady 10
pack .lbl -pady 10

button .btn -text "Close" -command { exit }
pack .btn -pady 10

