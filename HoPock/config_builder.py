"""
Translates the p8 files into the booklet config file and styles
"""
from models.config import BookletConfig, PageConfig
from models.styles import *
from definition_parser import DefinitionEntry

STYLE_PARAMETERS = {
    "font",
    "fontsize",
    "fontcolor"
}

def split_options(options):
    style_options = {}
    page_options = {}

    for name,value in options.items():
        if name in STYLE_PARAMETERS:
            style_options[name] = value
        else:
            page_options[name] = value

    return style_options, page_options

def set_nested_value(obj, path, value):
    target = obj

    for attribute in path[:-1]:
        target = getattr(target, attribute)

    setattr(target, path[-1], value)

def convert_value(value, expected_type):
    if isinstance(value, expected_type):
        return value

    return expected_type(value)

PAGE_STYLE_OPTIONS = {
    "font.name":  (("font", "name"), str),
    "font.size":  (("font", "size"), int),
    "font.color": (("font", "color"), str),
    "file": ("file", str),
    "shownumber": ("shownumber", int),
}

def build_page_style(options):
    style = PageStyle()

    for name, value in options.items():
        definition = PAGE_STYLE_OPTIONS.get(name)
        print ("bps-------", name, value, definition)

        if definition is None:
            raise ValueError(f"Unknown booklet style option: {name}")
        path, expected_type = definition
        value = convert_value(value, expected_type)
        set_nested_value(style, path, value)

    return style

BOOKLET_STYLE_OPTIONS = {
    "font.name":  (("font", "name"), str),
    "font.size":  (("font", "size"), int),
    "font.color": (("font", "color"), str),
    "border":     (("border",), int),
}

def build_booklet_style(options):
    style = BookletStyle()

    for name, value in options.items():
        definition = BOOKLET_STYLE_OPTIONS.get(name)

        if definition is None:
            raise ValueError(f"Unknown booklet style option: {name}")
        path, expected_type = definition
        value = convert_value(value, expected_type)
        set_nested_value(style, path, value)

    return style

def build_configuration(booklet_definition):

    # for entry in booklet_definition:
    #     print (entry)
    # print ("="*40)

    pages = []
    for entry in booklet_definition:
        if entry.page_type == "booklet":
            booklet_style_opts, booklet_config_opts = split_options(entry.options)
            
            # print (f"BOOKLET STYLE {booklet_style_opts}")
            # print (f"BOOKLET CONFIG {booklet_config_opts}")
            # resolve_booklet_config(cfgBooklet, booklet_config_opts)
            # print (cfgBooklet["format"])
        else: # this is a page
            page_style_options, page_config_options = split_options(entry.options)
            print (page_style_options, page_config_options)
            # print ("page")
            # build the page style
            page_style = build_page_style(page_style_options)

            # buld the page config
            page_config = PageConfig(page_type=entry.page_type, style=page_style, text=entry.text, **page_config_options)
            # add it to the pages
            pages.append (page_config)
            continue

    styleBooklet = build_booklet_style(booklet_style_opts)
    cfgBooklet = BookletConfig(pages=pages, style=styleBooklet, **booklet_config_opts)

    print (cfgBooklet)
    return cfgBooklet
