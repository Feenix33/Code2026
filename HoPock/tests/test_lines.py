from reportlab.lib.units import inch

from models.config import PageConfig
from models.data_classes import Point
from models.page_details import LinesPageDetail
from models.styles import BookletStyle
from pages.lines import LinesPage

from conftest import RecordingCanvas


def test_lines_page_draws_evenly_spaced_lines_inside_margins():
    canvas = RecordingCanvas()
    page = LinesPage(
        PageConfig(page_type="lines", detail=LinesPageDetail(spacing=0.25)),
        BookletStyle(),
    )

    page.render(canvas, corner=Point(0, 0), rotate=False, dim=Point(180, 100))

    lines = [call for call in canvas.calls if call[0] == "line"]
    assert page.spacing == 0.25 * inch
    assert lines == [
        ("line", 10, 82, 170, 82),
        ("line", 10, 64, 170, 64),
        ("line", 10, 46, 170, 46),
        ("line", 10, 28, 170, 28),
        ("line", 10, 10, 170, 10),
    ]


def test_lines_page_leaves_space_below_title():
    canvas = RecordingCanvas(leading=12)
    page = LinesPage(
        PageConfig(page_type="lines", title="My Notes", detail=LinesPageDetail()),
        BookletStyle(),
    )

    page.render(canvas, corner=Point(0, 0), rotate=False, dim=Point(180, 100))

    lines = [call for call in canvas.calls if call[0] == "line"]
    assert ("drawCentredString", 90, 88, "My Notes") in canvas.calls
    assert [line[2] for line in lines] == [58, 40, 22, 4]
