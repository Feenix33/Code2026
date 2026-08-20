import ast
import os

from page import Page, PageFactory


@PageFactory.register("reportlab")
class ReportLabPage(Page):
    """Draw a page from a file containing simple ReportLab canvas commands."""

    _COMMAND_ALIASES = {
        "strokeColor": "setStrokeColor",
        "fillColor": "setFillColor",
        "closePath": "close",
    }
    _PATH_COMMANDS = {"moveTo", "lineTo", "curveTo", "closePath"}

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

    @staticmethod
    def _literal(node):
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError, SyntaxError) as error:
            raise ValueError("ReportLab command arguments must be literals") from error

    def _run_command(self, canvas, expression, path):
        if not isinstance(expression, ast.Call) or not isinstance(expression.func, ast.Name):
            raise ValueError("Only direct ReportLab command calls are supported")

        command_name = expression.func.id
        if command_name == "showPage":
            return path

        if command_name == "beginPath":
            if expression.args or expression.keywords:
                raise ValueError("beginPath does not accept arguments")
            return canvas.beginPath()

        if command_name == "drawPath":
            if path is None:
                raise ValueError("drawPath requires a preceding beginPath()")
            target = canvas
            args = [path] + [self._literal(argument) for argument in expression.args]
        else:
            target = path if path is not None and command_name in self._PATH_COMMANDS else canvas
            command_name = self._COMMAND_ALIASES.get(command_name, command_name)
            args = [self._literal(argument) for argument in expression.args]

        command = getattr(target, command_name, None)
        if command is None or not callable(command) or command_name.startswith("_"):
            raise ValueError(f"Unsupported ReportLab command '{command_name}'")

        keywords = {
            keyword.arg: self._literal(keyword.value)
            for keyword in expression.keywords
            if keyword.arg is not None
        }
        if len(keywords) != len(expression.keywords):
            raise ValueError("ReportLab command keywords must have names")
        command(*args, **keywords)
        return path

    def draw(self, canvas):
        full_path = self._resolve_full_path()
        if not full_path:
            raise ValueError("reportlab page requires a file= attribute")

        with open(full_path, "r", encoding="utf-8") as command_file:
            source = command_file.read()

        tree = ast.parse(source, filename=full_path, mode="exec")
        path = None
        for statement in tree.body:
            if isinstance(statement, ast.Pass):
                continue
            if not isinstance(statement, ast.Expr):
                raise ValueError("ReportLab command files may only contain command calls")
            path = self._run_command(canvas, statement.value, path)
