"""Test extract utility functions."""

from flyfield.extract import remove_duplicates, sort_boxes


def make_box(page_num=1, x0=0, y0=0, x1=10, y1=10, bottom=10, left=0):
    """Helper to create a box dictionary with specified coordinates."""
    return {
        "page_num": page_num,
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "bottom": bottom,
        "left": left,
    }


def test_remove_duplicates_removes_close_points():
    """Test removal of points close enough to be considered duplicates."""
    boxes = [
        make_box(),
        make_box(x0=0.0001),  # Near-duplicate of first box
        make_box(x0=20),
    ]
    cleaned = remove_duplicates(boxes)
    assert len(cleaned) == 2
    assert any(abs(b["x0"]) < 1e-5 for b in cleaned)


def test_sort_boxes_orders_by_page_and_position():
    """Test sorting of boxes by page number, then bottom position, then left coordinate."""
    boxes = [
        make_box(page_num=1, bottom=100, left=10),
        make_box(page_num=1, bottom=100, left=5),
        make_box(page_num=2, bottom=150, left=-1),
    ]
    sorted_boxes = sort_boxes(boxes)
    assert sorted_boxes[0]["page_num"] == 1
    assert sorted_boxes[-1]["page_num"] == 2
    assert sorted_boxes[0]["left"] == 5
    assert sorted_boxes[1]["left"] == 10
