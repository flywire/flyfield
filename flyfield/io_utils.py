import csv
import logging
from PyPDFForm import PdfWrapper

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

logger = logging.getLogger(__name__)

def write_csv(boxes_or_page_dict, csv_path):
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
        all_boxes = [box for boxes in boxes_or_page_dict.values() if boxes is not None for box in boxes]
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

def read_csv_rows(filename):
    """
    Read CSV rows from a file into a list of dictionaries with typed fields.

    Args:
        filename (str): Path to CSV file.

    Returns:
        list: List of dict rows with key typed conversions and
              'fill' assigned to 'block_fill' for consistency.
    """
    rows = []
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row["page_num"] = int(row["page_num"]) if row["page_num"].strip() else None
                    row["line"] = int(row["line"]) if row["line"].strip() else None
                    row["gap"] = float(row["gap"]) if row["gap"].strip() else 0.0
                    row["block_length"] = int(row["block_length"]) if row["block_length"].strip() else 0
                    row["height"] = float(row.get("height", 0))
                    row["width"] = float(row.get("width", 0))
                except (ValueError, KeyError):
                    continue
                if "fill" in row:
                    row["block_fill"] = row["fill"]
                    del row["fill"]
                rows.append(row)
    except Exception as e:
        logger.error(f"Error reading CSV rows from {filename}: {e}")
    return rows

def save_pdf_form_data_to_csv(pdf_path, csv_path):
    """Extract data from a PDF form and save as CSV file.

    Args:
        pdf_path (str): Path to the input PDF form.
        csv_path (str): Path to the output CSV file.
    """
    try:
        data = dict(
            #        sorted(
            #            (
            (k, v
                .upper()
            )
            for k, v in PdfWrapper(pdf_path).data.items()
            if v is not None and str(v).strip() != "" and str(v).strip("0") != ""
            #            ),
            #            key=lambda item: tuple(int(x) for x in item[0].split("-")),
            #        )
        )
    except Exception as e:
        logger.error(f"Failed to extract data from {pdf_path}: {e}")
        data = {}
    
    try:
        with open(csv_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["code", "fill"])
            for k, v in data.items():
                writer.writerow([k, v])
    except Exception as e:
        logger.error(f"Failed to write CSV file {csv_path}: {e}")
