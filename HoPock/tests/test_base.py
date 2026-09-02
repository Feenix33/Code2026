from models.config import PageConfig
from models.data_classes import Point
from models.styles import BookletStyle, Line, PageStyle
from pages.base import Page

from conftest import RecordingCanvas


class StubPage(Page):
    def draw(self, resume=False):
        self.draw_called = True


def test_render_rotates_translates_draws_frame_and_invokes_draw():
    canvas = RecordingCanvas(pagesize=(200, 100))
    config = PageConfig(
        page_type="stub",
        style=PageStyle(showframe=True, frame=Line(color="blue")),
    )
    page = StubPage(config, BookletStyle())

    page.render(canvas, corner=Point(20, 30), rotate=True, dim=Point(80, 40))

    assert page.draw_called is True
    assert page.mid == Point(40, 20)
    assert canvas.calls[:5] == [
        ("saveState",),
        ("translate", 100, 50),
        ("rotate", 180),
        ("translate", -100, -50),
        ("translate", 20, 30),
    ]
    assert ("rect", 0, 0, 80, 40, 1, 0) in canvas.calls
    assert canvas.calls[-1] == ("restoreState",)


def test_line_and_title_helpers_apply_style_and_return_next_y_position():
    canvas = RecordingCanvas(leading=14)
    config = PageConfig(page_type="stub", title="Notes")
    page = StubPage(config, BookletStyle())
    page.canvas = canvas
    page.max = Point(100, 60)
    page.mid = Point(50, 30)
    page.style.line = Line(color="red", width=2, dash=43)

    page._set_Line_format_default()
    next_y = page._draw_title()

    assert ("setStrokeColor", "red") in canvas.calls
    assert ("setLineWidth", 2) in canvas.calls
    assert ("setDash", [4, 3], 0) in canvas.calls
    assert ("drawCentredString", 50, 46, "Notes") in canvas.calls
    assert next_y == 32
