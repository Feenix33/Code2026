"""
Generic utilty routines
"""
from datetime import datetime, date, timedelta
import ast
import re

import logging
logger = logging.getLogger(__name__)

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



def header_lcr(format_string="\t{dd}{mmm}", header_date=None):
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

    format_string = format_string.replace(r"\t", "\t")

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

def parse_mystery_date_string(date_str: str) -> date:
    """
    Converts a date string in various formats into a datetime.date object.
    Supported formats:
    - yyyy-mm-dd
    - mm/dd
    - mm/dd/yyyy
    - dd-mmm-yy
    - dd-mmm-yyyy
    - mm-dd-yyyy
    """
    # Define standard format codes matching the requirements
    formats = [
        "%Y-%m-%d",  # yyyy-mm-dd
        "%m/%d",     # mm/dd (defaults to current year)
        "%m/%d/%Y",  # mm/dd/yyyy
        "%d-%b-%y",  # dd-mmm-yy (e.g., 25-Sep-26)
        "%d-%b-%Y",  # dd-mmm-yyyy (e.g., 25-Sep-2026)
        "%m-%d-%Y",  # mm-dd-yyyy
        "%d%b"       # dd-mmm (25Sep)
    ]
    
    for fmt in formats:
        try:
            # Attempt to parse and immediately extract the date component
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
            
    raise ValueError(f"Date string '{date_str}' does not match any expected formats.")

# --- Quick Usage Examples ---
# print(parse_date_string("2026-09-25"))  # Output: 2026-09-25
# print(parse_date_string("25-Sep-26"))   # Output: 2026-09-25
# print(parse_date_string("09/25"))       # Output: 2026-09-25


def get_monday(input_date: date = None) -> date:
    # If no date is provided, default to today's date
    if input_date is None:
        input_date = date.today()
        
    # .weekday() returns 0 for Monday, 1 for Tuesday, ..., 6 for Sunday
    # Subtracting the weekday value always points back to that week's Monday
    return input_date - timedelta(days=input_date.weekday())

def flip_format_string(text: str) -> str:
    """
    For a title format string that separates left, center, and right by tabs, this routine 
    flips the string so it is right center left
    """
    # 1. Standardize literal "\t" into actual tab characters
    normalized = text.replace(r"\t", "\t")
    parts = normalized.split("\t")
    
    # 2. Pad the list to guarantee exactly 3 sections [left, center, right]
    while len(parts) < 3:
        parts.append("")
        
    # 3. Flip the left (index 0) and right (index 2) sections
    parts[0], parts[2] = parts[2], parts[0]
    
    # 4. Remove trailing empty sections to eliminate trailing tabs
    while parts and parts[-1] == "":
        parts.pop()
        
    # 5. Rejoin and return using a standard tab character
    return "\t".join(parts)




def clean_recipe_strings(strings_list):
    """
    Takes a list of strings and replaces unprintable characters and common abbreviations

    Usage:
    cleaned_data = clean_recipe_strings(raw_data)
    for original, cleaned in zip(raw_data, cleaned_data):
    """
    # 1. Unicode Fraction & Symbol Replacements
    # Matches anywhere in the text, converting fractions and removing degree symbols.
    # Mixed forms like "1½" must become "1 1/2" rather than "11/2".
    literal_replacements = {
        "½": "1/2",
        "¼": "1/4",
        "¾": "3/4",
        "⅓": "1/3",
        "⅔": "2/3",
        "°": ""
    }
    
    # 2. Measurement Unit Mappings to standard abbreviations
    # Grouped logically by their destination abbreviation
    unit_mappings = {
        "c": [r"cups?", r"c\."],
        "tsp": [r"teaspoons?", r"tsp\.?", r"t\."],
        "tbsp": [r"tablespoons?", r"tbsp\.?", r"tbs\.?", r"tblsp\.?", r"T\."],
        "oz": [r"ounces?", r"oz\."],
        "lb": [r"pounds?", r"lbs?\.?"],
        "g": [r"grams?", r"g\."],
        "kg": [r"kilograms?", r"kg\."]
    }
    
    # 3. Compile Patterns
    # We dynamically build regex to catch unit-only words OR digit-unit pairs with any spacing
    measurement_patterns = []
    for abbrev, variations in unit_mappings.items():
        # Joins variations, e.g., (?:cups?|c\.)
        variations_pattern = f"(?:{'|'.join(variations)})"
        
        # Pattern A: Standardize a numeric amount and the abbreviated unit with a space,
        # e.g. "1/2 tsp" or "2 cups" -> "1/2 tsp" / "2 c".
        # The unit is kept as a separate token so we do not collapse "1/2tsp".
        measurement_patterns.append((
            re.compile(r'(\d+(?:\/\d+)?)\s*' + variations_pattern + r'\b', re.IGNORECASE),
            rf'\1 {abbrev}'
        ))
        
        # Pattern B: Clean up standalone instances keeping word boundaries -> "Add cups" to "Add c"
        # Restricts matching inside words like "buttercup"
        measurement_patterns.append((
            re.compile(r'\b' + variations_pattern + r'\b', re.IGNORECASE),
            abbrev
        ))

    processed_strings = []
    
    for text in strings_list:
        # Step A: Handle mixed whole-plus-fraction values before the generic replacement.
        # "1½" should become "1 1/2", not "11/2".
        for target, replacement in literal_replacements.items():
            if target in {"½", "¼", "¾", "⅓", "⅔"}:
                pattern = re.compile(rf'(?<=\d){re.escape(target)}')
                text = pattern.sub(f" {replacement}", text)

        # Step B: Apply literal character mappings elsewhere
        for target, replacement in literal_replacements.items():
            pattern = re.compile(re.escape(target), re.IGNORECASE)
            text = pattern.sub(replacement, text)

        # Step C: Normalize numeric amounts and unit spacing without collapsing the unit
        # onto the numeric value, e.g. "1/2tsp" -> "1/2 tsp".
        for pattern, replacement in measurement_patterns:
            text = pattern.sub(replacement, text)

        processed_strings.append(text)
        
    return processed_strings

