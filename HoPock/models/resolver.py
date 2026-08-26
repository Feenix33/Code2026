"""
Resolver
Resolve the styles
"""
from dataclasses import fields


from dataclasses import fields, is_dataclass
from copy import deepcopy

# def merge_styles(default, override):
#     """
#     Return a copy of default with non-None values from override
#     applied recursively.
#     """

#     result = deepcopy(default)

#     if override is None:
#         return result

#     for field in fields(override):

#         override_value = getattr(override, field.name)

#         if override_value is None:
#             continue

#         default_value = getattr(result, field.name)

#         if (
#             is_dataclass(override_value)
#             and is_dataclass(default_value)
#         ):
#             merged = merge_styles(
#                 default_value,
#                 override_value
#             )
#             setattr(result, field.name, merged)

#         else:
#             setattr(
#                 result,
#                 field.name,
#                 override_value
#             )

#     return result


# def resolve_page_style(booklet_style, page_style):
#     return merge_styles(booklet_style, page_style)


from copy import deepcopy


def resolve_page_style(booklet_style, page_style):
    style = deepcopy(booklet_style)

    if page_style is None:
        return style

    if page_style.font.name is not None:
        style.font.name = page_style.font.name

    if page_style.font.size is not None:
        style.font.size = page_style.font.size

    if page_style.font.color is not None:
        style.font.color = page_style.font.color

    if page_style.showpage is not None:
        style.showpage = page_style.showpage

    return style