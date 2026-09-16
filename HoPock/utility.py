"""
Generic utilty routines
"""
import logging
logger = logging.getLogger(__name__)

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