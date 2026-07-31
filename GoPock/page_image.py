from page import Page, PageFactory
import PIL
# import pprint


@PageFactory.register("image")
class PageImage(Page):
    def __init__(self, title="Image Page", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title

    def draw(self, canvas):
        wordFont = self.get_style("fontTitle")
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        titleFormat = self.get_style("titleFormat")
        # pageDate = self.get_style("date")
        image1 = self.get_style("file")
        image2 = self.get_style("file2")

        if image1 is not None: print (image1)
        if image2 is not None: print (image2)
        # print(f"Title: {self.title}, Format: {titleFormat}, Date: {pageDate}")
        # self.printCanvasThreePart(canvas, self.mid.y, formatStr=titleFormat, titleStr=self.title, date=None)

        x = 10
        y = 10 #self.max.y - 10
        ww = self.max.x - 20
        hh = self.max.y - 20
        canvas.drawImage(image1, x, y, width=ww, height=hh) #, mask=None)
