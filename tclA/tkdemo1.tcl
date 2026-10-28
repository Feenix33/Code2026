package require Tk

wm title . "Magicsplat Tk Test"
wm geometry . "300x150"

# Use ttk::label and ttk::button instead of standard widgets
ttk::label .lbl -text "Tcl/Tk is working!" -font {Consolas 14 bold} -padding 10
pack .lbl -pady 10

ttk::button .btn -text "Close" -command { exit }
pack .btn -pady 10

