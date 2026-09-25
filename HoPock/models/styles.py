"""
Styles used by the booklet and individual pages.
"""

from dataclasses import dataclass, field


@dataclass
class Font:
    """
    Font definition.

    None means that the value has not been specified and should
    be inherited from another style.
    """
    name: str | None = None
    size: int | None = None
    color: str | None = None


@dataclass
class Line:
    """
    Line definition.

    None means that the value has not been specified and should
    be inherited from another style.
    """
    color: str | None = None
    width: int | None = None
    dash: int | None = None


@dataclass
class Marker:
    """
    Marker used by list styles.
    """
    type: str | None = None
    text: str | None = None
    format: str | None = None


@dataclass
class TextStyle:
    """
    Text style definition.

    Values are None when the style is being used as an override.
    BookletStyle provides the actual defaults.
    """
    name: str | None = None

    font: Font = field(default_factory=Font)
    font_medium: Font = field(default_factory=Font)
    font_large: Font = field(default_factory=Font)

    alignment: str | None = None
    leading: float | None = None
    space_after: float | None = None
    space_before: float | None = None

    # List-related settings
    list_type: str | None = None
    left_indent: float | None = None
    first_line_indent: float | None = None
    hanging_indent: bool | None = None

    marker: Marker = field(default_factory=Marker)

    # ReportLab bullet settings
    bulletfontname: str | None = None
    bulletfontsize: float | None = None
    bulletindent: float | None = None
    bulletcolor: str | None = None


@dataclass
class BookletStyle:
    """
    Booklet-wide defaults.

    These values are the starting point for every page.
    """

    # ---------------------------------------------------------
    # General booklet settings
    # ---------------------------------------------------------

    border: int = 10
    margin: int = 10

    showframe: bool = False
    showpage: bool = False

    # ---------------------------------------------------------
    # Default font
    # ---------------------------------------------------------

    font: Font = field(default_factory=lambda: Font(
        name="Helvetica",
        size=8,
        color="black"
    ))
    font_medium: Font = field(default_factory=lambda: Font(name="Helvetica", size=10, color="green" ))
    font_large: Font = field(default_factory=lambda: Font(name="Helvetica", size=12, color="blue" ))

    # ---------------------------------------------------------
    # Text styles
    # ---------------------------------------------------------

    title: TextStyle = field(default_factory=lambda: TextStyle(
        name="TitleStyle",
        font=Font(
            name="Helvetica",
            size=13,
            color="orange"
        ),
        alignment="center",
        leading=14,
        space_after=12,
        space_before=0
    ))

    body: TextStyle = field(default_factory=lambda: TextStyle(
        name="BodyStyle",
        font=Font(
            name="Helvetica",
            size=8,
            color="black"
        ),
        font_large=Font(name="Helvetica", size=14, color="green"),
        alignment="left",
        leading=10,
        space_after=10,
        space_before=0
    ))

    heading1: TextStyle = field(default_factory=lambda: TextStyle(
        name="HeadingStyle",
        font=Font(
            name="Helvetica",
            size=12,
            color="black"
        ),
        alignment="left",
        leading=14,
        space_after=10,
        space_before=0
    ))

    heading2: TextStyle = field(default_factory=lambda: TextStyle(
        name="HeadingStyle",
        font=Font(
            name="Helvetica",
            size=11,
            color="blue"
        ),
        alignment="left",
        leading=13,
        space_after=10,
        space_before=0
    ))

    bullet: TextStyle = field(default_factory=lambda: TextStyle(
        name="BulletStyle",
        font=Font(
            name="Helvetica",
            size=8,
            color="black"
        ),
        alignment="left",
        leading=10,
        space_after=0,
        space_before=0,

        list_type="bullet",
        left_indent=10,
        first_line_indent=-10,
        hanging_indent=True,

        marker=Marker(
            type="bullet",
            text="•"
        ),

        bulletfontname="Helvetica",
        bulletfontsize=8,
        bulletindent=10,
        bulletcolor="black"
    ))

    # ---------------------------------------------------------
    # Line styles
    # ---------------------------------------------------------

    line: Line = field(default_factory=lambda: Line(
        color="lightgrey",
        width=1,
        dash=0
    ))

    frame: Line = field(default_factory=lambda: Line(
        color="grey",
        width=1,
        dash=0
    ))


@dataclass
class PageStyle:
    """
    Overrides for a single page.

    Every value defaults to None so that it inherits the
    corresponding value from BookletStyle.
    """

    font: Font = field(default_factory=Font)
    font_medium: Font = field(default_factory=Font)
    font_large: Font = field(default_factory=Font)

    line: Line = field(default_factory=Line)
    frame: Line = field(default_factory=Line)

    title: TextStyle = field(default_factory=TextStyle)
    body: TextStyle = field(default_factory=TextStyle)
    heading1: TextStyle = field(default_factory=TextStyle)
    heading2: TextStyle = field(default_factory=TextStyle)
    bullet: TextStyle = field(default_factory=TextStyle)

    margin: int | None = None
    showframe: bool | None = None
    showpage: bool | None = None