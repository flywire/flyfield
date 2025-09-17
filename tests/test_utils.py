"""Tests for utility functions in flyfield."""

import pytest

from flyfield.utils import (
    add_suffix_to_filename,
    allowed_text,
    clean_fill_string,
    colour_match,
    conditional_merge_list,
    format_money_space,
    int_to_rgb,
    parse_implied_decimal,
    parse_money_space,
    parse_pages,
    version,
)


@pytest.mark.parametrize(
    "filename,suffix,expected",
    [
        ("file.txt", "_v2", "file_v2.txt"),
        ("archive.tar.gz", "_old", "archive.tar_old.gz"),
        ("noext", "_suffix", "noext_suffix"),
        ("a.b.c.d", "_x", "a.b.c_x.d"),
    ],
)
def test_add_suffix_to_filename(filename, suffix, expected):
    """Test adding suffixes to filename before extension."""
    assert add_suffix_to_filename(filename, suffix) == expected


@pytest.mark.parametrize(
    "color,target,tol,expected",
    [
        ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0), 1e-3, True),
        ((1.0, 1.0, 1.0 - 1e-4), (1.0, 1.0, 1.0), 1e-3, True),
        ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 1e-3, False),
        ((1.0, 1.0, 1.0, 0.5), (1.0, 1.0, 1.0), 1e-3, True),
        ((0.5,), (1.0, 1.0, 1.0), 1e-3, False),
        (None, (1.0, 1.0, 1.0), 1e-3, False),
    ],
)
def test_colour_match(color, target, tol, expected):
    """Test color matching with tolerance."""
    assert colour_match(color, target_color=target, tol=tol) is expected


@pytest.mark.parametrize(
    "color_int,expected",
    [
        (0xFF0000, (1.0, 0.0, 0.0)),
        (0x00FF00, (0.0, 1.0, 0.0)),
        (0x0000FF, (0.0, 0.0, 1.0)),
        (0x123456, (0x12 / 255, 0x34 / 255, 0x56 / 255)),
    ],
)
def test_int_to_rgb(color_int, expected):
    """Test integer to RGB tuple conversion."""
    assert int_to_rgb(color_int) == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("a b  c   d", "ab c d"),
        (" a  b ", "a b"),
        ("  ", " "),
        ("hello  world  ", "hello world "),
    ],
)
def test_clean_fill_string(input_text, expected):
    """Test cleaning fill strings by removing excess spaces."""
    assert clean_fill_string(input_text) == expected


@pytest.mark.parametrize(
    "text,field_type,expected_allowed,expected_type",
    [
        (".", "DollarCents", True, "DollarCents"),
        (".00.", "DollarCents", True, "DollarCents"),
        (".00", "Dollars", True, "Dollars"),
        (".00.00", "Dollars", True, "Dollars"),
        ("S", "DollarCents", True, "DollarCents"),
        ("M", None, True, None),
        (".00", None, True, "Dollars"),
        ("X", None, False, None),
        ("T", None, True, None),
    ],
)
def test_allowed_text(text, field_type, expected_allowed, expected_type):
    """Test allowed_text behavior for various inputs and field types."""
    assert allowed_text(text, field_type) == (expected_allowed, expected_type)


@pytest.mark.parametrize(
    "amount,with_decimals,expected",
    [
        (1234.56, True, "1 234 56"),
        (1234, False, "1 234"),
        (0, True, "0 00"),
        (0, False, "0"),
        (1234567.89, True, "1 234 567 89"),
    ],
)
def test_format_money_space(amount, with_decimals, expected):
    """Test formatting money amounts with spaced digits."""
    assert format_money_space(amount, with_decimals) == expected


@pytest.mark.parametrize(
    "money_str,with_decimals,expected",
    [
        ("1 234 56", True, 1234.56),
        ("1 234", False, 1234),
        ("123 456 78", True, 123456.78),
        ("0", False, 0),
        ("0 00", True, 0.00),
    ],
)
def test_parse_money_space(money_str, with_decimals, expected):
    """Test parsing spaced money strings into floats or ints."""
    result = parse_money_space(money_str, with_decimals)
    if with_decimals:
        assert abs(result - expected) < 1e-6
    else:
        assert result == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("706935", 7069.35),
        ("35", 0.35),
        ("0", 0.0),
        ("", 0.0),
        ("abc12345", 123.45),
    ],
)
def test_parse_implied_decimal(input_str, expected):
    """Test parsing implied decimal numeric strings into float values."""
    assert abs(parse_implied_decimal(input_str) - expected) < 1e-6


def test_version_returns_string():
    """Test version function returns a non-empty string."""
    v = version()
    assert isinstance(v, str)
    assert len(v) > 0


@pytest.mark.parametrize(
    "pages_str,expected",
    [
        ("1,3,5-7", [1, 3, 5, 6, 7]),
        ("10, 12-14, 16", [10, 12, 13, 14, 16]),
        ("2-2", [2]),
        ("7", [7]),
        ("1,2,3", [1, 2, 3]),
        ("1-3,4-6", [1, 2, 3, 4, 5, 6]),
    ],
)
def test_parse_pages(pages_str, expected):
    """Test parsing page number ranges from strings."""
    assert parse_pages(pages_str) == expected


def test_conditional_merge_list():
    """Test conditional merging of list elements based on a key."""
    data = [{"code": "A", "value": 1}, {"code": "B", "value": 2}]
    boxes = [{"code": "A", "field_type": "ID"}, {"code": "B", "field_type": "ID"}]
    conditional_merge_list(data, boxes, "code", ["field_type"])
    assert all("field_type" in d and d["field_type"] == "ID" for d in data)
