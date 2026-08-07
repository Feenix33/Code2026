"""
PDF renderer.

This renderer will eventually create printable maps.

For now it simply demonstrates the interface.
"""

from renderer import Renderer


class PdfRenderer(Renderer):
    def __init__(self, filename):
        self.filename = filename

    def render(self, grid):
        print(
            f"PDF renderer not implemented yet.\n"
            f"Would save to {self.filename}"
        )
