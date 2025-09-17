"""
Utility functions for input/output operations.

Includes CSV reading/writing and data transformation helpers.
"""

import csv
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Union

from PyPDFForm import PdfWrapper

from .config import NUMERIC_FIELD_TYPES
from .utils import (
    conditional_merge_list,
    format_money_space,
    parse_implied_decimal,
    parse_money_space,
)

logger = logging.getLogger(__name__)

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

COLUMN_TYPES = {
    "page_num": int,
    "id": int,
    "x0": float,
    "y0": float,
    "x1": float,
    "y1": float,
    "left": float,
    "top": float,
    "right": float,
    "bottom": float,
    "height": float,
    "width": float,
    "pgap": float,
    "gap": float,
    "line": int,
    "block": int,
    "block_length": int,
    "block_width": float,
    "code": str,
    "field_type": str,
    "chars": str,
    "fill": str,
}


def load_boxes_from_csv(csv_path: str) -> dict[int, list[dict]]:
    """
    Load boxes data from a CSV into a dictionary keyed by page number,

    applying the specified types to each column in the CSV.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        dict[int, list[dict]]: Dictionary mapping page number (int)
        to a list of box dictionaries with appropriately typed values.

    Description:
        The CSV is expected to contain columns:

        - page_num (int), id (int), x0 (float), y0 (float), x1 (float), y1 (float),
        - left (float), top (float), right (float), bottom (float),
        - height (float), width (float), pgap (float), gap (float),
        - line (int), block (int), block_length (int), block_width (float),
        - code (str), field_type (str), chars (str), fill (str)

        Each value from the CSV is converted from string to the appropriate type.
        Empty or missing values are converted to None for numeric types and empty string for strings.
        Conversion errors are caught and logged; original strings are kept in those cases.
    """
    logger.info(f"Reading blocks from CSV: {csv_path}")
    rows = read_csv_rows(csv_path)  # Should return list of dict[str, str]

    def convert_value(value: str, to_type):
        if value is None or value == "":
            if to_type in (int, float):
                return None
            return ""
        try:
            return to_type(value)
        except Exception as e:
            logger.warning(f"Failed to convert value '{value}' to {to_type}: {e}")
            return value  # fallback: keep original string

    page_dict = defaultdict(list)
    for row in rows:
        typed_row = {
            col: convert_value(row.get(col), col_type)
            for col, col_type in COLUMN_TYPES.items()
        }
        if typed_row.get("page_num") is not None:
            page_dict[typed_row["page_num"]].append(typed_row)
    return page_dict


def write_csv(
    boxes_or_page_dict: Union[List[Dict], Dict[int, List[Dict]]], csv_path: str
) -> None:
    """
    Write box data or page dictionary data to CSV file.

    Saves only one 'fill' column:
        - Uses 'block_fill' if present,
        - Otherwise falls back to original 'fill'.

    Args:
        boxes_or_page_dict (list or dict): List of box dicts or dict keyed by page containing lists of boxes.
        csv_path (str): Output CSV file path.
    """
    if isinstance(boxes_or_page_dict, dict):
        all_boxes = [
            box
            for boxes in boxes_or_page_dict.values()
            if boxes is not None
            for box in boxes
        ]
    else:
        all_boxes = boxes_or_page_dict or []
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            for box in all_boxes:
                height = round(box.get("y1", 0) - box.get("y0", 0), 1)
                width = round(box.get("x1", 0) - box.get("x0", 0), 1)
                fill_value = box.get("block_fill")
                if fill_value is None:
                    fill_value = box.get("fill", "")
                field_type = box.get("field_type")
                # Convert monetary fill values back to float/int as appropriate

                if (
                    field_type in ("Dollars", "DollarCents", "CurrencyDecimal")
                    and fill_value
                ):
                    decimal = field_type in ("DollarCents", "CurrencyDecimal")
                    try:
                        fill_value = parse_money_space(fill_value, decimal=decimal)
                    except Exception as e:
                        logger.warning(
                            f"Failed to parse money from fill_value '{fill_value}' for field_type '{field_type}': {e}"
                        )
                row = [
                    box.get("page_num", ""),
                    box.get("id", ""),
                    box.get("x0", ""),
                    box.get("y0", ""),
                    box.get("x1", ""),
                    box.get("y1", ""),
                    box.get("left", ""),
                    box.get("top", ""),
                    box.get("right", ""),
                    box.get("bottom", ""),
                    height,
                    width,
                    box.get("pgap", ""),
                    box.get("gap", ""),
                    box.get("line", ""),
                    box.get("block", ""),
                    box.get("block_length", ""),
                    box.get("block_width", ""),
                    box.get("code", ""),
                    box.get("field_type", ""),
                    box.get("chars", ""),
                    fill_value,
                ]

                writer.writerow(row)
    except Exception as e:
        logger.error(f"Failed to write CSV {csv_path}: {e}")


def read_csv_rows(filename: str) -> List[Dict[str, str]]:
    """
    Read CSV rows into a list, converting typed fields and normalizing monetary fills.

    Args:
        filename (str): Path to CSV file.

    Returns:
        list of dict: Rows with typed values and block_fill normalized.
    """
    rows = []
    currency_field_types = {"Dollars", "DollarCents", "Currency", "CurrencyDecimal"}

    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            is_extraction_csv = "page_num" in headers

            for row in reader:
                if is_extraction_csv:
                    try:
                        # Convert page_num, line, gap, block_length, height, width fields to correct types

                        row["page_num"] = (
                            int(row["page_num"]) if row["page_num"].strip() else None
                        )
                        row["line"] = int(row["line"]) if row["line"].strip() else None
                        row["gap"] = float(row["gap"]) if row["gap"].strip() else 0.0
                        row["block_length"] = (
                            int(row["block_length"])
                            if row["block_length"].strip()
                            else 0
                        )
                        row["height"] = float(row.get("height", 0))
                        row["width"] = float(row.get("width", 0))
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping row due to value error: {e}")
                        continue
                # Rearrange 'fill' to 'block_fill' with formatted monetary fields

                if "fill" in row:
                    fill_value = row["fill"]
                    field_type = row.get("field_type", "")

                    if field_type in currency_field_types and fill_value.strip():
                        if (
                            field_type in ("DollarCents", "CurrencyDecimal")
                            and " " not in fill_value
                        ):
                            # Use implied decimal parser for no explicit decimal separator

                            try:
                                amount = parse_implied_decimal(fill_value)
                                fill_value = format_money_space(amount, decimal=True)
                            except Exception as e:
                                logger.warning(
                                    f"Failed to parse implied decimal fill '{fill_value}' for field_type '{field_type}': {e}"
                                )
                        else:
                            # Use existing parser for explicit decimal formatting

                            decimal = field_type in ("DollarCents", "CurrencyDecimal")
                            try:
                                amount = parse_money_space(fill_value, decimal=decimal)
                                fill_value = format_money_space(amount, decimal=decimal)
                            except Exception as e:
                                logger.warning(
                                    f"Failed to parse/format fill '{fill_value}' for field_type '{field_type}': {e}"
                                )
                        row["block_fill"] = fill_value
                        del row["fill"]
                rows.append(row)
    except Exception as e:
        logger.error(f"Failed to read CSV rows from {filename}: {e}")
    return rows


def save_pdf_form_data_to_csv(
    pdf_path: str, csv_path: str, boxes: Optional[Dict[int, List[dict]]] = None
) -> None:
    """
    Extract PDF form data, convert string values to uppercase and numeric fields to raw numbers, then save as CSV.

    Args:
        pdf_path (str): Input PDF form file path.
        csv_path (str): Output CSV path.
        boxes (dict, optional): Boxes metadata to enrich form data.

    Returns:
        None
    """
    data = []
    try:
        # Extract form data; convert string values to uppercase where applicable

        form_data = {
            k: v.upper() if isinstance(v, str) else str(v)
            for k, v in PdfWrapper(pdf_path).data.items()
            if v is not None and str(v).strip() != "" and str(v).strip("0") != ""
        }
        # Convert raw data dict to list of dicts with explicit 'code' and 'value' keys

        data = [{"code": k, "value": v} for k, v in form_data.items()]
    except Exception as e:
        logger.error(f"Failed to extract data from {pdf_path}: {e}")
    logger.debug(f"Extracted PDF form data (type={type(data)}), count={len(data)}")

    if boxes:
        flat_boxes = [entry for sublist in boxes.values() for entry in sublist]
        conditional_merge_list(data, flat_boxes, "code", ["field_type"])
    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write CSV header

            writer.writerow(["code", "fill"])

            # Write each field record as a CSV row

            for field in data:
                code = field.get("code")
                fill_value = field.get("value")
                field_type = field.get("field_type")

                logger.debug(
                    f"Code: {code}, Raw Value: {fill_value}, Field Type: {field_type}"
                )
                if field_type in NUMERIC_FIELD_TYPES and isinstance(fill_value, str):
                    try:
                        if field_type == "CurrencyDecimal":
                            amount = parse_implied_decimal(fill_value)
                            fill_value = str(amount)  # Save raw number, not formatted!
                            logger.debug(f"Parsed CurrencyDecimal: {fill_value}")
                        elif field_type in ("DollarCents", "Dollars"):
                            decimal = field_type == "DollarCents"
                            amount = parse_money_space(fill_value, decimal=decimal)
                            fill_value = str(amount)  # Save raw number, not formatted!
                            logger.debug(f"Parsed {field_type}: {fill_value}")
                    except Exception as e:
                        logger.warning(
                            f"Failed parsing money value '{fill_value}' for field '{code}': {e}"
                        )
                writer.writerow([code, fill_value])
    except Exception as e:
        logger.error(f"Failed to write CSV file {csv_path}: {e}")
