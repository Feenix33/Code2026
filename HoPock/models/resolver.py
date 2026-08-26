"""
Resolver
Resolve the styles
"""
from copy import deepcopy
from dataclasses import fields, is_dataclass

def merge_style(default, override):
    """
    Return a copy of default with non-None values from override
    recursively applied.
    """

    result = deepcopy(default)

    if override is None:
        return result

    for field in fields(override):

        override_value = getattr(override, field.name)

        # None means "no override"
        if override_value is None:
            continue

        default_value = getattr(result, field.name)

        # Nested dataclass -- recurse
        if (
            is_dataclass(override_value)
            and is_dataclass(default_value)
        ):
            merged = merge_style(
                default_value,
                override_value
            )
            setattr(result, field.name, merged)

        else:
            setattr(
                result,
                field.name,
                override_value
            )

    return result

def resolve_page_style(booklet_style, page_style):
    return merge_style(booklet_style, page_style)