import ast
import os

from page import Page, PageFactory
from reportlab.lib import colors

"""
max = 178 x 286
"""

@PageFactory.register("reportlab")
class ReportLabPage(Page):
    """Draw a page from a file containing simple ReportLab canvas commands."""

    # _COMMAND_ALIASES = {
    #     "strokeColor": "setStrokeColor",
    #     "fillColor": "setFillColor",
    #     "closePath": "close",
    # }
    # _PATH_COMMANDS = {"moveTo", "lineTo", "curveTo", "closePath"}

    def __init__(self, file=None, filename=None, path=None, **kwargs):
        super().__init__()
        self._file_arg = file or filename
        self._path_arg = path

    def _resolve_full_path(self):
        if not self._file_arg:
            return None

        file_path = os.path.expanduser(str(self._file_arg))
        if os.path.isabs(file_path):
            return file_path

        if self._path_arg:
            path = str(self._path_arg).lower()
            if path == "local":
                base = os.path.dirname(__file__)
            elif path == "global":
                base = os.getcwd()
            else:
                base = os.path.expanduser(str(self._path_arg))
                if not os.path.isabs(base):
                    base = os.path.abspath(os.path.join(os.getcwd(), base))
        else:
            base = os.getcwd()

        return os.path.abspath(os.path.join(base, file_path))

    def tokenize_function_line(self, line_str):
        # 1. Parse the string into an AST tree
        # ast.parse returns a 'Module' node; we grab the first statement
        expr_stmt = ast.parse(line_str.strip()).body[0]

        # 2. Ensure it's actually a function call
        if not isinstance(expr_stmt, ast.Expr) or not isinstance(expr_stmt.value, ast.Call):
            raise ValueError("[{line_str}] is not a valid function call structure.")
            
        call_node = expr_stmt.value
        
        # 3. Extract the function name (the 'id' of the Name node)
        function_name = call_node.func.id
        
        # 4. Extract the arguments back into their raw string representations
        # ast.unparse() requires Python 3.9+
        arguments = [ast.unparse(arg).strip() for arg in call_node.args]
        
        return {
            "function": function_name,
            "arguments": arguments
        }


    def handle_command(self, canvas, fcn, args):
        numArgs = len(args)
        match fcn.lower():
            ## Colors
            case 'strokecolor' if numArgs >= 1:
                canvas.setStrokeColor(args[0]) 
            case 'fillcolor' if numArgs >= 1:
                canvas.setFillColor(args[0]) 

            # line control
            case 'setlinewidth':
                w = int(args[0])
                canvas.setLineWidth(w)
                # print ('lw')
            case 'setdash':
                if numArgs >= 2:
                    dashOn, dashOff = (int(x) for x in args[:2])
                    canvas.setDash([dashOn, dashOff])
                else: # assume reset
                    canvas.setDash([])

            # drawing
            case 'line' if numArgs >= 4:
                x1, y1, x2, y2 = (int(x) for x in args[:4])
                canvas.line(x1,y1,x2,y2)

            case 'rect' | 'rectangle' if numArgs >= 4:
                x, y, w, h = (int(x) for x in args[:4])
                stroke = int(args[4]) if numArgs >= 5 else 1
                fill = int(args[4]) if numArgs >= 6 else 0
                canvas.rect(x, y, w, h, stroke=stroke, fill=fill) 
            case 'ellipse' if numArgs >= 4:
                x1, y1, x2, y2 = (int(x) for x in args[:4])
                stroke = int(args[4]) if numArgs >= 5 else 1
                fill = int(args[4]) if numArgs >= 6 else 0
                canvas.ellipse(x1,y1, x2,y2, stroke=stroke, fill=fill)
            case 'arc' if numArgs >= 4:
                x1, y1, x2, y2 = (int(x) for x in args[:4])
                canvas.arc(x1,y1,x2,y2) 

            # strings
            case 'drawstring' | 'string' if numArgs >= 3: 
                x, y = (int(x) for x in args[:2])
                text = str(args[2])
                canvas.drawString(x, y, text)

            # font control

            # unknown
            case _:
                print (f"reportlab page unhandled command: {fcn}")

    def draw(self, canvas):
        full_path = self._resolve_full_path()
        if not full_path:
            raise ValueError("reportlab page requires a file= attribute")

        # save the state
        canvas.saveState()

        with open(full_path, "r", encoding="utf-8") as command_file:
            source = command_file.read()
            for fileline in source.splitlines():
                # process the line
                line = fileline.strip()
                if len(line) == 0 or line[0] == '#': # comment
                    continue
                tokens = self.tokenize_function_line(line)
                if tokens != None: args = tokens['arguments']
                self.handle_command(canvas, tokens['function'].lower(), args)

        #restore the state
        canvas.restoreState()
