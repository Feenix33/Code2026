"""Test doubles shared by page-rendering tests."""


class RecordingCanvas:
    """Small ReportLab-compatible canvas that records drawing calls."""

    def __init__(self, pagesize=(200, 100), leading=12):
        self._pagesize = pagesize
        self._leading = leading
        self.calls = []

    def saveState(self):
        self.calls.append(("saveState",))

    def restoreState(self):
        self.calls.append(("restoreState",))

    def translate(self, x, y):
        self.calls.append(("translate", x, y))

    def rotate(self, degrees):
        self.calls.append(("rotate", degrees))

    def setStrokeColor(self, color):
        self.calls.append(("setStrokeColor", color))

    def setLineWidth(self, width):
        self.calls.append(("setLineWidth", width))

    def setDash(self, array, phase=0):
        self.calls.append(("setDash", array, phase))

    def rect(self, x, y, width, height, stroke=1, fill=0):
        self.calls.append(("rect", x, y, width, height, stroke, fill))

    def setFont(self, name, size):
        self.calls.append(("setFont", name, size))

    def setFillColor(self, color):
        self.calls.append(("setFillColor", color))

    def drawCentredString(self, x, y, text):
        self.calls.append(("drawCentredString", x, y, text))

    def line(self, x1, y1, x2, y2):
        self.calls.append(("line", x1, y1, x2, y2))
