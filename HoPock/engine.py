"""
This ties your processors and generators together and compiles the final pages into a PDF.
"""
from dataclasses import dataclass, field
from models.config import BookletConfig, PageConfig
from models.data_classes import *

import logging

logger = logging.getLogger(__name__)

"""
class OrigBookletEngine:
    def __init__(self, pages_list, output_name):
        self.pages_list = pages_list
        self.output_name = output_name
        
        # Registry mapping your .p8 commands to their proper classes
        self.registry = {
            "ascii": AsciiProcessor(),
            "markdown": MarkdownProcessor(),
            "image": ImageProcessor(),
            "internal_month": CurrentMonthGenerator(),
            "internal_toc": TableOfContentsGenerator()
        }

    def build(self):
        compiled_pages = []
        
        for page in self.pages_list:
            proc_type = page["processor"]
            target = page["target"]
            
            if proc_type in self.registry:
                worker = self.registry[proc_type]
                # Process the file or run the internal generator
                content = worker.process(target)
                compiled_pages.append(content)
            else:
                print(f"Warning: Unknown processor '{proc_type}'. Skipping page.")
        
        # NOTE: This is where you would feed 'compiled_pages' into a PDF package 
        # like ReportLab, FPDF2, or WeasyPrint to draw the booklet.
        print(f"DEBUG: Assembling {len(compiled_pages)} pages into {self.output_name}")
"""

@dataclass
class Panel:
    corner: Point
    rotate: bool

class BookletEngine:
    def __init__(self, cfgBooklet: BookletConfig):
        self.cfg = cfgBooklet # copy the booklet config

        # convenience variables
        
        logger.debug ("Engine created ")
        logger.debug (f"panels {self.cfg.panels}")

        self.panels = self._define_panels()
        for p in self.panels:
            print (p)


    def _define_panels(self):
        """
        Compute the panel corners and rotations
        Currently hardcoded for the panelss
        """
        width, height = self.cfg.pagesize
        margin = self.cfg.margin

        if self.cfg.panels == 8:
            fWidth = (width / 4) - margin * 2
            fHeight = (height / 2) - margin * 2

            f0 = Point(0 * fWidth + 1 * margin, 0 * fHeight + 1 * margin)
            f1 = Point(1 * fWidth + 3 * margin, 0 * fHeight + 1 * margin)
            f2 = Point(2 * fWidth + 5 * margin, 0 * fHeight + 1 * margin)
            f3 = Point(3 * fWidth + 7 * margin, 0 * fHeight + 1 * margin)
            # corners = [f0, f1, f2, f3, f0, f1, f2, f3] #ORIG
            corners = [f1, f2, f3, f0, f1, f2, f3, f0]
            rotate = [False, False, False, True, True, True, True, False]
        else:
            logger.debug("Other panel counts not immplemented")

        panels = []
        for c, r in zip(corners, rotate):
            panels.append(Panel(c, r))
        return panels

        
    def build(self):
        compiled_pages = []
        print(f"DEBUG: Assembling {len(compiled_pages)} pages into {self.output_name}")
