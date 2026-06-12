"""
GoPock.py
Entry point for booklet creation.
"""
import pprint

from booklet import Booklet
from page import PageFactory
import page_word
import page_text
import page_lines
from utils import read_page_specs, build_book


def main():
    booklet = Booklet()
    # pprint.pprint(booklet.config)
    specs = read_page_specs("input.txt")
    # print("----- After parsing -----")
    # pprint.pprint(booklet.config)
    # pprint.pprint(specs)

    build_book(booklet, specs, PageFactory)
    booklet.render()


if __name__ == '__main__':
    main()
