"""
This ties your processors and generators together and compiles the final pages into a PDF.
"""

from processors import AsciiProcessor, MarkdownProcessor, ImageProcessor
from generators import CurrentMonthGenerator, TableOfContentsGenerator

class BookletEngine:
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

