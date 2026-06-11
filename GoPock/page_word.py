from page import Page, PageFactory
# import pprint

@PageFactory.register("blank")
class PageWord(Page):
    def __init__(self, **kwargs):
        super().__init__()

    def draw(self, canvas):
        pass

@PageFactory.register("word")
class PageWord(Page):
    def __init__(self, title="Generic Word Page", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title


    def draw(self, canvas):
        wordFont = self.get_style("fontTitle")
        # pprint.pprint(wordFont)
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        # canvas.setFont("Helvetica", 12)
        # canvas.drawCentredString(Page.mid.x, Page.mid.y, self.title)
        titleFormat = self.get_style("titleFormat")
        pageDate = self.get_style("date")
        # print(f"Title: {self.title}, Format: {titleFormat}, Date: {pageDate}")
        self.printCanvasThreePart(canvas, Page.mid.y, formatStr=titleFormat, titleStr=self.title, date=pageDate)
