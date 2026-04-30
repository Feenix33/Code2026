import sys
import os
from fpdf import FPDF
import csv
import datetime
import configparser
import logging
import argparse
import calendar
from pprint import pprint
#import re

'''
ToDo
x Create an ini file for reading in doc parameters
x Base class has the ini and defn files
x Frame on title and backpage and each page
x Better control on book defn file
x Other page types besides recipe
x image as a pane; add actual, width, height fit, left, centered
x standard error output / python std?
x logging
x default image sizing
x Book publishing with defn on command line
x pass body txt in ini file
x add tag to gen text to handle title and convert recipes

o nroff parser for pane
o pocket planner pages
o   calendar
o   weekly
o   daily
o   checkboxes
o   lines
o   grid / dots
'''

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__('L', 'in','Letter')
        self.config = configparser.ConfigParser()

        # added stuff
        #ini_file = "book.ini"
        if 'ini' in kwargs:
            logging.debug ("Processing ini file: {}".format( kwargs['ini']))
            ini_file = kwargs['ini']
        self.read_ini(ini_file)
        self.build_panes()


    def read_ini(self, iniFile):
        # setup the config parser
        self.config = configparser.ConfigParser()
        self.config.read(iniFile)
        default = self.config['Default']
        # read in the layout parameters
        self.page_margin = default.getfloat('PageMargin', 0.2)
        self.pane_margin = default.getfloat('PaneMargin', 0.2)
        self.pane_font_size = default.getint('PaneFontSize', 7)
        self.font = "Arial"
        self.back_font_size = default.getint('BackFontSize', 6)
        self.title_font_size = default.getint('TitleFontSize', 14)
        self.author_font_size = default.getint('AuthorFontSize', 10)
        self.title_position = default.getint('TitlePosition', 40)
        self.pane_use_width = default.getfloat('PaneUseWidth', 0.80)
        self.pt2in = 0.0138889
        self.title_frame = default.getboolean('TitleFrame', True)
        self.back_frame = default.getboolean('BackFrame', True)
        self.out_fname = default.get('OutputFile', "Boomlet.pdf")

        default_format = default.get('DefaultFormat', "Text")
        self.pane_format = [default_format] * 8 #init the 8 pages to the default
        for j in range(8):
            self.pane_format[j] = default.get('P'+str(j+1)+'Format', default_format)

        # Read the book specific portions
        infiles = default.get('InFiles', "")
        self.infiles = infiles.split(",")
        self.infiles = [t.strip() for t in self.infiles]

        self.pictures = default.get("Pictures","")
        self.pictures = self.pictures.split(",")
        self.pictures = [t.strip() for t in self.pictures]

        default_fit = default.get("PicturesFitDefault","width")
        self.pictures_fit = [default_fit]*len(self.pictures)
        pictures_fit = default.get("PicturesFit","")
        pictures_fit = pictures_fit.split(",")
        if len(pictures_fit) == len(self.pictures_fit):
            self.pictures_fit = [t.strip() for t in pictures_fit]

        self.title = default.get('Title', "Booklet Title")
        self.author = default.get('Author', "<< author >>")
        self.date = default.get('Date', "<< date >>")
        self.edition = default.get('Edition', "<< edition >>")
        self.book8up = "1.0" # no get

        self.infile_text = []
        for j in range(8):
            txt = default.get('Infile'+str(j+1), "")
            if len(txt) > 0:
                self.infile_text.append (txt)

        self.commands = []
        for j in range(8):
            txt = default.get('Command'+str(j+1), "")
            if len(txt) > 0:
                self.commands.append (txt)

    def build_panes(self):
        # hardcoded
        #self.page_margin = self.ipage_margin
        #self.pane_margin = self.ipane_margin
        paneW = (11 - 2*self.page_margin - 3*self.pane_margin)/4
        paneH = (8.5 - 2*self.page_margin - self.pane_margin)/2
        self.pane_width = (11 - 2*self.page_margin - 3*self.pane_margin)/4
        self.pane_height = (8.5 - 2*self.page_margin - self.pane_margin)/2
        self.panes = []
        for h  in range (1,3):
            for w in range (1,5):
                x1 = self.page_margin + (w-1)*(self.pane_width + self.pane_margin)
                y1 = self.page_margin + (h-1)*(self.pane_height + self.pane_margin)
                x2 = x1 + self.pane_width
                y2 = y1 + self.pane_height
                self.panes.append([x1, y1])
        j=0

    def bold(self):
        self.set_font(self.font,'B',self.pane_font_size)

    def normal(self):
        self.set_font(self.font,'',self.pane_font_size)

    def process(self):
        self.add_page()
        self.set_margins(self.page_margin, self.page_margin, self.page_margin)

        jinf = 0
        jpf = 0
        jpic = 0
        jinfile = 0
        jcommand = 0
        for pfmt in self.pane_format:
            if pfmt == "front":
                logging.debug("Generating front on pane {}".format(jpf))
                self.gen_front(jpf)
            elif pfmt == "back":
                logging.debug("Generating back on pane {}".format(jpf))
                self.gen_back(jpf)
            elif pfmt == "recipe":
                logging.debug("Generating recipe {} on pane {}".format(self.infiles[jinf], jpf)) 
                txt = self.get_file_text(self.infiles[jinf])
                self.gen_text_pane(jpf, txt, title=True)
                #self.gen_recipe(jpf, self.infiles[jinf])
                jinf += 1
            elif pfmt == "text":
                logging.debug("Generating text {} on pane {}".format(self.infiles[jinf], jpf)) 
                txt = self.get_file_text(self.infiles[jinf])
                self.gen_text_pane(jpf, txt, title=False)
                jinf += 1
            elif pfmt == "infile":
                logging.debug("Generating infile {} on pane {}".format(self.infiles[jinf], jpf)) 
                self.gen_text_pane(jpf, self.infile_text[jinfile], title=False)
                jinfile += 1
            elif pfmt == "intitle":
                logging.debug("Generating intitle {} on pane {}".format(self.infiles[jinf], jpf)) 
                self.gen_text_pane(jpf, self.infile_text[jinfile], title=True)
                jinfile += 1
            elif pfmt == "picture":
                logging.debug("Generating picture {} on pane {} with {} sizing".format(
                    self.pictures[jpic], jpf, self.pictures_fit[jpic]))
                self.gen_picture(jpf, self.pictures[jpic], self.pictures_fit[jpic])
                jpic += 1
            elif pfmt == "calendar":
                logging.debug("Generating calendar {} on pane {}".format("XX", jpf)) 
                self.gen_calendar(jpf)
            elif pfmt == "blank":
                pass
            elif pfmt == "command":
                self.gen_command(jpf, self.commands[jcommand])
                jcommand += 1
                pass
            else:
                logging.error ("Error unknown format {}".format(pfmt))
            jpf += 1

    def gen_calendar(self, pane_index):
        txt = calendar.calendar(2021,w=1,c=1,m=2)
        font_size = self.pane_font_size
        self.pane_font_size = 6
        self.font = 'Courier'
        self.normal()

        self.gen_text_pane(pane_index, txt, title=False)
        self.pane_font_size = font_size
        self.font = 'Arial'

        self.normal()


    def gen_command(self, pane_index, cmds_in):
        '''
         box 10 20 50 dim x y
         color 255 0 0
        '''
        xp = lambda x: px + (x*pw/100.)
        yp = lambda y: py + (y*ph/100.)
        def cmd_frame(stack):
            logging.debug("frame command")
            self.line (px, py, px+pw, py)
            self.line (px, py+ph, px+pw, py+ph)
            self.line (px, py, px, py+ph)
            self.line (px+pw, py, px+pw, py+ph)

        def cmd_horzs(stack):
            # s1 number of horizontal lines
            # s2 if present then put a line at the top
            logging.debug("horzs command: {}".format(stack))
            number = int(stack.pop(0))
            delta_y = 100/number
            if stack: # assume second variable is true, TODO test later? 
                y = 0
                number += 1
            else: 
                y = delta_y
            for n in range(number):
                self.line(xp(0), yp(y), xp(100), yp(y))
                y += delta_y

        def cmd_verts(stack):
            logging.debug("verts command {}".format(stack))
            number = int(stack.pop(0))
            delta_x = 100/number
            if stack: # assume second variable is true, TODO test later? 
                x = 0
                number += 1
            else:
                x = delta_x
            for n in range(number):
                self.line(xp(x), yp(0), xp(x), yp(100))
                x += delta_x

        def cmd_rect(stack):
            logging.debug("rect command")
            x1, y1, x2, y2 = map(int, stack)
            self.rect ( xp(x1), yp(y1), xp(x2)-xp(x1), yp(y2)-yp(y1))

        def cmd_box(stack):
            aspect = ph / pw
            logging.debug("box command aspect {}".format(aspect))
            x1, y1, dim = map(int, stack)
            self.rect (xp(x1), yp(y1), (dim*pw/100.), (dim / aspect *ph/100.))

        def cmd_grid(stack):
            # 0 % witdh across
            # 1 number of grid buffer
            logging.debug("grid command {}".format(stack))
            dim = int(stack[0]) * pw / 100.
            margin = int(stack[1]) if 1 < len(stack)  else 0
            nx = int(pw/dim) - 2 *margin #number of lines so no spill
            ny = int(ph/dim) - 2 *margin
            width = nx*dim
            height = ny*dim
            xoff = (pw-width) / 2
            yoff = (ph-height) / 2
            logging.debug("     grid x y   {} {}".format(nx, ny))
            logging.debug("     grid margin {}".format(margin))
            #for n in range(margin, nx+1-margin):
            for n in range(nx+1):
                self.line(n*dim+xoff, yoff, n*dim+xoff, height+yoff)
            for n in range(ny+1):
                self.line(xoff, n*dim+yoff, width+xoff, n*dim+yoff)

        def cmd_color(stack):
            self.set_draw_color(int(stack[0]), int(stack[1]), int(stack[2]))


        processor = {
                'frame' : cmd_frame,
                'horzs' : cmd_horzs,
                'verts' : cmd_verts,
                'box': cmd_box,
                'color' : cmd_color,
                'rect' : cmd_rect,
                'grid' : cmd_grid,
                }

        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        ph = self.pane_height
        logging.debug ("Processing commands on {}".format (pane_index))
        cmds = cmds_in.splitlines()
        for cmd in cmds:
            tokens = cmd.split()
            if tokens[0][0] == '#': continue
            func = processor.get(tokens[0])
            func(tokens[1:])
                


    def gen_picture(self, pane_index, infile, fit):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        self.normal()
        #self.image(infile, px, py, pw, self.pane_height)
        if fit=="actual":
            self.image(infile, px, py)
        elif fit=="width":
            self.image(infile, px, py, pw)
        elif fit=="height":
            self.image(infile, px, py, h=self.pane_height)
        elif fit=="fit":
            self.image(infile, px, py, pw, self.pane_height)
        else:
            logging.error ("Error unknown image fit= {}".format(fit))


    def gen_text_pane(self, pane_index, txt, title=False):
        '''
        Text is passed in
        title=true look for the first CR and bold then rest is normal
        '''
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        mch = self.pane_font_size * 1.1 * self.pt2in

        j = -1
        if title:
            j = txt.find('\n')
            self.set_xy(px, py)
            self.bold()
            self.multi_cell(pw, (mch*1.2), txt[:j], align='C')
            py = self.get_y()
        self.normal()
        self.set_xy(px, py)
        self.multi_cell(pw, mch, txt[(j+1):], align='L')

    def gen_back(self, pane_index=2):
        self.set_font('Arial','', self.back_font_size)
        mch = self.back_font_size * 1.3 * self.pt2in

        #adjust width to make narrower
        pw_adjustment = 2
        back_align = 'C'
        px = self.panes[pane_index][0] + pw_adjustment *self.pane_margin
        py = self.panes[pane_index][1] + (1*self.pane_height/2)
        pw = self.pane_width - 2*pw_adjustment *self.pane_margin #double for left&right

        self.set_xy(px, py)
        txt = self.title
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.author:
            self.set_x(px)
            txt = "by {}".format(self.author)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.edition:
            self.set_x(px)
            txt = "{} Edition".format(self.edition)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        now = datetime.datetime.now().strftime("%d %B %Y")
        self.set_x(px)
        txt = "Created on {}".format(now)
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.book8up:
            self.set_x(px)
            txt = "using book8up.py Ver {}".format(self.book8up)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.back_frame: self.pane_frame(pane_index)


    def gen_front(self, pane_index=7, title_text=None):
        txt = title_text or self.title

        pane_mar = (1.0 - self.pane_use_width)/2
        pw = self.pane_width * self.pane_use_width

        self.set_font('Arial','B', self.title_font_size)
        mch = self.title_font_size * 1.3 * self.pt2in

        sw = self.get_string_width(txt)
        px = self.panes[pane_index][0] + (self.pane_width * pane_mar)
        py = self.panes[pane_index][1] + (self.pane_height*self.title_position/100.0) - mch * (int(sw/pw)+1)
        #xxxx

        self.set_xy(px, py)


        self.multi_cell(pw, mch, txt, align='C', border=0)
        sw = self.get_string_width(txt)

        self.set_font('Arial','', self.author_font_size)
        self.set_x(px)
        self.multi_cell(pw, mch, "\n", align='C', border=0)
        txt = self.author
        self.set_x(px)
        self.multi_cell(pw, mch, txt, align='C', border=0)
        
        if self.title_frame: self.pane_frame(pane_index)


    def pane_frame(self, pane_index):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        self.line(px, py, px+self.pane_width, py)
        self.line(px, py+self.pane_height, px+self.pane_width, py+self.pane_height)
        self.line(px, py, px, py+self.pane_height)
        self.line(px+self.pane_width, py, px+self.pane_width, py+self.pane_height)


    def get_file_text(self, infile):
        # convert to a try catch eventually for file does not exist cases
        with open(infile, 'r') as fh:
            txt = fh.read()
        fh.close ()
        return txt

    def publish(self):
        logging.debug("publish() booklet to file {}".format(self.out_fname))
        self.output(self.out_fname)



if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(message)s', 
            datefmt='%I:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("defn_file", nargs='?', default='book.ini', help="Booklet definition file")
    args = parser.parse_args()

    logging.debug("Running book.py")


    logging.debug ("Creating object")
    book = Booklet(ini=args.defn_file)
    
    logging.debug ("Processing")
    book.process()
    
    logging.debug ("Publishing")
    book.publish()
    logging.debug ("Fini\n")
