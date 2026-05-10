"""
Pocket planner 8-pg
72 points per inch

fonts: Helvetica, Times, Courier
Alignment: 0-TA_LEFT 1-center 2-right 4-justify

This order:
    3R   2R
    4    1

Eight is 
7 6 5 4 upside down
8 1 2 3

COMMANDS
.font <font params> adjust the current font
.newpage    force a framebreak (page because pocket docs)
.spacer     add a spacer of current font size
.file       Read in a file and process it, ignore config in the file 

CONFIG
.frames     Show frames
.fold       Show folds 
.margin #   Size of margins
.separator  Separator/spacer after every paragraph
.version    Version number

PAGES
.grid <spacing> <color>
.lines <spacing> <color>
.day <start> <last> <spacing> <date>
.week <start>
.month <start>
.year <year>
.todo <title> <spacing>
.shop <title>


FONT PARAMETERS
            textColor=colors.black,
            backColor=colors.white,
            alignment=reportlab.lib.enums.TA_LEFT,
            align=None,
            firstLineIndent=0,
            leftIndent=0,
            bulletIndent=0,
            fontName='Helvetica',
            fontSize=10,
            spaceBefore=0,
            spaceAfter=None,
            leading=None):

NOTES:
- The padding is between the border and the text in the prototype:
    Frame(x1, y1, width,height, leftPadding=6, bottomPadding=6, rightPadding=6, topPadding=6, id=None, showBoundary=0)

"""

import argparse
import sys
import os
import datetime
import re
import unicodedata
from reportlab.lib.pagesizes import A4, landscape, letter, portrait
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
import reportlab.lib.enums 
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Spacer, Paragraph, PageBreak, Image

class Planner: 
    def __init__(self,nameOut="output.pdf", docSize=letter, marginSize=0.2*inch, showFrames=True, drawFolds=True, separator=False):
        self.docSize = docSize
        self.margin = marginSize # how big is the margin for each frame
        self.showFrames = showFrames # show the frame borders
        self.drawFolds = drawFolds # draw the fold lines or not
        self.frameN = 0 # control variable
        self.canvas = None
        self.layout = None
        self.nameOut = nameOut
        self.fontSize = None
        self.separator = separator # put a spacer after every paragraph
        self.author = None # Metadata
        self.title = None # Metadata
        self.subject = None # Metadata
        self.keywords = None # Metadata
        self.version = None
    
    def create(self):
        if self.layout == None: self.layout = 8
        if self.layout == 8 or self.layout == 2: self.docSize = landscape(self.docSize) # other functions dependent upon layout
        if self.fontSize == None:
            self.fontSize = 8
        self.frames, self.frameRotate = self.defineFrames()
        self.currentStyle = self.buildParagraphStyle(fontSize=self.fontSize, spaceAfter= 0)
        self.canvas = Canvas(self.nameOut, pagesize=self.docSize)
        self.frameN = 0
        self.currentFrame = self.frames[self.frameN]
        if self.showFrames: self.currentFrame.drawBoundary(self.canvas)
        if self.drawFolds: self.drawFoldlines() #self.canvas)

    def defineFrames(self):
        width, height = self.docSize
        def defineFrame(x,y, w,h, m):
            return Frame(x+m, y+m, w-m-m, h-m-m)
        # 6 5 4 3 upside down
        # 7 0 1 2
        fWidth = width / 4
        fHeight = height / 2

        f0 = defineFrame(0*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f1 = defineFrame(1*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f2 = defineFrame(2*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f3 = defineFrame(3*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        # top half (upside down)
        f4 = defineFrame(0*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f5 = defineFrame(1*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f6 = defineFrame(2*fWidth, 0*fHeight, fWidth, fHeight, self.margin)
        f7 = defineFrame(3*fWidth, 0*fHeight, fWidth, fHeight, self.margin)

        frames = [f1, f2, f3, f4, f5, f6, f7, f0]
        rotate = [False, False, False, True, False, False, False, True]

        return frames, rotate

    def buildParagraphStyle(self, name='CurrentStyle',
            textColor=colors.black,
            backColor=colors.white,
            alignment=reportlab.lib.enums.TA_LEFT,
            align=None,
            firstLineIndent=0,
            leftIndent=0,
            bulletIndent=0,
            fontName='Times', #'Helvetica',
            fontSize=10,
            spaceBefore=0,
            spaceAfter=None,
            leading=None):
        if leading == None: leading = int(fontSize * 1.2)
        if spaceAfter == None: spaceAfter = int(fontSize * 1.2)
        tempAlign = alignment if align == None else self.alignmentStrToEnum(align.lower())
        return ParagraphStyle(
            name=name,
            backColor = backColor,
            textColor = textColor,
            alignment = tempAlign,
            firstLineIndent = firstLineIndent,
            leftIndent=leftIndent,
            bulletIndent=bulletIndent,
            fontName=fontName,
            fontSize=fontSize,
            spaceBefore=spaceBefore,
            spaceAfter=spaceAfter,
            leading=leading)

    def drawFoldlines(self):
        self.canvas.saveState()
        self.canvas.setDash(1,5) # on off
        self.canvas.line(0, self.docSize[1]/2, self.docSize[0], self.docSize[1]/2)
        self.canvas.setStrokeColor('red')
        for x in [2.75, 5.5, 8.25]: #TODO adjust to doc size
            self.canvas.line(x*inch, 0*inch, x*inch, 8.5*inch)
        self.canvas.restoreState()

    def RotatePage(self):
        self.canvas.translate(self.docSize[0]/2, self.docSize[1]/2)
        self.canvas.rotate(180)
        self.canvas.translate(-self.docSize[0]/2, -self.docSize[1]/2)

    def makePlanner(self, inConfig):
        self.build()
        
    def build(self):
        if self.author != None: self.canvas.setAuthor(self.author)
        if self.title != None: self.canvas.setTitle(self.title)
        if self.subject != None: self.canvas.setSubject(self.subject)
        if self.keywords != None: self.canvas.setKeywords(self.keywords)
        self.canvas.save()


##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### 


def main():
    #Read command line arguments
    config = None
    outputFilename = 'Planner.pdf'

    booklet = Planner(nameOut=outputFilename)
    booklet.makePlanner(config)

if __name__ == '__main__':
    main()
