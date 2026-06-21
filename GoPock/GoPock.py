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
import page_grid
import page_checklist
import page_weekly
from utils import read_page_specs, build_book

"""
Main TODO:

- Weekly

- Text processor

Refactor TODO:


Hints:
Print current fuction name
import inspect
inspect.currentframe().f_code.co_name

================================================================================================
Print current function name
import sys
def my_awesome_function():
    func_name = sys._getframe().f_code.co_name
    print(f"Currently executing: {func_name}")

================================================================================================
strftime
Years & Months: 
%Y (4-digit)
%y (2-digit)
%B (full name)
%b (abbr.)
%m (zero-padded)

Days & Weeks
%d (day)
%A/%a (weekday name)
%j (day of year)
%w = Weekday symbol (custom)

Time & Zone:
%H/%I (24/12h),
%M (min)
%S (sec)
%p (AM/PM)
%z (UTC offset)
%Z (timezone)

Locales:
%c (date/time)
%x (date)
%X (time)

"""


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
