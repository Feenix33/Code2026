"""
Central place to build the paragraph styles for use by the processor
Should be called in a page's constrctor
"""
from reportlab.lib.styles import ParagraphStyle

import logging
logger = logging.getLogger(__name__)

class ReportLabStyles:

    def __init__(self, style):
        self.title_style = self._create_paragraph_style(style.titlestyle)
        # self.heading = self._create_paragraph_style(style.heading)
        self.body_style = self._create_paragraph_style(style.bodystyle)

        tt = self.title_style
        logger.debug(f"Style {tt.name}: font={tt.fontName}, size={tt.fontSize}, leading={tt.leading}, spaceAfter={tt.spaceAfter}, spaceBefore={tt.spaceBefore}")
        tt = self.body_style
        logger.debug(f"Style {tt.name}: font={tt.fontName}, size={tt.fontSize}, leading={tt.leading}, spaceAfter={tt.spaceAfter}, spaceBefore={tt.spaceBefore}")

    def _create_paragraph_style(self, text_style):
        return ParagraphStyle(
            name=text_style.name,
            fontName=text_style.font.name,
            fontSize=text_style.font.size,
            textColor=text_style.font.color,
            leading=text_style.leading,
            spaceAfter=text_style.space_after,
            spaceBefore=text_style.space_before,
        )