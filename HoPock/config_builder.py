"""
Translates the p8 files into the booklet config file and styles
"""
from dataclasses import fields, is_dataclass
from types import UnionType
from typing import get_type_hints, get_origin, get_args, Union
from pathlib import Path

from models.config import (
    PageConfig,
    BookletConfig,
)

from models.styles import (
    Font,
    BookletStyle,
    PageStyle,
)

from models.data_classes import Point

from pages.factory import PageFactory
from pages import (
    daily,
    calendar,
    lines,
    grid,
    text,
)

import logging
logger = logging.getLogger(__name__)

def resolve_file_path(data_dir, filename):
    """Resolve a page file against the booklet data directory."""

    if filename is None:
        return None

    path = Path(filename)

    # Absolute paths are always used as-is.
    if path.is_absolute():
        return path

    # If there is a booklet data directory, prepend it.
    if data_dir is not None:
        return Path(data_dir) / path

    # Otherwise leave the relative path alone.
    return path

def convert_value(value, expected_type):

    if value is None:
        return None

    # Handle int | None, str | None, etc.
    origin = get_origin(expected_type)

    if origin in (Union, UnionType):

        possible_types = [
            t for t in get_args(expected_type)
            if t is not type(None)
        ]

        if len(possible_types) == 1:
            expected_type = possible_types[0]

    if isinstance(value, expected_type):
        return value

    if expected_type is bool:

        if isinstance(value, str):
            value = value.strip().lower()

            if value in ("true", "1", "yes", "on"):
                return True

            if value in ("false", "0", "no", "off"):
                return False

            raise ValueError(
                f"Invalid boolean value: {value}"
            )

        return bool(value)

    try:
        return expected_type(value)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Cannot convert {value!r} "
            f"to {expected_type}"
        ) from exc


def set_nested_value(obj, path, value):
    """Set a value on an object using a dotted attribute path."""
    target = obj

    for attribute in path[:-1]:
        target = getattr(target, attribute)

    setattr(target, path[-1], value)


def apply_options(obj, options):
    """
    Apply recognized options to a dataclass object.

    Options use dotted names for nested attributes, for example:

        font.size=10
        font.color=blue

    Returns a dictionary containing options that were not
    recognized by this object.
    """

    remaining = {}

    for name, value in options.items():

        path = name.split(".")
        current = obj

        try:
            # Walk through all but the final attribute.
            for attribute in path[:-1]:
                current = getattr(current, attribute)

            final_attribute = path[-1]

            # Does the final attribute actually exist?
            if not hasattr(current, final_attribute):
                remaining[name] = value
                continue

            # Get the declared type from the class containing
            # the final attribute.
            type_hints = get_type_hints(current.__class__)

            if final_attribute not in type_hints:
                remaining[name] = value
                continue

            expected_type = type_hints[final_attribute]

            converted_value = convert_value(
                value,
                expected_type
            )

            setattr(
                current,
                final_attribute,
                converted_value
            )

        except AttributeError:
            remaining[name] = value

    return remaining


def build_configuration(definitions):
    pages = []

    booklet_style = BookletStyle()
    booklet_config = BookletConfig(pages=pages, style=booklet_style)

    for entry in definitions:

        # ---------------------------------
        # Booklet options
        # ---------------------------------
        if entry.page_type == "booklet":

            remaining = apply_options(
                booklet_style,
                entry.options
            )

            remaining = apply_options(
                booklet_config,
                remaining
            )

            if remaining:
                raise ValueError(
                    f"Unknown booklet options: {remaining}"
                )

            continue

        # ---------------------------------
        # Page style
        # ---------------------------------
        page_style = PageStyle()

        remaining = apply_options(
            page_style,
            entry.options
        )

        # ---------------------------------
        # Page-specific detail
        # ---------------------------------
        page_detail = PageFactory.create_detail(
            entry.page_type
        )

        if page_detail is not None:

            remaining = apply_options(
                page_detail,
                remaining
            )

        # ---------------------------------
        # Generic page configuration
        # ---------------------------------
        page_config = PageConfig(
            page_type=entry.page_type,
            style=page_style,
            text=entry.text,
            detail=page_detail
        )

        remaining = apply_options(
            page_config,
            remaining
        )

        if remaining:
            raise ValueError(
                f"Unknown options for page "
                f"'{entry.page_type}': {remaining}"
            )

        page_config = finalize_page_config(
            page_config,
            booklet_config
        )
        pages.append(page_config)

    # from pprint import pprint
    # pprint(booklet_config, indent=2, depth=4, compact=True)
    # logger.debug (booklet_config)
    return booklet_config


def finalize_page_config(page_config, booklet_config):
    """Resolve page-level values that depend on booklet configuration."""

    if page_config.file is not None:
        page_config.file = resolve_file_path(
            booklet_config.data_dir,
            page_config.file
        )

    return page_config