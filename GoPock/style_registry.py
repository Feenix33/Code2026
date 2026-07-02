from reportlab.lib import colors

DEFAULT_PARAGRAPH_STYLE_NAME = 'body'
DEFAULT_PARAGRAPH_STYLE_FOR_RECIPE = 'line'

PARAGRAPH_STYLE_NAMES = (
    'body',
    'line',
    'heading',
    'heading1',
    'heading2',
    'heading3',
    'heading4',
    'title',
    'title2',
    'bullet',
    'numlist',
    'code',
)

KNOWN_PARAGRAPH_STYLES = set(PARAGRAPH_STYLE_NAMES)


def paragraph_style_configs(base_kwargs):
    return {
        'body': {
            **base_kwargs,
            'name': 'Body',
        },
        'line': {
            **base_kwargs,
            'name': 'Line',
            'spaceAfter': 0,
        },
        'heading': {
            **base_kwargs,
            'name': 'Heading',
            'fontSize': base_kwargs['fontSize'] * 1.2,
        },
        'heading1': {
            **base_kwargs,
            'name': 'Heading1',
            'fontSize': base_kwargs['fontSize'] * 1.6,
        },
        'heading2': {
            **base_kwargs,
            'name': 'Heading2',
            'fontSize': base_kwargs['fontSize'] * 1.4,
        },
        'heading3': {
            **base_kwargs,
            'name': 'Heading3',
            'fontSize': base_kwargs['fontSize'] * 1.3,
        },
        'heading4': {
            **base_kwargs,
            'name': 'Heading4',
            'fontSize': base_kwargs['fontSize'] * 1.2,
        },
        'title': {
            **base_kwargs,
            'name': 'Title',
            'fontSize': base_kwargs['fontSize'] * 1.8,
            'align': 'center',
            'textColor': 'blue',
        },
        'title2': {
            **base_kwargs,
            'name': 'Title2',
            'fontSize': base_kwargs['fontSize'] * 1.4,
            'align': 'center',
        },
        'bullet': {
            **base_kwargs,
            'name': 'Bullet',
            'leftIndent': 10,
            'bulletIndent': 20,
        },
        'numlist': {
            **base_kwargs,
            'name': 'Numbered',
            'leftIndent': 10,
            'bulletIndent': 20,
        },
        'code': {
            **base_kwargs,
            'name': 'Code',
            'fontName': 'Courier',
            'backColor': colors.whitesmoke,
            'spaceAfter': 6,
        },
    }
