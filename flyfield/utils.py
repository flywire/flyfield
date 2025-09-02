import pathlib
import os
import re
from .config import COLOR_WHITE as TARGET_COLOUR, COLOR_BLACK

def add_suffix_to_filename(filename, suffix):
    """
    Add a suffix before the file extension in a filename.
    """
    base, ext = os.path.splitext(filename)
    return f"{base}{suffix}{ext}"

def colour_match(color, target_color=TARGET_COLOUR, tol=1e-3):
    """
    Check if an input RGB or RGBA color matches the target color within a tolerance.
    
    Args:
        color (tuple): Color tuple expected as normalized RGB or RGBA (values in range [0.0, 1.0]).
        target_color (tuple): Target RGB tuple (normalized floats) to match against.
        tol (float): Tolerance for color difference on each channel.
    
    Returns:
        bool: True if the color matches the target within tolerance, otherwise False.
    
    Note:
        If the input color has an alpha channel (RGBA), the alpha component is ignored.
    """
    if not color or len(color) < 3:
        return False
    # Compare only RGB channels; ignore alpha if present
    return all(abs(a - b) < tol for a, b in zip(color[:3], target_color))

def int_to_rgb(color_int):
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

def clean_fill_string(line_text):
    """
    Clean a concatenated fill text string by removing single spaces while preserving double spaces as single spaces.

    Args:
        line_text (str): Raw concatenated text containing spaces.

    Returns:
        str: Cleaned string with double spaces replaced by single spaces and single spaces removed.
    """
    line_text = re.sub(r" {2,}", "<<<SPACE>>>", line_text)
    line_text = line_text.replace(" ", "")
    line_text = line_text.replace("<<<SPACE>>>", " ")
    return line_text

def allowed_text(text, field_type=None):
    """
    Determine whether a text string is allowed inside a box based on predefined allowed patterns.
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

def format_money(s, decimal=True):
    """Format numeric string as currency with spaces; optional decimals.

    Args:
        s (str): Numeric string (non-digits removed internally).
        decimal (bool): If True, last two digits are decimal part. Defaults to True.

    Returns:
        str: Formatted currency string with space separators.
    """
    digits_only = re.sub(r"\D", "", s)

    def group_thousands(num_str):
        # Group digits in reverse order by threes, then join in correct order
        groups = []
        while num_str:
            groups.append(num_str[-3:])
            num_str = num_str[:-3]
        return " ".join(reversed(groups))

    if decimal:
        return re.sub(
            r"^0*(\d+)?(\d{2})$",
            lambda m: (
                (group_thousands(m.group(1)) + " " if m.group(1) else "") + m.group(2)
            ),
            digits_only,
        )
    else:
        digits_only = digits_only.lstrip("0") or "0"
        return group_thousands(digits_only)

def version():
    """
    Get installed package version using importlib.metadata.
    
    Returns:
        str: Version string, or 'unknown' if not found.
    """
    try:
        # Python 3.8+
        from importlib.metadata import version as pkg_version, PackageNotFoundError
    except ImportError:
        # For Python <3.8
        from importlib_metadata import version as pkg_version, PackageNotFoundError

    try:
        return pkg_version("flyfield")
    except PackageNotFoundError:
        return "unknown"

def parse_pages(pages_str):
    """
    Parse a string of page numbers and ranges into a sorted list of integers.

    Example: "1,3,5-7" → [1, 3, 5, 6, 7]

    Args:
        pages_str (str): Comma-separated pages and ranges.

    Returns:
        list[int]: Sorted list of page numbers.
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
