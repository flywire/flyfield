import pytest
from flyfield.utils import colour_match, allowed_text, format_money

@pytest.mark.parametrize("color, expected", [
    ((1, 1, 1), True),          # exact
    ((0.9999, 1, 1), True),     # within tolerance
    ((0, 0, 0), False),         
    (None, False),
    ((1, 1), False),
])
def test_colour_match(color, expected):
    assert colour_match(color) is expected

@pytest.mark.parametrize("text, field_type, expected_allowed", [
    (".00", "Dollars", True),
    (".", "DollarCents", True),
    ("X", "Dollars", False),
    ("S", None, True),
    ("Unknown", None, False),
])
def test_allowed_text(text, field_type, expected_allowed):
    allowed, _ = allowed_text(text, field_type)
    assert allowed is expected_allowed

def test_format_money_groups_digits():
    assert format_money("12345", decimal=False) == "12 345"
    assert format_money("12345", decimal=True).endswith("45")
