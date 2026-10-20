from reportlab.lib.styles import ParagraphStyle

import mistune

from processors.markdown import MyMarkdownRenderer


class FakeStyles:
    def get(self, name):
        return ParagraphStyle(name)

    def derive(self, base_style, overrides):
        return ParagraphStyle(
            "blockquote",
            parent=base_style,
            textColor="purple",
            leftIndent=10,
        )


def test_block_quote_renders_child_paragraph_inline_without_queuing_it_separately():
    renderer = MyMarkdownRenderer(FakeStyles())
    markdown = mistune.create_markdown(renderer=renderer)

    markdown("> quoted **bold** text\n")

    assert len(renderer.queue) == 1
    assert renderer.queue[0].text == "quoted <b>bold</b> text"


def test_block_quote_preserves_separate_paragraphs():
    renderer = MyMarkdownRenderer(FakeStyles())
    markdown = mistune.create_markdown(renderer=renderer)

    markdown("> first paragraph\n>\n> second paragraph\n")

    assert len(renderer.queue) == 1
    assert renderer.queue[0].text == "first paragraph<br/><br/>second paragraph"


def test_table_renders_as_a_monospace_ascii_table():
    renderer = MyMarkdownRenderer(FakeStyles())
    markdown = mistune.create_markdown(renderer=renderer, plugins=["table"])

    markdown("| Name | Value |\n| ---- | ----: |\n| alpha | 1 |\n| beta | 20 |\n")

    assert len(renderer.queue) == 1
    assert renderer.queue[0].text == (
        "| Name  | Value |\n"
        "|-------|-------|\n"
        "| alpha |     1 |\n"
        "| beta  |    20 |"
    )


def test_table_renders_inline_emphasis_without_counting_markup_in_column_width():
    renderer = MyMarkdownRenderer(FakeStyles())
    markdown = mistune.create_markdown(renderer=renderer, plugins=["table"])

    markdown("| Item | Note |\n| --- | --- |\n| **bold** | plain |\n")

    assert renderer.queue[0].text == (
        "| Item | Note  |\n"
        "|------|-------|\n"
        "| <b>bold</b> | plain |"
    )
