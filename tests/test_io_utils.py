"""Tests for flyfield utility functions."""

import pytest

from flyfield.extract import remove_duplicates
from flyfield.io_utils import (
    read_csv_rows,
    write_csv,
)
from flyfield.utils import allowed_text


def test_allowed_text_generic_and_specific():
    """Test allowed_text with generic and specific input strings."""
    assert allowed_text("S")[0]
    assert allowed_text(".00", "Dollars")[0]
    assert not allowed_text("nope")[0]


def test_remove_duplicates_across_points():
    """Test remove_duplicates removes points close to duplicates correctly."""
    points = [
        {"page_num": 1, "x0": 0, "y0": 0, "x1": 10, "y1": 10},
        {
            "page_num": 1,
            "x0": 0.0001,
            "y0": 0,
            "x1": 10,
            "y1": 10,
        },  # should be duplicate
        {"page_num": 1, "x0": 20, "y0": 20, "x1": 30, "y1": 30},
    ]
    cleaned = remove_duplicates(points)
    assert len(cleaned) == 2
    assert any(abs(p["x0"] - 0) < 1e-5 for p in cleaned)


def test_write_and_read_csv_roundtrip(tmp_path):
    """Test writing points to CSV and reading them back preserves data."""
    points = [
        {
            "page_num": 1,
            "id": 1,
            "x0": 0,
            "y0": 0,
            "x1": 10,
            "y1": 10,
            "left": 0,
            "top": 10,
            "right": 10,
            "bottom": 0,
            "pgap": "",
            "gap": "",
            "line": 1,
            "block": 1,
            "block_length": 1,
            "block_width": 10,
            "code": "1-1-1",
            "field_type": "Dollars",
            "chars": "S",
            "block_fill": "1 234 56",
        }
    ]
    csv_file = tmp_path / "test.csv"
    write_csv(points, csv_file)
    rows = read_csv_rows(csv_file)
    assert len(rows) == 1
    row = rows[0]
    assert row["field_type"] == "Dollars"
    assert "block_fill" in row
    assert isinstance(row["block_fill"], str)
    assert " " in row["block_fill"]


def test_write_csv_handles_missing_block_fill(tmp_path):
    """Test CSV writing handles missing block_fill field correctly."""
    points = [
        {
            "page_num": 1,
            "id": 2,
            "x0": 5,
            "y0": 5,
            "x1": 15,
            "y1": 20,
            "left": 5,
            "top": 20,
            "right": 15,
            "bottom": 5,
            "pgap": "",
            "gap": "",
            "line": 2,
            "block": 2,
            "block_length": 1,
            "block_width": 10,
            "code": "2-2-2",
            "field_type": "DollarCents",
            "chars": "M",
            "fill": "1 234 56",
        }
    ]
    csv_file = tmp_path / "test2.csv"
    write_csv(points, csv_file)
    rows = read_csv_rows(csv_file)
    assert len(rows) == 1
    row = rows[0]
    assert row["field_type"] == "DollarCents"
    assert "block_fill" in row
    assert row["block_fill"].endswith("56")


def test_read_csv_rows_skips_bad_numeric_rows(tmp_path):
    """Test read_csv_rows skips rows with invalid numeric fields."""
    CSV_HEADER = [
        "page_num",
        "id",
        "x0",
        "y0",
        "x1",
        "y1",
        "left",
        "top",
        "right",
        "bottom",
        "height",
        "width",
        "pgap",
        "gap",
        "line",
        "block",
        "block_length",
        "block_width",
        "code",
        "field_type",
        "chars",
        "fill",
    ]
    lines = [
        ",".join(CSV_HEADER),
        "abc,1,0,0,10,10,0,10,10,0,10,10,,,1,1,1,10,1-1-1,Dollars,S,1 234 56",  # 'abc' invalid page_num
    ]
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("\n".join(lines), encoding="utf-8")
    rows = read_csv_rows(bad_csv)
    assert len(rows) == 0  # bad row skipped


@pytest.mark.parametrize(
    "text,field_type,expected",
    [
        ("S", None, True),
        (".00", "Dollars", True),
        ("nope", None, False),
    ],
)
def test_allowed_text_param(text, field_type, expected):
    """Parametrized test for allowed_text with various inputs."""
    allowed, _ = allowed_text(text, field_type)
    assert allowed is expected
