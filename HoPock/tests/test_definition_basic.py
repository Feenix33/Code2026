from definition_parser import DefinitionParser


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
