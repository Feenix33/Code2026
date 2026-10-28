import tkinter
"""
Simple example showing TCL script that feeds Tkinter
"""

def debug_tcl_arguments(*args):
    """This python function intercepts the arguments sent from Tcl."""
    print("📥 [Python Received a Call from Tcl!]")
    print(f"   Raw tuple data: {args}")
    print(f"   Number of args: {len(args)}")
    
    # Inspecting individual arguments
    for idx, arg in enumerate(args):
        print(f"   └─ argument[{idx}]: '{arg}' (Type: {type(arg).__name__})")
    print("=" * 50)

# 1. Initialize the built-in Tcl interpreter
tcl_interp = tkinter.Tk().tk  # Direct, clean access to the core Tcl object

# 2. Register the custom keyword "test_args" to map to our Python function
tcl_interp.createcommand("test_args", debug_tcl_arguments)

# 3. Define a generic Tcl script testing various parameter styles
tcl_script = """
# Test 1: Standard space-separated arguments
test_args high female 1.5

# Test 2: Passing a flag-based keyword pair 
test_args -pitch low -speed 0.8

# Test 3: Passing a string containing spaces using curly braces (Tcl text block)
test_args {Hello World! This is a single text argument block.}

# Test 4: Passing no arguments at all
test_args
"""

# 4. Execute the script
print("🚀 Running Tcl Script...\n" + "=" * 50)
tcl_interp.eval(tcl_script)

