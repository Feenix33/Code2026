import shlex
import datetime
import re

from data_classes import PageSpec


def set_nested_attr(obj, path, value):
    # print("SETTING:", path, "=", value, "on", obj)

    parts = path.split(".")
    current = obj

    for part in parts[:-1]:
        print("  traversing:", part, "->", getattr(current, part))
        current = getattr(current, part)

    setattr(current, parts[-1], value)


def get_nested_attr(obj, path):
    current = obj
    for part in path.split("."):
        current = getattr(current, part)
    return current


def convert_value(value):
    value = value.strip()

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


def parse_attributes(text):
    attrs = {}
    tokens = shlex.split(text)

    for token in tokens:
        if "=" not in token:
            continue

        key, value = token.split("=", 1)
        attrs[key] = convert_value(value)
    return attrs


def read_page_specs(filename):
    specs = []

    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    line_number = 0

    while line_number < len(lines):
        raw_line = lines[line_number]
        line = raw_line.strip()
        line_number += 1

        if not line:
            continue

        if line.startswith("#"):
            continue

        spec_start_line = line_number

        if line.endswith("{"):
            page_type = line[:-1].strip()
            attrs = {}

            while line_number < len(lines):
                block_line = lines[line_number].strip()
                line_number += 1
                if block_line == "}":
                    break

                if not block_line:
                    continue

                if block_line.startswith("#"):
                    continue

                attrs.update(parse_attributes(block_line))
        else:
            parts = shlex.split(line)
            page_type = parts[0]
            attrs_text = line[len(page_type):]
            attrs = parse_attributes(attrs_text)

        specs.append(PageSpec(page_type=page_type, attrs=attrs, line_number=spec_start_line))

    return specs


def build_book(book, specs, page_factory):
    for spec in specs:
        if spec.page_type == "book":
            for key, value in spec.attrs.items():
                try:
                    set_nested_attr(book.config, key, value)
                except AttributeError:
                    print(f"WARNING line {spec.line_number}: unknown book setting '{key}'")
            continue

        if spec.page_type == "defaults":
            for key, value in spec.attrs.items():
                try:
                    set_nested_attr(book.style, key, value)
                except AttributeError:
                    print(f"WARNING line {spec.line_number}: unknown style attribute '{key}'")
            continue

        # print(f"Creating page of type '{spec.page_type}' with attributes {spec.attrs}")
        page = page_factory.create(spec.page_type, **spec.attrs)
        if page is None:
            print(f"WARNING line {spec.line_number}: unknown page type '{spec.page_type}'")
            continue

        page.overrides = spec.attrs
        book.add_page(page)

def parse_date_value(val):
    """Parse a date-like value into a datetime.date.

    Accepts datetime.date, datetime.datetime, or a string in a variety
    of common formats. Raises ValueError if parsing fails.
    """
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
        return val
    if isinstance(val, datetime.datetime):
        return val.date()
    if isinstance(val, str):
        s = val.strip()
        # Normalize common trailing punctuation
        s = s.strip().rstrip('.,')
        # Handle m/d, m/d/yy, mm/dd/yy, mm/dd/yyyy and variants where year is optional
        # Accept any non-digit separator (/, -, ., space)
        mmdy = re.match(r'^(?P<m>\d{1,2})\D+(?P<d>\d{1,2})(?:\D+(?P<y>\d{2,4}))?$', s)
        if mmdy:
            mm = int(mmdy.group('m'))
            dd = int(mmdy.group('d'))
            ygrp = mmdy.group('y')
            if ygrp is None or ygrp == '':
                year = datetime.date.today().year
            else:
                if len(ygrp) == 2:
                    year = 2000 + int(ygrp)
                else:
                    year = int(ygrp)
            try:
                return datetime.date(year, mm, dd)
            except Exception:
                # fall through to other parsing attempts
                pass

        # Try ISO format first
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            pass

        # Try a list of common formats
        fmts = [
            '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
            '%m-%d-%Y', '%m/%d/%Y', '%b %d %Y', '%b %d, %Y',
            '%B %d %Y', '%B %d, %Y', '%b%d%Y', '%d %b %Y', '%d %B %Y'
        ]
        for fmt in fmts:
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except Exception:
                continue

        # YYYYMMDD
        m = re.match(r'^(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2})$', s)
        if m:
            return datetime.date(int(m.group('y')), int(m.group('m')), int(m.group('d')))

        # Try python-dateutil if available for more fuzzy parsing
        try:
            from dateutil import parser as _parser
            return _parser.parse(s).date()
        except Exception:
            pass

    raise ValueError(f"Unrecognized date format: {val}")


def buildThreePart(formatStr="\t%d%b%y\t", titleStr=None, date=None):
    """Build a date header with left, center, and right fields.

    Args:
        formatStr: the format string (tabs split left/center/right). May
            include a custom token '%s' which will be replaced with
            `titleStr`.
        titleStr: optional title string to substitute for '%s'.
        date: optional date (datetime.date, datetime.datetime, or string).
            If None, today's date is used.

    Returns:
        Tuple of (left, center, right) strings.
    """
    # If date not provided, default to today
    if date is None:
        date = datetime.date.today()

    if isinstance(date, str):
        try:
            date = parse_date_value(date)
        except Exception:
            date = datetime.datetime.fromisoformat(date).date()
    elif isinstance(date, datetime.datetime):
        date = date.date()
    elif not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date, datetime.datetime, or ISO date string")

    # Accept literal backslash-t escapes from config files as actual tab separators.
    formatStr = formatStr.replace('\\t', '\t')
    parts = formatStr.split('\t')
    parts += [''] * (3 - len(parts))
    left_fmt, center_fmt, right_fmt = parts[:3]

    # Support an additional custom token for a single-letter weekday ('%w')
    # and a title insertion token '%s'. Replace '%s' with a placeholder so
    # strftime doesn't try to interpret title contents.
    def _format_part(fmt):
        if not fmt:
            return ''

        dow_placeholder = '__DOW_LETTER__'
        title_placeholder = '__TITLE_PLACEHOLDER__'
        replaced_dow = False

        fmt_for_strftime = fmt

        if '%w' in fmt_for_strftime:
            fmt_for_strftime = fmt_for_strftime.replace('%w', dow_placeholder)
            replaced_dow = True

        if '%s' in fmt_for_strftime:
            fmt_for_strftime = fmt_for_strftime.replace('%s', title_placeholder)

        # Use strftime for the rest of the formatting
        result = date.strftime(fmt_for_strftime)

        # Substitute single-letter weekday if requested
        if replaced_dow:
            dow_map = {0: 'M', 1: 'T', 2: 'W', 3: 'R', 4: 'F', 5: 'S', 6: 'U'}
            letter = dow_map.get(date.weekday(), '?')
            result = result.replace(dow_placeholder, letter)

        # Substitute title placeholder with provided title (or empty string)
        if title_placeholder in result:
            sub = '' if titleStr is None else str(titleStr)
            result = result.replace(title_placeholder, sub)

        return result

    left = _format_part(left_fmt)
    center = _format_part(center_fmt)
    right = _format_part(right_fmt)

    return left, center, right


if __name__ == '__main__':
   
    print ("TESTING buildThreePart")   
    def TESTbuildThreePart(formatStr=None, titleStr=None, date=None):
        left, center, right = buildThreePart(formatStr, titleStr, date)
        print(f"Left: '{left}', Center: '{center}', Right: '{right}'")

    TESTbuildThreePart(
        formatStr="\t%d%b%y\t",
        titleStr="Test Title",
        date="2023-10-01"
    )
    TESTbuildThreePart(formatStr="\t%s",titleStr= "Test Two")
    TESTbuildThreePart(formatStr="%d %w\t%s\t%b", titleStr="Test Three")
    TESTbuildThreePart(formatStr="%s %y\t\t\t\t", titleStr="Test Four")
