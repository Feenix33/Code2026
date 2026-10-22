import logging
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import DicePageDetail
from reportlab.pdfbase.pdfmetrics import stringWidth
import random
import re

logger = logging.getLogger(__name__)


""" 
Options
    die         # string of rolls and die
"""
@PageFactory.register(
    "dice",
    detail_class=DicePageDetail
)




class DicePage(Page):

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def _parse_dice(self, die_string: str) -> tuple[int, int]:
        """Parses a dice string (e.g., '2d6', 'd8', '5') into (roll, die).
        
        Defaults roll to 1 and die to 6 if missing or unparseable.
        """
        if not die_string:
            return 1, 6
            
        # Convert to lowercase to handle 'D' or 'd' uniformly
        normalized = die_string.lower().strip()
        
        # Split by the 'd' character if it exists
        if 'd' in normalized:
            parts = normalized.split('d')
            roll_part = parts[0]
            die_part = parts[1] if len(parts) > 1 else ""
        else:
            # If no 'd' is present, the entire string represents the die face count
            roll_part = ""
            die_part = normalized

        # Extract digits or apply default fallbacks
        roll = int(roll_part) if roll_part.isdigit() else 1
        die = int(die_part) if die_part.isdigit() else 6
        
        return roll, die


    def draw(self, resume=False):
        logger.debug(f"Dice sheet details={self.detail}")

        self._set_Line_format_default()
        self._set_font(self.style.font_fixed)
        lineht = self.leading

        dice_string = self.detail.die
        if self.detail.dice:
            dice_string = self.detail.dice
        nroll, ndie = self._parse_dice(dice_string)

        titletext = self.config.titletext
        if not titletext:
            titletext = f"Dice Sheet {nroll}d{ndie}"
        ypos = self._draw_title(title_str=titletext) - lineht

        xpos = self.mgn
        # self.canvas.drawString(xpos, ypos, "Roll some dice")

        # compute the max string
        font_name = self.style.font_fixed.name
        font_size = self.style.font_fixed.size
        available_width = self.max.x - 2*self.mgn  # e.g., page width minus margins
        # Calculate the width of a single character (like 'A' or ' ')
        char_width = stringWidth('A', font_name, font_size)
        # Calculate max length
        max_chars = int(available_width // char_width)

        # compute the max roll width
        max_value = ndie**nroll
        digits = len(str(max_value))
        rolls_per_line = max_chars // (digits+1)
        # logger.debug(f"Max chars = {max_chars}  max rolls={rolls_per_line} digits={digits} max={max_value}")
        while ypos > lineht:
            outstr = ""
            for _ in range(rolls_per_line):
                roll_total = sum(random.randint(1, ndie) for _ in range(nroll))
                outstr += f"{roll_total:{digits}} "
            self.canvas.drawString(xpos, ypos, outstr)
            ypos -= lineht


