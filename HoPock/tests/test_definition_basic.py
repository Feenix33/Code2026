from definition_parser import DefinitionParser
from config_builder import build_configuration


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
