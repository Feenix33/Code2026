"""
Predefined booklets
"""
import logging
from datetime import date, timedelta

def parse_start_date(value):
    if value == "today":
        return date.today()

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"Invalid date '{value}'. "
            "Use YYYY-MM-DD, for example 2026-10-05."
        )


def build_weekly_definition(start_date):
    lines = [
        "cover titletext='Weekly Planner'",
        f"weekly day={start_date.isoformat()}",
        "list titletext='To Do'",
        "list titletext='Stuff'",
        "lines",
        "lines"
    ]

    return lines

def build_file_definition(filename):
    lines = [
        f"text file={filename}"
    ]
    return lines


def build_daily_definition(start_date):
    lines = []

    # Replace these illustrative entries with your actual
    # registered cover and daily page types/options.
    lines.append(f"cover titletext='Daily Planner'") #={start_date.isoformat()}")

    for offset in range(7):
        page_date = start_date + timedelta(days=offset)
        lines.append(f"daily day={page_date.isoformat()}")

    return lines

def build_manual_definition():
    lines = [
        'cover titletext="Pocket Printer"',
        'text {titletext="Page Types"',  
        '   cover A simple cover',
        '   text Read a text file',
        '   list A list that can be prefiled',
        '}',
        'text {titletext="text"',
        '"titletext=<string> Title of the page"',
        '"file=<filename> Get input from this file"',
        '}'
    ]
    return lines

