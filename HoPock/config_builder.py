"""
Translates the p8 files into the booklet config file and styles
"""
from dataclasses import fields, is_dataclass
from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints

from models.config import (
    PageConfig,
    BookletConfig,
)

from models.styles import (
    Font,
    BookletStyle,
    PageStyle,
)

from pages.factory import PageFactory
from pages import daily
from pages import calendar
from pages import lines

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


def OLDconvert_value(value, expected_type):
    """Convert a configuration value to the expected Python type."""

    # Handle Optional[T] / T | None
    origin = get_origin(expected_type)

    if origin is Union or origin is type(None):
        types = [t for t in get_args(expected_type) if t is not type(None)]

        if value is None or value == "":
            return None

        if len(types) == 1:
            return convert_value(value, types[0])

    # Already the correct type
    if isinstance(value, expected_type):
        return value

    # Boolean needs special handling
    if expected_type is bool:
        if isinstance(value, str):
            value = value.lower()

            if value in ("true", "1", "yes", "on"):
                return True

            if value in ("false", "0", "no", "off"):
                return False

            raise ValueError(f"Invalid boolean value: {value}")

        return bool(value)

    # Standard conversions: int, str, float, etc.
    try:
        return expected_type(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Cannot convert {value!r} to {expected_type}"
        ) from exc

def set_nested_value(obj, path, value):
    """Set a value on an object using a dotted attribute path."""
    target = obj

    for attribute in path[:-1]:
        target = getattr(target, attribute)

    setattr(target, path[-1], value)


from dataclasses import fields, is_dataclass
from typing import get_type_hints, get_origin, get_args, Union


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



# def apply_options(obj, options):
#     """
#     Apply recognized options to a dataclass object.

#     Returns:
#         dict: Options that were not recognized by the object.
#     """

#     remaining = {}

#     for name, value in options.items():

#         path = name.split(".")
#         current = obj

#         try:
#             # Walk down the path and determine whether it exists.
#             for attribute in path[:-1]:
#                 current = getattr(current, attribute)

#             final_attribute = path[-1]

#             # Make sure the final attribute exists.
#             if not hasattr(current, final_attribute):
#                 remaining[name] = value
#                 continue

#             # Get type information from the actual class.
#             type_hints = get_type_hints(type(current))

#             if final_attribute not in type_hints:
#                 remaining[name] = value
#                 continue

#             expected_type = type_hints[final_attribute]

#             converted_value = convert_value(
#                 value,
#                 expected_type
#             )

#             set_nested_value(
#                 obj,
#                 path,
#                 converted_value
#             )

#         except AttributeError:
#             remaining[name] = value

#     return remaining

# def build_configuration(booklet_definition):

#     pages = []

#     booklet_style = BookletStyle()
#     booklet_config = BookletConfig(pages=pages)

#     for entry in booklet_definition:

#         if entry.page_type == "booklet":

#             # First: try presentation options
#             remaining = apply_options(
#                 booklet_style,
#                 entry.options
#             )

#             # Then: try booklet configuration options
#             remaining = apply_options(
#                 booklet_config,
#                 remaining
#             )

#             if remaining:
#                 raise ValueError(
#                     f"Unknown booklet options: "
#                     f"{', '.join(remaining)}"
#                 )

#         else:

#             # Start with default page style
#             page_style = PageStyle()

#             # Apply presentation options
#             remaining = apply_options(
#                 page_style,
#                 entry.options
#             )

#             detail_class = PageFactory.get_detail_class(entry.page_type)

#             if detail_class is not None:
#                 page_detail = detail_class()

#                 remaining = apply_options(
#                     page_detail,
#                     remaining
#                 )
#             else:
#                 page_detail = None

#             # Create page configuration
#             page_config = PageConfig(
#                 page_type=entry.page_type,
#                 style=page_style,
#                 text=entry.text
#             )

#             # Apply page configuration options
#             remaining = apply_options(
#                 page_config,
#                 remaining
#             )

#             if remaining:
#                 raise ValueError(
#                     f"Unknown options for page "
#                     f"{entry.page_type}: "
#                     f"{', '.join(remaining)}"
#                 )

#             pages.append(page_config)

#     print (booklet_config)
#     return booklet_config

def build_configuration(definitions):
    pages = []

    booklet_style = BookletStyle()
    booklet_config = BookletConfig(pages=pages)

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

        pages.append(page_config)

    print (booklet_config)
    return booklet_config