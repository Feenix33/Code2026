import pytest

from definition_parser import DefinitionEntry, DefinitionParser


def test_parse_file_reads_utf8_configuration(tmp_path):
    config_file = tmp_path / "test.p8"
    config_file.write_text(
        "daily title=Café\n",
        encoding="utf-8",
    )

    entries = DefinitionParser().parse_file(config_file)

    assert entries == [
        DefinitionEntry(
            page_type="daily",
            options={"title": "Café"},
        )
    ]


def test_parse_lines_ignores_blank_and_comment_lines_outside_entries():
    entries = DefinitionParser().parse_lines([
        "",
        "  # standalone comment",
        "daily",
        "   ",
        "# another comment",
    ])

    assert entries == [DefinitionEntry(page_type="daily")]


def test_page_type_and_option_names_are_lowercased_but_values_are_preserved():
    entries = DefinitionParser().parse_lines([
        "Daily FontSize=12 Title=KeepCase",
    ])

    assert entries[0].page_type == "daily"
    assert entries[0].options == {
        "fontsize": "12",
        "title": "KeepCase",
    }


@pytest.mark.parametrize(
    "line",
    [
        "daily fontsize=12 color=red",
        "daily fontsize =12 color =red",
        "daily fontsize= 12 color= red",
        "daily fontsize = 12 color = red",
    ],
)
def test_option_spacing_is_flexible(line):
    entries = DefinitionParser().parse_lines([line])

    assert entries[0].options == {
        "fontsize": "12",
        "color": "red",
    }


def test_quoted_option_values_keep_spaces_and_case():
    entries = DefinitionParser().parse_lines([
        """daily title="Keep This Case" subtitle='another value'""",
    ])

    assert entries[0].options == {
        "title": "Keep This Case",
        "subtitle": "another value",
    }


def test_quoted_option_value_can_escape_its_quote():
    entries = DefinitionParser().parse_lines([
        r"""daily title="A \"quoted\" title" """,
    ])

    assert entries[0].options == {
        "title": 'A "quoted" title',
    }


def test_unrecognized_backslash_escape_is_preserved_in_quoted_value():
    entries = DefinitionParser().parse_lines([
        r'daily pattern="a\tb"',
    ])

    assert entries[0].options["pattern"] == r"a\tb"


def test_option_line_continuation_joins_options():
    entries = DefinitionParser().parse_lines([
        "daily fontsize=12 \\",
        "color=red",
    ])

    assert entries[0].options == {
        "fontsize": "12",
        "color": "red",
    }


@pytest.mark.parametrize(
    ("lines", "message"),
    [
        (["daily fontsize=12 \\"], "no continuation line"),
        (["daily fontsize=12 \\", ""], "Blank line"),
    ],
)
def test_invalid_option_line_continuation_raises(lines, message):
    with pytest.raises(ValueError, match=message):
        DefinitionParser().parse_lines(lines)


def test_inline_block_can_contain_options():
    entries = DefinitionParser().parse_lines([
        "daily { fontsize=12 color=red }",
    ])

    assert entries[0].options == {
        "fontsize": "12",
        "color": "red",
    }
    assert entries[0].text == []


def test_inline_block_can_contain_text():
    entries = DefinitionParser().parse_lines([
        "markdown { A line of text.}",
    ])

    assert entries[0].text == ["A line of text."]


def test_block_comments_are_ignored_before_options_and_text():
    entries = DefinitionParser().parse_lines([
        "markdown {",
        "# ignored option-section comment",
        "title=Example",
        "A line of text.",
        "# retained text",
        "}",
    ])

    assert entries[0].options == {"title": "Example"}
    assert entries[0].text == ["A line of text.", "# retained text"]


def test_blank_line_switches_block_from_options_to_text():
    entries = DefinitionParser().parse_lines([
        "markdown {",
        "title=Example",
        "",
        "body=value is text now",
        "}",
    ])

    assert entries[0].options == {"title": "Example"}
    assert entries[0].text == ["body=value is text now"]


def test_escaped_hash_becomes_literal_hash_at_start_of_block_text():
    entries = DefinitionParser().parse_lines([
        "markdown {",
        "title=Example",
        r"\# Heading",
        "}",
    ])

    assert entries[0].options == {"title": "Example"}
    assert entries[0].text == ["# Heading"]


def test_hash_escapes_apply_to_text_but_not_options():
    entries = DefinitionParser().parse_lines([
        r'daily title="\#keep"',
    ])

    assert entries[0].options == {"title": r"\#keep"}


def test_unclosed_quoted_option_value_raises():
    with pytest.raises(ValueError, match="Unterminated quoted option value"):
        DefinitionParser().parse_lines([
            'daily title="unfinished',
        ])


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("daily fontsize", "Expected '='"),
        ("daily =12", "Invalid option syntax"),
        ("daily fontsize=", "has no value"),
        ("daily fontsize=12 extra", "Expected '='"),
    ],
)
def test_invalid_option_syntax_raises(line, message):
    with pytest.raises(ValueError, match=message):
        DefinitionParser().parse_lines([line])
