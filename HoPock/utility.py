"""
Generic utilty routines
"""
import logging
logger = logging.getLogger(__name__)
from datetime import date


import ast
import re

def OLDstring_to_args(arg_str):
    """
    Should convert an input string with key value pairs to actual key value pairs
    """
    # 1. Handle empty or whitespace-only strings
    if not arg_str or not arg_str.strip():
        return {}
        
    kwargs = {}
    # Split by comma and filter out any empty chunks (e.g., trailing commas)
    pairs = [item.strip() for item in arg_str.split(",") if item.strip()]
    
    for pair in pairs:
        # Ignore items without an '=' sign
        if "=" not in pair:
            continue
            
        # 2. split("=", 1) handles spaces and preserves '=' inside values
        key, val = pair.split("=", 1)
        key = key.strip()
        val = val.strip()
        
        # 3. Try parsing numeric/boolean primitives, fall back to string
        try:
            kwargs[key] = ast.literal_eval(val)
        except (ValueError, SyntaxError):
            kwargs[key] = val
            
    return kwargs

"""
Converted the above to the below to handle commas or no commas
"""
def string_to_args(arg_str):
    """Convert whitespace- or comma-separated key/value pairs to a dict."""
    if not arg_str or not arg_str.strip():
        return {}

    pair_pattern = re.compile(
        r"(?P<key>[A-Za-z_][\w.]*)\s*=\s*"
        r"(?P<value>.*?)"
        r"(?=\s*,?\s+[A-Za-z_][\w.]*\s*=|$)"
    )
    kwargs = {}

    for match in pair_pattern.finditer(arg_str):
        key = match.group("key")
        value = match.group("value").strip().rstrip(",").strip()
        try:
            kwargs[key] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            kwargs[key] = value

    return kwargs



def header_lcr(format_string, header_date=None):
    """
    Format a header string into left, center, and right sections.

    Sections are separated by tab characters.

    Date fields:
        {d}       Day number, no leading zero
        {dd}      Day number, two digits
        {ddd}     3-letter day of week
        {dddd}    Full day of week
        {m}       Month number, no leading zero
        {mm}      Month number, two digits
        {mmm}     3-letter month
        {mmmm}    Full month name
        {yy}      2-digit year
        {yyyy}    4-digit year
        {dw}      Single-letter day:
                  Monday=M, Tuesday=T, Wednesday=W,
                  Thursday=R, Friday=F, Saturday=S, Sunday=U

    If no date is supplied, today's date is used.
    """

    if header_date is None:
        header_date = date.today()

    day_letters = {
        0: "M",  # Monday
        1: "T",  # Tuesday
        2: "W",  # Wednesday
        3: "R",  # Thursday
        4: "F",  # Friday
        5: "S",  # Saturday
        6: "U",  # Sunday
    }

    values = {
        "d": str(header_date.day),
        "dd": f"{header_date.day:02d}",
        "ddd": header_date.strftime("%a"),
        "dddd": header_date.strftime("%A"),

        "m": str(header_date.month),
        "mm": f"{header_date.month:02d}",
        "mmm": header_date.strftime("%b"),
        "mmmm": header_date.strftime("%B"),

        "yy": header_date.strftime("%y"),
        "yyyy": header_date.strftime("%Y"),

        "dw": day_letters[header_date.weekday()],
    }

    # Replace date fields.
    result = format_string

    # Longest fields first so {dddd} isn't partially
    # interpreted as {dd} + "dd", etc.
    for field in sorted(values, key=len, reverse=True):
        result = result.replace("{" + field + "}", values[field])

    # Split into header sections.
    parts = result.split("\t")

    if len(parts) == 1:
        return "", parts[0], ""

    if len(parts) == 2:
        return parts[0], parts[1], ""

    # Three or more sections: first = left,
    # second = center, everything after = right.
    return parts[0], parts[1], "\t".join(parts[2:])