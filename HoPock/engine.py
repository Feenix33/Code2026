"""
This ties your processors and generators together and compiles the final pages into a PDF.
"""
from dataclasses import dataclass, field
from models.config import BookletConfig, PageConfig
from models.styles import *
from models.data_classes import *
from pages.factory import PageFactory

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen.canvas import Canvas

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

        self.panel_dim = self._define_panel_dim()
        self.panels = self._define_panels()
        self.panel_num = 0

        self.canvas = Canvas(self.cfg.outfile, pagesize=self.cfg.pagesize)
        logger.debug(f"Output to {self.cfg.outfile}")


    def _define_panel_dim(self):
        # compute the size of a panel 
        width, height = self.cfg.pagesize
        margin = self.cfg.margin
        if self.cfg.panels == 8:
            fWidth = (width / 4) - margin * 2
            fHeight = (height / 2) - margin * 2
            dim = Point (y=fHeight, x=fWidth)
        else:
            logger.debug("Other panel counts not immplemented")
            dim = Point (0, 0)
        return dim

    def _define_panels(self):
        """
        Compute the panel corners and rotations
        Currently hardcoded 
        """
        # width, height = self.cfg.pagesize
        margin = self.cfg.margin
        fWidth, fHeight = self.panel_dim.x, self.panel_dim.y

        if fWidth < 1 or fHeight < 1:
            logger.debug("Panel dimension not set")

        if self.cfg.panels == 8:
            # fWidth = (width / 4) - margin * 2
            # fHeight = (height / 2) - margin * 2

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

        # print (f"fwh = {fWidth} {fHeight}")
        # print (f"doc = {width} {height}")
        # print (f"mul = {4*fWidth} {2*fHeight}")
        # print (f"mgn = {margin}")
        return panels

        
    def build(self):
        for pgcfg in self.cfg.pages:
            page = PageFactory.create(pgcfg, self.cfg.style)
            # config: PageConfig, booklet_style: BookletStyle):
            # corner = self.panels[self.panel_num].corner
            # rotate = self.panels[self.panel_num].rotate
            result = False
            resume = False
            while not result: # keep rendering until the page is complete
                corner = self.panels[self.panel_num].corner
                rotate = self.panels[self.panel_num].rotate
                result = page.render(self.canvas, corner, rotate, self.panel_dim, resume=resume)
                if self.cfg.addpages and not result: # if the page is not complete, add a new page
                    resume = True
                else:
                    result = True # exit the loop if the page is complete or addpages is False
                self.panel_num = (self.panel_num + 1) % self.cfg.panels
                if self.panel_num == 0: # we had a rollover 
                    self.canvas.showPage() # start a new page

        # logger.debug ("showPage()")
        if self.panel_num != 0: # we had a rollover 
            self.canvas.showPage() # start a new page
        self.canvas.save()
