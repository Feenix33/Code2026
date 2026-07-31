import unittest

from page_image import PageImage
from data_classes import Point, Font


class DummyCanvas:
    def __init__(self):
        self.calls = []

    def setFont(self, *args):
        pass

    def setFillColor(self, *args):
        pass

    def drawInlineImage(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class PageImageDrawTests(unittest.TestCase):
    def test_draw_uses_image_filename_as_the_first_draw_inline_image_argument(self):
        page = PageImage()
        page.max = Point(300, 200)
        page.overrides["fontTitle"] = Font(name="Helvetica", size=12, color="black")
        page.overrides["file"] = "demo.png"

        canvas = DummyCanvas()
        page.draw(canvas)

        self.assertEqual(len(canvas.calls), 1)
        self.assertEqual(canvas.calls[0][0][0], "demo.png")


if __name__ == "__main__":
    unittest.main()
