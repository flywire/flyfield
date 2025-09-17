"""
General utility functions.

Helper functions for parsing, formatting, and validation.
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from .config import COLOR_WHITE as TARGET_COLOUR


def add_suffix_to_filename(filename: str, suffix: str) -> str:
    """
    Add a suffix before the file extension in a filename.

    Args:
        filename (str): Original filename.
        suffix (str): Suffix to add.

    Returns:
        str: Filename with suffix added.
    """
    base, ext = os.path.splitext(filename)
    return f"{base}{suffix}{ext}"


def colour_match(
    color: Tuple[float, ...],
    target_color: Tuple[float, float, float] = TARGET_COLOUR,
    tol: float = 1e-3,
) -> bool:
    """
    Check if a color matches a target within a tolerance.

    Args:
        color (tuple): RGB color tuple.
        target_color (tuple): RGB target color.
        tol (float): Allowed tolerance.

    Returns:
        bool: True if colors match within tolerance.

    Note:
        If the input color has an alpha channel (RGBA), the alpha component is ignored.
    """
    if not color or len(color) < 3:
        return False
    # Compare only RGB channels; ignore alpha if present

    return all(abs(a - b) < tol for a, b in zip(color[:3], target_color))


def int_to_rgb(color_int: int) -> Tuple[float, float, float]:
    """
    Convert a 24-bit integer color in 0xRRGGBB format to normalized RGB tuple of floats.

    Args:
        color_int (int): Integer encoding color as 0xRRGGBB.

    Returns:
        tuple: Normalized (r, g, b) floats in range [0.0, 1.0].
    """
    r = ((color_int >> 16) & 0xFF) / 255
    g = ((color_int >> 8) & 0xFF) / 255
    b = (color_int & 0xFF) / 255
    return (r, g, b)


def clean_fill_string(line_text: str) -> str:
    """
    Clean a concatenated fill text string by removing single spaces while preserving double spaces as single spaces.

    Args:
        line_text (str): Raw line text.

    Returns:
        str: Cleaned fill string.
    """
    line_text = re.sub(r" {2,}", "<<<SPACE>>>", line_text)
    line_text = line_text.replace(" ", "")
    line_text = line_text.replace("<<<SPACE>>>", " ")
    return line_text


def allowed_text(
    text: str, field_type: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Determine if text is allowed based on predefined rules and field type.

    Helps to filter out pre-filled or invalid box contents.

    Args:
        text (str): Text extracted from a box.
        field_type (str or None): Optional current field type guess to refine allowed patterns.

    Returns:
        tuple: (bool indicating if allowed, detected field type or None)
    """
    allowed_text_by_type = {
        "DollarCents": {".", ".00."},
        "Dollars": {".00", ".00.00"},
    }
    generic_allowed_text = {"S", "M", "I", "T", "H"}
    if field_type in allowed_text_by_type:
        allowed_set = allowed_text_by_type[field_type] | generic_allowed_text
        if text in allowed_set:
            return True, field_type
        else:
            return False, None
    else:
        for ftype, texts in allowed_text_by_type.items():
            if text in texts:
                return True, ftype
        if text in generic_allowed_text:
            return True, None
        return False, None


def format_money_space(amount: float, decimal: bool = True) -> str:
    """
    Format a numeric amount to a string with space-separated thousands and optional decimal.

    Args:
        amount (float or int): Numeric amount to format.
        decimal (bool): Whether to include two decimal places.

    Returns:
        str: Formatted monetary string.
    """
    if decimal:
        s = f"{amount:,.2f}"
        int_part, dec_part = s.split(".")
        int_part = int_part.replace(",", " ")
        return f"{int_part} {dec_part}"
    else:
        s = f"{int(amount):,}"
        int_part = s.replace(",", " ")
        return int_part


def parse_money_space(money_str: str, decimal: bool = True) -> float:
    """
    Parse a monetary string with optional implied decimal space formatting.

    Args:
        money_str (str): Monetary string to parse (e.g., "12 345" means 123.45 if decimal is True).
        decimal (bool): Whether the last two digits represent cents (default True).

    Returns:
        float: Parsed monetary value as a float.
    """
    if decimal:
        if " " in money_str:
            parts = money_str.rsplit(" ", 1)
            int_part = parts[0].replace(" ", "")
            dec_part = parts[1]
            combined = f"{int_part}.{dec_part}"
            return float(combined)
        else:
            # No decimal part found, treat as int

            return float(money_str.replace(" ", ""))
    else:
        return int(money_str.replace(" ", ""))


def parse_implied_decimal(s: str) -> float:
    """
    Parse a numeric string with implied decimal (last two digits as decimals).

    Args:
        s (str): Numeric string (e.g., "12345" -> 123.45).

    Returns:
        float: Parsed float value.
    """
    s = s.strip()
    digits_only = re.sub(r"\D", "", s)

    if not digits_only:
        return 0.0
    if len(digits_only) <= 2:
        # If only 1 or 2 digits, treat as fractional part

        combined = f"0.{digits_only.zfill(2)}"
    else:
        combined = f"{digits_only[:-2]}.{digits_only[-2:]}"
    return float(combined)


def version() -> str:
    """
    Return the current version string of the library/module.

    Returns:
        str: Version string.
    """
    try:
        # Python 3.8+

        from importlib.metadata import PackageNotFoundError
        from importlib.metadata import version as pkg_version
    except ImportError:
        # For Python <3.8

        from importlib_metadata import PackageNotFoundError
        from importlib_metadata import version as pkg_version
    try:
        return pkg_version("flyfield")
    except PackageNotFoundError:
        return "unknown"


def parse_pages(pages_str: str) -> List[int]:
    """
    Parse a string specifying pages or page ranges into a list of page integers.

    Args:
        pages_str (str): Pages specified as a comma-separated list or ranges (e.g., "1,3-5").

    Returns:
        list[int]: List of individual page numbers.
    """
    pages = set()
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-")
            start, end = int(start_str), int(end_str)
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


def conditional_merge_list(
    main_list: List[Dict],
    ref_list: List[Dict],
    match_key: str,
    keys_to_merge: List[str],
) -> None:
    """
    Conditionally merge dictionaries in a main list with those in a reference list.

    Args:
        main_list (list[dict]): Primary list of dictionaries.
        ref_list (list[dict]): Reference list of dictionaries.
        match_key (str): Key to match dictionaries.
        keys_to_merge (list[str]): Keys to merge from ref_list into main_list.

    Returns:
        None: Modifies main_list in place.
    """
    # Build lookup dictionary for efficient matching

    ref_lookup = {item[match_key]: item for item in ref_list if match_key in item}
    for record in main_list:
        ref_record = ref_lookup.get(record.get(match_key))
        if ref_record:
            for key in keys_to_merge:
                if key in ref_record:
                    record[key] = ref_record[key]
