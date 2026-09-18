"""
Get the reportlab styles generated on the fly
This is used by the processors
"""
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

from models.styles import Marker

import logging
logger = logging.getLogger(__name__)


"""
Usage:
styles.set("heading", fontSize=14)
    Every subsequent 
        styles.get("heading") returns the 14pt version
    Can also do
        styles.set("heading", fontSize=14, textColor="red")

styles.get("heading", spaceAfter=20)
    Is a temporary override

We could have
    def adjust_font_size(self, percentage):
        for name in self._get_style_names():
            current = self.get(name).fontSize
            new_size = current * (1 + percentage / 100)
            self.set(name, fontSize=new_size)

Then
    styles.adjust_font_size(10) adjusts all font sizes by +10%

But make it explicit rathern than trying to find them all on the fly:
    def _get_style_names(self):
    return (
        "title",
        "body",
        "heading",
    )

Note: If your BookletStyle/effective style is a dataclass containing the styles, we can discover them generically using dataclasses.fields() 
rather than maintaining this list. That would fit very well with your goal of avoiding code that needs to be updated every time you add another style.
We can do that when you get to that point.

For Current Style
current_style = styles.get("body")
If there is a nroff type command like
.PS 14
then
current_style = styles.get(
    "body",
    fontSize=14
)

Do NOT do this: current_style.fontSize = 14
"""

REPORTLAB_FONT_PROPERTIES = {
    "font.name": "fontName",
    "font.size": "fontSize",
    "font.color": "textColor",
    "leading": "leading",
    "space.after": "spaceAfter",
    "space.before": "spaceBefore",
    "alignment": "alignment",
    "bulletfontname": "bulletFontName",
    "bulletfontsize": "bulletFontSize",
    "bulletindent": "bulletIndent",
    "bulletcolor": "bulletColor",
    "first_line_indent": "firstLineIndent"
}


class ReportLabStyleProvider:

    def __init__(self, style):
        self.style = style
        self._styles = {}
        self._overrides = {}

    def get(self, name, **overrides):
        name = name.lower()

        # Start with persistent overrides for this style
        properties = self._overrides.get(name, {}).copy()

        # One-time overrides supplied to this get()
        properties.update(overrides)

        key = (
            name,
            tuple(sorted(properties.items()))
        )

        if key not in self._styles:
            self._styles[key] = self._create_style(
                name,
                properties
            )

        return self._styles[key]

    def set(self, name, **overrides):
        name = name.lower()

        if name not in self._overrides:
            self._overrides[name] = {}

        self._overrides[name].update(overrides)

        # Existing cached styles may now be stale
        self._styles.clear()

    def _create_style(self, name, overrides):
        #cme I added these 2 lines, not sure if this is proper, it is to catch getattr error that follows
        if not hasattr(self.style, name):
            raise ValueError(f"Unknown style: {name}")
        
        text_style = getattr(self.style, name)
        font = text_style.font

        alignment_map = {
            "left": TA_LEFT,
            "center": TA_CENTER,
            "right": TA_RIGHT,
            "justify": TA_JUSTIFY,
        }

        properties = {
            "name": name,
            "fontName": font.name or "Helvetica",
            "fontSize": font.size or 8,
            "textColor": font.color or "black",
            "leading": text_style.leading or 10,
            "spaceAfter": text_style.space_after or 0,
            "spaceBefore": text_style.space_before or 0,
            "alignment": alignment_map.get(
                (text_style.alignment or "left").lower(),
                TA_LEFT
            ),
            "bulletFontName": text_style.bulletfontname or "Helvetica", 
            "bulletFontSize": text_style.bulletfontsize or 8, 
            "bulletIndent": (text_style.bulletindent if text_style.bulletindent is not None else 0), 
            "bulletColor": text_style.bulletcolor or "black",
            "firstLineIndent": (text_style.first_line_indent if text_style.first_line_indent is not None else 0),
        }


        properties.update(overrides)

        return ParagraphStyle(**properties)

    def derive1(self, base_style, options):

        properties = {
            "fontName": base_style.fontName,
            "fontSize": base_style.fontSize,
            "textColor": base_style.textColor,
            "leading": base_style.leading,
            "spaceAfter": base_style.spaceAfter,
            "spaceBefore": base_style.spaceBefore,
            "alignment": base_style.alignment,
        }

        for name, value in options.items():

            if name == "font.name":
                properties["fontName"] = value

            elif name == "font.size":
                properties["fontSize"] = value

            elif name == "font.color":
                properties["textColor"] = value

        return ParagraphStyle(
            name=f"{base_style.name}_variant",
            **properties
        )



    def derive(self, base_style, options):

        properties = {
            "fontName": base_style.fontName,
            "fontSize": base_style.fontSize,
            "textColor": base_style.textColor,
            "leading": base_style.leading,
            "spaceAfter": base_style.spaceAfter,
            "spaceBefore": base_style.spaceBefore,
            "alignment": base_style.alignment,
        }

        for name, value in options.items():
            reportlab_name = REPORTLAB_FONT_PROPERTIES.get(name)

            if reportlab_name is None:
                raise ValueError(f"Unknown style option: {name}")

            if name == "alignment" and isinstance(value, str):
                alignment_values = {
                    "left": TA_LEFT,
                    "center": TA_CENTER,
                    "right": TA_RIGHT,
                    "justify": TA_JUSTIFY,
                }
                try:
                    value = alignment_values[value.lower()]
                except KeyError as error:
                    raise ValueError(f"Unknown alignment: {value}") from error

            properties[reportlab_name] = value

        if "font.size" in options and "leading" not in options:
            properties["leading"] = properties["fontSize"] * 1.2
            logger.debug ("Automatic leading computation")
            

        return ParagraphStyle(
            name=f"{base_style.name}_variant",
            **properties
        )

    # def get_marker(self, style_name):
    #     """
    #     Return the marker definition for a style.

    #     The marker is stored in the HoPock TextStyle, not in
    #     the ReportLab ParagraphStyle.

    #     Returns:
    #         Marker object, or None if the style has no marker.
    #     """
    #     text_style = self._styles.get(style_name.lower())

    #     if text_style is None:
    #         raise ValueError(f"Unknown style: {style_name}")

    #     if text_style.marker is None:
    #         return None

    #     return Marker(
    #         text=text_style.marker,
    #         font=text_style.marker_font
    #     )

    def get_markerSIMPLE(self, style_name):
        """
        Return the marker definition for a style.

        The marker is stored in the HoPock TextStyle, not in
        the ReportLab ParagraphStyle.

        Returns:
            Marker object, or None if the style has no marker.
        """
        style_name = style_name.lower()

        if not hasattr(self.style, style_name):
            raise ValueError(f"Unknown style: {style_name}")

        text_style = getattr(self.style, style_name)

        if text_style.marker is None:
            return None

        return text_style.marker

    def get_marker(self, style_name, **overrides):
        style_name = style_name.lower()

        if not hasattr(self.style, style_name):
            raise ValueError(f"Unknown style: {style_name}")

        text_style = getattr(self.style, style_name)

        if text_style.marker is None:
            return None

        marker = text_style.marker

        # Start with the base marker
        result = {
            "type": marker.type,
            "text": marker.text,
        }

        # Apply overrides
        result.update(overrides)

        return Marker(**result)