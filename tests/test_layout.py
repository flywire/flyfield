import pytest
from flyfield.layout import calculate_layout_fields, assign_numeric_blocks

def make_point(page_num, bottom, x0=0, x1=10):
    return {"page_num": page_num, "bottom": bottom, "x0": x0, "x1": x1}

def test_calculate_layout_fields_groups_lines_and_blocks():
    points = [make_point(1, 100), make_point(1, 100), make_point(1, 90), make_point(2, 100)]
    page_dict = calculate_layout_fields(points)
    assert 1 in page_dict and 2 in page_dict
    for pt in page_dict[1]:
        assert "block" in pt
        assert "line" in pt

def test_assign_numeric_blocks_merges_blocks():
    rows = [
        {
            "block_length": 3,
            "pgap": None,    # first block pgap None
            "left": 0,
            "line": 1,
            "block_width": 10,
            "field_type": None,
            "block_fill": "100",
        },
        {
            "block_length": 3,
            "pgap": 4,       # small gap to trigger merging
            "left": 20,
            "line": 1,
            "block_width": 10,
            "field_type": None,
            "block_fill": "200",
        },
    ]
    page_dict = {1: rows}
    assign_numeric_blocks(page_dict)

    # The first block in merged run should have assigned a currency type
    assert page_dict[1][0].get("field_type") in ("Currency", "CurrencyDecimal")

