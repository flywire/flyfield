import pytest
from flyfield.markup_and_fields import adjust_form_boxes

@pytest.mark.parametrize("row,width,block_length,expected_width", [
    ({"left": 10, "field_type": "Dollars"}, 50, 1, 29),
    ({"left": 10, "field_type": "DollarCents"}, 50, 1, 46),
    ({"left": 10, "field_type": "Currency"}, 50, 3, None),
    ({"left": 10, "field_type": None}, 50, 1, 50),
])
def test_adjust_form_boxes(row, width, block_length, expected_width):
    _, width_adj, _ = adjust_form_boxes(row, width, block_length)
    if expected_width is not None:
        assert width_adj == expected_width
    else:
        assert width_adj >= width
