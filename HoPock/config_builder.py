# """
# Translates the p8 files into the booklet config file and styles
# """
# import ast
# from dataclasses import fields, is_dataclass
# from types import UnionType
# from typing import get_type_hints, get_origin, get_args, Union
# from pathlib import Path

# from models.config import (
#     PageConfig,
#     BookletConfig,
# )

# from models.styles import (
#     Font,
#     BookletStyle,
#     PageStyle,
# )

# from models.data_classes import Point

# from pages.factory import PageFactory
# from pages import (
#     daily,
#     calendar,
#     lines,
#     grid,
#     list as list_page,
#     runoff,
#     text,
#     markdown,
# )

# import logging
# logger = logging.getLogger(__name__)

# def resolve_file_path(data_dir, filename):
#     """Resolve a page file against the booklet data directory."""

#     if filename is None:
#         return None

#     path = Path(filename)

#     # Absolute paths are always used as-is.
#     if path.is_absolute():
#         return path

#     # If there is a booklet data directory, prepend it.
#     if data_dir is not None:
#         return Path(data_dir) / path

#     # Otherwise leave the relative path alone.
#     return path

# def convert_value(value, expected_type):

#     if value is None:
#         return None

#     # Handle int | None, str | None, etc.
#     origin = get_origin(expected_type)

#     if origin is list:
#         item_type = get_args(expected_type)[0] if get_args(expected_type) else object

#         if isinstance(value, str):
#             try:
#                 value = ast.literal_eval(value)
#             except (ValueError, SyntaxError) as exc:
#                 raise ValueError(
#                     f"Cannot convert {value!r} to {expected_type}; "
#                     "use a quoted list literal"
#                 ) from exc

#         if not isinstance(value, list):
#             raise ValueError(
#                 f"Cannot convert {value!r} to {expected_type}"
#             )

#         if item_type is not object and not all(
#             isinstance(item, item_type) for item in value
#         ):
#             raise ValueError(
#                 f"List values must be {item_type.__name__}: {value!r}"
#             )

#         return value

#     if origin in (Union, UnionType):

#         possible_types = [
#             t for t in get_args(expected_type)
#             if t is not type(None)
#         ]

#         if len(possible_types) == 1:
#             expected_type = possible_types[0]

#     if isinstance(value, expected_type):
#         return value

#     if expected_type is bool:

#         if isinstance(value, str):
#             value = value.strip().lower()

#             if value in ("true", "1", "yes", "on"):
#                 return True

#             if value in ("false", "0", "no", "off"):
#                 return False

#             raise ValueError(
#                 f"Invalid boolean value: {value}"
#             )

#         return bool(value)

#     try:
#         return expected_type(value)

#     except (TypeError, ValueError) as exc:
#         raise ValueError(
#             f"Cannot convert {value!r} "
#             f"to {expected_type}"
#         ) from exc


# def set_nested_value(obj, path, value):
#     """Set a value on an object using a dotted attribute path."""
#     target = obj

#     for attribute in path[:-1]:
#         target = getattr(target, attribute)

#     setattr(target, path[-1], value)


# def apply_options(obj, options):
#     """
#     Apply recognized options to a dataclass object.

#     Options use dotted names for nested attributes, for example:

#         font.size=10
#         font.color=blue

#     Returns a dictionary containing options that were not
#     recognized by this object.
#     """

#     remaining = {}

#     for name, value in options.items():

#         path = name.split(".")
#         current = obj

#         try:
#             # Walk through all but the final attribute.
#             for attribute in path[:-1]:
#                 current = getattr(current, attribute)

#             final_attribute = path[-1]

#             # Does the final attribute actually exist?
#             if not hasattr(current, final_attribute):
#                 remaining[name] = value
#                 continue

#             # Get the declared type from the class containing
#             # the final attribute.
#             type_hints = get_type_hints(current.__class__)

#             if final_attribute not in type_hints:
#                 remaining[name] = value
#                 continue

#             expected_type = type_hints[final_attribute]

#             converted_value = convert_value(
#                 value,
#                 expected_type
#             )

#             setattr(
#                 current,
#                 final_attribute,
#                 converted_value
#             )

#         except AttributeError:
#             remaining[name] = value

#     return remaining


# def build_configuration(definitions):
#     pages = []

#     booklet_style = BookletStyle()
#     booklet_config = BookletConfig(pages=pages, style=booklet_style)

#     for entry in definitions:

#         # ---------------------------------
#         # Booklet options
#         # ---------------------------------
#         if entry.page_type == "booklet":

#             remaining = apply_options(
#                 booklet_style,
#                 entry.options
#             )

#             remaining = apply_options(
#                 booklet_config,
#                 remaining
#             )

#             if remaining:
#                 raise ValueError(
#                     f"Unknown booklet options: {remaining}"
#                 )

#             continue

#         # ---------------------------------
#         # Page style
#         # ---------------------------------
#         page_style = PageStyle()

#         remaining = apply_options(
#             page_style,
#             entry.options
#         )

#         # ---------------------------------
#         # Page-specific detail
#         # ---------------------------------
#         page_detail = PageFactory.create_detail(
#             entry.page_type
#         )

#         if page_detail is not None:

#             remaining = apply_options(
#                 page_detail,
#                 remaining
#             )

#         # ---------------------------------
#         # Generic page configuration
#         # ---------------------------------
#         page_config = PageConfig(
#             page_type=entry.page_type,
#             style=page_style,
#             text=entry.text,
#             detail=page_detail
#         )

#         remaining = apply_options(
#             page_config,
#             remaining
#         )

#         if remaining:
#             raise ValueError(
#                 f"Unknown options for page "
#                 f"'{entry.page_type}': {remaining}"
#             )

#         page_config = finalize_page_config(
#             page_config,
#             booklet_config
#         )
#         pages.append(page_config)

#     # from pprint import pprint
#     # pprint(booklet_config, indent=2, depth=4, compact=True)
#     # logger.debug (booklet_config)
#     return booklet_config


# def finalize_page_config(page_config, booklet_config):
#     """Resolve page-level values that depend on booklet configuration."""

#     if page_config.file is not None:
#         page_config.file = resolve_file_path(
#             booklet_config.data_dir,
#             page_config.file
#         )

#     return page_config


# =================================================================== New Version Below
"""
Translates p8 files into the booklet configuration and styles.
"""

import ast
import logging

from dataclasses import fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import get_args, get_origin, get_type_hints, Union

from models.config import (
    PageConfig,
    BookletConfig,
)

from models.styles import (
    BookletStyle,
    PageStyle,
)

from pages.factory import PageFactory

from pages import (
    daily,
    calendar,
    lines,
    grid,
    list as list_page,
    runoff,
    text,
    markdown,
)


logger = logging.getLogger(__name__)


def resolve_file_path(data_dir, filename):
    """
    Resolve a page file against the booklet data directory.

    Absolute paths are used as-is.
    Relative paths are resolved against data_dir when supplied.
    """

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
    """
    Convert a configuration value to the declared Python type.
    """

    if value is None:
        return None

    # ---------------------------------------------------------
    # List types
    # ---------------------------------------------------------

    origin = get_origin(expected_type)

    if origin is list:

        item_type = (
            get_args(expected_type)[0]
            if get_args(expected_type)
            else object
        )

        if isinstance(value, str):

            try:
                value = ast.literal_eval(value)

            except (ValueError, SyntaxError) as exc:

                raise ValueError(
                    f"Cannot convert {value!r} to {expected_type}; "
                    "use a quoted list literal"
                ) from exc

        if not isinstance(value, list):

            raise ValueError(
                f"Cannot convert {value!r} to {expected_type}"
            )

        if (
            item_type is not object
            and not all(
                isinstance(item, item_type)
                for item in value
            )
        ):

            raise ValueError(
                f"List values must be {item_type.__name__}: "
                f"{value!r}"
            )

        return value

    # ---------------------------------------------------------
    # Optional / Union types
    # ---------------------------------------------------------

    if origin in (Union, UnionType):

        possible_types = [
            t
            for t in get_args(expected_type)
            if t is not type(None)
        ]

        if len(possible_types) == 1:
            expected_type = possible_types[0]

    # ---------------------------------------------------------
    # Already correct type
    # ---------------------------------------------------------

    if isinstance(value, expected_type):
        return value

    # ---------------------------------------------------------
    # Boolean
    # ---------------------------------------------------------

    if expected_type is bool:

        if isinstance(value, str):

            value = value.strip().lower()

            if value in (
                "true",
                "1",
                "yes",
                "on"
            ):
                return True

            if value in (
                "false",
                "0",
                "no",
                "off"
            ):
                return False

            raise ValueError(
                f"Invalid boolean value: {value}"
            )

        return bool(value)

    # ---------------------------------------------------------
    # Other types
    # ---------------------------------------------------------

    try:
        return expected_type(value)

    except (TypeError, ValueError) as exc:

        raise ValueError(
            f"Cannot convert {value!r} "
            f"to {expected_type}"
        ) from exc


def set_nested_value(obj, path, value):
    """
    Set a value on an object using a dotted attribute path.

    Example:

        set_nested_value(
            page_style,
            ["body", "font", "size"],
            10
        )
    """

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
        body.font.size=10

    Returns a dictionary containing options that were not
    recognized by this object.
    """

    remaining = {}

    for name, value in options.items():

        path = name.split(".")
        current = obj

        try:

            # -------------------------------------------------
            # Walk through nested attributes.
            # -------------------------------------------------

            for attribute in path[:-1]:
                current = getattr(current, attribute)

            final_attribute = path[-1]

            # -------------------------------------------------
            # Does the final attribute exist?
            # -------------------------------------------------

            if not hasattr(current, final_attribute):

                remaining[name] = value
                continue

            # -------------------------------------------------
            # Get the declared type from the class containing
            # the final attribute.
            # -------------------------------------------------

            type_hints = get_type_hints(
                current.__class__
            )

            if final_attribute not in type_hints:

                remaining[name] = value
                continue

            expected_type = type_hints[
                final_attribute
            ]

            # -------------------------------------------------
            # Convert the configuration value.
            # -------------------------------------------------

            converted_value = convert_value(
                value,
                expected_type
            )

            # -------------------------------------------------
            # Store the converted value.
            # -------------------------------------------------

            setattr(
                current,
                final_attribute,
                converted_value
            )

        except AttributeError:

            remaining[name] = value

    return remaining


def build_configuration(definitions):
    """
    Build the complete BookletConfig from parsed definitions.
    """

    pages = []

    booklet_style = BookletStyle()

    booklet_config = BookletConfig(
        pages=pages,
        style=booklet_style
    )

    for entry in definitions:

        # =====================================================
        # Booklet options
        # =====================================================

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
                    f"Unknown booklet options: "
                    f"{remaining}"
                )

            continue

        # =====================================================
        # Page style
        #
        # This is intentionally an empty override object.
        # Values not specified by the user remain None and
        # will inherit from BookletStyle later.
        # =====================================================

        page_style = PageStyle()

        remaining = apply_options(
            page_style,
            entry.options
        )

        # =====================================================
        # Page-specific detail
        # =====================================================

        page_detail = PageFactory.create_detail(
            entry.page_type
        )

        if page_detail is not None:

            remaining = apply_options(
                page_detail,
                remaining
            )

        # =====================================================
        # Generic page configuration
        # =====================================================

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

        # =====================================================
        # Anything left is unknown.
        # =====================================================

        if remaining:

            raise ValueError(
                f"Unknown options for page "
                f"'{entry.page_type}': "
                f"{remaining}"
            )

        # =====================================================
        # Resolve values that depend on booklet configuration.
        # =====================================================

        page_config = finalize_page_config(
            page_config,
            booklet_config
        )

        pages.append(page_config)

    return booklet_config


def finalize_page_config(page_config, booklet_config):
    """
    Resolve page-level values that depend on booklet configuration.
    """

    if page_config.file is not None:

        page_config.file = resolve_file_path(
            booklet_config.data_dir,
            page_config.file
        )

    return page_config