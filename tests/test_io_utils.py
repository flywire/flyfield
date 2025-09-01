import pytest
from flyfield.io_utils import write_csv, read_csv_rows
from flyfield.extract import remove_duplicates
from flyfield.utils import allowed_text

def test_allowed_text_generic_and_specific():
    assert allowed_text("S")[0]
    assert allowed_text(".00", "Dollars")[0]
    assert not allowed_text("nope")[0]

def test_remove_duplicates_across_points():
    points = [
        {"page_num": 1, "x0": 0, "y0": 0, "x1": 10, "y1": 10},
        {"page_num": 1, "x0": 0.0001, "y0": 0, "x1": 10, "y1": 10},  # duplicate
        {"page_num": 1, "x0": 20, "y0": 20, "x1": 30, "y1": 30},
    ]
    cleaned = remove_duplicates(points)
    assert len(cleaned) == 2

def test_write_and_read_csv_roundtrip(tmp_path):
    points = [{
        "page_num": 1, "id": 1, "x0": 0, "y0": 0, "x1": 10, "y1": 10,
        "left": 0, "top": 10, "right": 10, "bottom": 0,
        "pgap": "", "gap": "",
        "line": 1, "block": 1, "block_length": 1, "block_width": 10,
        "code": "1-1-1", "field_type": "Dollars", "chars": "S"
    }]
    csv_file = tmp_path / "output.csv"
    write_csv(points, csv_file)
    rows = read_csv_rows(csv_file)
    assert len(rows) == 1
    assert rows[0]["field_type"] == "Dollars"
