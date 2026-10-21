from reportlab.lib.styles import ParagraphStyle

from processors.roff import RoffProcessor


class FakeStyles:
    def get(self, name):
        return ParagraphStyle(name)

    def derive(self, base_style, overrides):
        return base_style


def test_defn_removes_quotes_from_multiword_first_token():
    renderer = RoffProcessor()

    result = renderer.process(
        ['.defn "-h, --help" Show a terse help'],
        FakeStyles(),
    )

    assert len(result) == 1
    assert result[0].text == (
        "<b><i>-h, --help</i></b> Show a terse help"
    )
