from datetime import date

from definition_parser import DefinitionParser
from config_builder import build_configuration
from utility import header_lcr


def test_normal_options():
    lines = [
        "daily fontsize=12 color=red",
    ]

    parser = DefinitionParser()
    entries = parser.parse_lines(lines)

    assert len(entries) == 1
    assert entries[0].page_type == "daily"
    assert entries[0].options == {
        "fontsize": "12",
        "color": "red",
    }


def test_list_page_mylist_option():
    entries = DefinitionParser().parse_lines([
        'list mylist="[\'one\', \'two\', \'three a and three b\', \'four 4 4 4\']"',
    ])

    config = build_configuration(entries)

    assert config.pages[0].detail.mylist == [
        "one",
        "two",
        "three a and three b",
        "four 4 4 4",
    ]


def test_weekly_dayformat_accepts_escaped_tabs():
    entries = DefinitionParser().parse_lines([
        r'weekly dayformat="{dd}\t{mmm}\t{yyyy}"',
    ])

    config = build_configuration(entries)

    assert header_lcr(
        config.pages[0].detail.dayformat,
        date(2026, 9, 21),
    ) == ("21", "Sep", "2026")


def test_escaped_hash_starts_block_text():
    entries = DefinitionParser().parse_lines([
        "markdown {",
        "# This is an option-mode comment.",
        "title=Example",
        r"\# Heading",
        "}",
    ])

    assert entries[0].options == {"title": "Example"}
    assert entries[0].text == ["# Heading"]


def test_hash_is_preserved_in_block_text_mode():
    entries = DefinitionParser().parse_lines([
        "markdown {",
        "",
        "# Heading",
        r"\# Another heading",
        "}",
    ])

    assert entries[0].text == ["# Heading", "# Another heading"]


def test_escaped_hash_on_block_opening_line():
    entries = DefinitionParser().parse_lines([
        r"markdown { \# Heading",
        "More text.",
        "}",
    ])

    assert entries[0].text == ["# Heading", "More text."]


def test_escaped_hash_in_inline_text_block():
    entries = DefinitionParser().parse_lines([
        r"markdown { \# Heading}",
    ])

    assert entries[0].text == ["# Heading"]
