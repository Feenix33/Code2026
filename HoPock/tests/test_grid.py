from reportlab.lib.units import inch

from models.config import PageConfig
from models.data_classes import Point
from models.page_details import GridPageDetail
from models.styles import BookletStyle
from pages.grid import GridPage

from conftest import RecordingCanvas


def test_grid_page_draws_centered_horizontal_and_vertical_lines():
    canvas = RecordingCanvas()
    page = GridPage(
        PageConfig(
            page_type="grid",
            detail=GridPageDetail(grid=Point(0.5, 0.25)),
        ),
        BookletStyle(),
    )

    page.render(canvas, corner=Point(0, 0), rotate=False, dim=Point(180, 100))

    lines = [call for call in canvas.calls if call[0] == "line"]
    assert page.grid == Point(0.5 * inch, 0.25 * inch)
    assert lines[:5] == [
        ("line", 18, 82, 162, 82),
        ("line", 18, 64, 162, 64),
        ("line", 18, 46, 162, 46),
        ("line", 18, 28, 162, 28),
        ("line", 18, 10, 162, 10),
    ]
    assert lines[5:] == [
        ("line", 18, 82, 18, 10),
        ("line", 54, 82, 54, 10),
        ("line", 90, 82, 90, 10),
        ("line", 126, 82, 126, 10),
        ("line", 162, 82, 162, 10),
    ]


def test_grid_page_uses_spacing_when_grid_coordinates_are_zero():
    page = GridPage(
        PageConfig(
            page_type="grid",
            detail=GridPageDetail(spacing=0.25, grid=Point(0, 0)),
        ),
        BookletStyle(),
    )

    assert page.grid == Point(0.25 * inch, 0.25 * inch)
