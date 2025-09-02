import pytest
from flyfield.extract import remove_duplicates, sort_boxes

def test_remove_duplicates_collapses_similar_boxes():
    points = [
        {"page_num": 1, "x0": 0, "y0": 0, "x1": 10, "y1": 10},
        {"page_num": 1, "x0": 0.0001, "y0": 0, "x1": 10, "y1": 10},  # duplicate
    ]
    cleaned = remove_duplicates(points)
    assert len(cleaned) == 1

def test_sort_boxes_orders_correctly():
    points = [
        {"page_num": 1, "bottom": 100, "left": 10},
        {"page_num": 1, "bottom": 100, "left": 5},
        {"page_num": 1, "bottom": 200, "left": 0},
    ]
    sorted_pts = sort_boxes(points)
    # highest bottom first, then by left
    assert sorted_pts[0]["bottom"] == 200
    assert sorted_pts[1]["left"] == 5
