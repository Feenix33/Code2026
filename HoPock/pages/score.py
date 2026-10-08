import logging
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import ScorePageDetail
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

SCORE_MAX_COUNT = 5
SCORE_MIN_COUNT = 2

""" 
Options
    count: int = 0              # max number of items 0 = infinite
    players: str = None         # polayer names  separated by | 
"""
@PageFactory.register(
    "score",
    detail_class=ScorePageDetail
)
class ScorePage(Page):
    # LIST_PAGE_DEFAULT_FONT_SIZE = 14

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def _init_layout(self):
        """Initializes shared configurations, fonts, and sets up baseline tracking variables."""
        self._set_Line_format_default()
        self._set_font(self.style.font_medium)
        lineht = self.leading

        if self.config.titletext:
            ypos = self._draw_title() - lineht
        else:
            ypos = self.max.y - lineht*1.5

        
        # ypos -= lineht * 1.0

        # Build shared label list
        label_list = []
        if self.detail.players:
            label_list = self.detail.players.split("|")
        if len(self.config.text):
            label_list = self.config.text

        # Determine limit
        count = self.detail.count if self.detail.count else SCORE_MAX_COUNT
        if count < 0:
            count = len(label_list)
        count = max(count, SCORE_MIN_COUNT)
        count = min(count, SCORE_MAX_COUNT)


        return ypos, lineht, label_list, count

    def draw(self, resume=False):
        logger.debug(f"Score sheet details={self.detail}")
        ypos, lineht, label_list, count = self._init_layout()

        dx = self.max.x / count

        xpos = dx/2
        for n in range(count):
            if len(label_list) > n and label_list[n]:
                self.canvas.drawCentredString(xpos, ypos, label_list[n])
            xpos += dx

        xpos = dx
        # draw vertical lines
        for n in range(count-1):
            self.canvas.line(xpos, ypos, xpos, self.mgn)
            xpos += dx

        # draw a horizontal
        ypos -= lineht * 1.5
        if len(label_list) > 0:
            ypos += lineht/2
        self.canvas.line(self.mgn, ypos, self.max.x-self.mgn, ypos)
