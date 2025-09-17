"""Unit tests for flyfield main module argument parsing and main() function."""

import sys
from unittest.mock import patch

import pytest

from flyfield import main as flyfield_main

DEFAULT_INPUT_PDF = "input.pdf"


@pytest.mark.parametrize(
    "argv,expected_pdf,expected_pages",
    [
        (["prog"], DEFAULT_INPUT_PDF, None),
        (["prog", "--input-pdf", "test.pdf"], "test.pdf", None),
        (["prog", "--pdf-pages", "1-3,5,7"], DEFAULT_INPUT_PDF, [1, 2, 3, 5, 7]),
    ],
)
def test_parse_arguments(monkeypatch, argv, expected_pdf, expected_pages):
    """Test command-line argument parsing for input-pdf and pdf-pages."""
    monkeypatch.setattr(sys, "argv", argv)
    args = flyfield_main.parse_arguments()
    assert args.input_pdf == expected_pdf
    assert args.pdf_pages == expected_pages


@patch("flyfield.main.logger")
@patch("flyfield.main.os.path.isfile", return_value=True)
@patch("flyfield.main.load_boxes_from_csv")
@patch("flyfield.main.process_boxes")
def test_main_with_input_csv_and_no_capture(
    mock_process, mock_load_csv, mock_isfile, mock_logger, monkeypatch
):
    """Test main function behavior when input CSV provided (should load CSV, no process)."""
    mock_load_csv.return_value = {"page": []}
    mock_process.return_value = {"page": []}
    monkeypatch.setattr(
        sys, "argv", ["prog", "--input-pdf", "test.pdf", "--input-csv", "input.csv"]
    )
    flyfield_main.main()
    mock_load_csv.assert_called_once_with("input.csv")
    mock_process.assert_not_called()


@patch("flyfield.main.logger")
@patch("flyfield.main.os.path.isfile", return_value=True)
@patch("flyfield.main.process_boxes")
def test_main_without_input_csv_uses_process_boxes(
    mock_process, mock_isfile, mock_logger, monkeypatch
):
    """Test main function behavior without input CSV (should process boxes)."""
    mock_process.return_value = {"page": []}
    monkeypatch.setattr(sys, "argv", ["prog", "--input-pdf", "test.pdf"])
    flyfield_main.main()
    mock_process.assert_called_once()
