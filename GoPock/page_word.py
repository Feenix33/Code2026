from page import Page, PageFactory
# import pprint


@PageFactory.register("word")
class PageWord(Page):
    def __init__(self, title="Generic Word Page", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title


    def draw(self, canvas):
        wordFont = self.get_style("fontTitle")
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        titleFormat = self.get_style("titleFormat")
        pageDate = self.get_style("date")
        # print(f"Title: {self.title}, Format: {titleFormat}, Date: {pageDate}")
        self.printCanvasThreePart(canvas, self.mid.y, formatStr=titleFormat, titleStr=self.title, date=pageDate)
