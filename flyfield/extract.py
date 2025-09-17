"""
Extraction functions for PDF processing.

Provides methods to extract PDF box data and text.
"""

import logging
from collections import defaultdict
from typing import Dict, List

import fitz  # PyMuPDF

from .config import MAX_BOX_HEIGHT, MIN_BOX_HEIGHT, TARGET_COLOUR
from .io_utils import write_csv
from .layout import assign_numeric_blocks, calculate_layout_fields
from .utils import allowed_text, colour_match, int_to_rgb

logger = logging.getLogger(__name__)


def extract_boxes(pdf_path: str) -> List[Dict]:
    """
    Extract filled rectangles (boxes) from a PDF matching a target color.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        list of dict: Each dict details box coordinates (PDF coordinates, origin bottom-left),
        page number, and other metadata for detected boxes.

    Notes:
        Converts PyMuPDF coordinates (origin top-left) to PDF standard bottom-left origin.
        Only boxes filled with the target color are extracted.
    """
    boxes = []
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(1, len(doc) + 1):
                try:
                    page = doc[page_num - 1]
                except IndexError:
                    logger.warning(f"Page {page_num} not found in document.")
                    continue
                page_height = page.rect.height
                for drawing in page.get_drawings():
                    rect = drawing.get("rect")
                    fill_color = drawing.get("fill")
                    if rect and colour_match(fill_color, target_color=TARGET_COLOUR):
                        # Convert PyMuPDF page coordinates (origin top-left)
                        # to PDF coordinate system (origin bottom-left)

                        pdf_y0 = page_height - rect.y1
                        pdf_y1 = page_height - rect.y0
                        boxes.append(
                            {
                                "page_num": page_num,
                                "x0": rect.x0,
                                "y0": pdf_y0,
                                "x1": rect.x1,
                                "y1": pdf_y1,
                                "left": round(rect.x0, 2),
                                "bottom": round(pdf_y0, 2),
                                "right": round(rect.x1, 2),
                                "top": round(pdf_y1, 2),
                                "chars": "",
                                "field_type": None,
                            }
                        )
    except Exception as e:
        logger.error(f"Could not open PDF file {pdf_path}: {e}")
    return boxes


def filter_boxes(page: fitz.Page, boxes: List[Dict]) -> List[Dict]:
    """
    Filter a list of boxes on a PDF page based on height and allowed text.

    Args:
        page (fitz.Page): PyMuPDF page object.
        boxes (list of dict): List of box dictionaries to filter.

    Returns:
        list of dict: Filtered boxes that meet size and allowed text criteria.

    Notes:
        Excludes boxes outside valid height ranges or with disallowed text.
    """
    filtered = []
    page_height = page.rect.height
    black = (0, 0, 0)  # RGB for black text matching

    for box in boxes:
        height = box.get("y1", 0) - box.get("y0", 0)
        if height < MIN_BOX_HEIGHT or height > MAX_BOX_HEIGHT:
            continue
        # Convert box coordinates to PyMuPDF's coordinate system for clipping

        pymupdf_y0 = page_height - box["y1"]
        pymupdf_y1 = page_height - box["y0"]
        clip_rect = fitz.Rect(box["x0"], pymupdf_y0, box["x1"], pymupdf_y1)

        text_dict = page.get_text("dict", clip=clip_rect)

        black_text_parts = []
        non_black_text_parts = []

        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if not span_text:
                        continue
                    span_color = span.get("color")
                    rgb = None
                    if span_color is not None:
                        if isinstance(span_color, int):
                            rgb = int_to_rgb(span_color)
                        elif isinstance(span_color, str):
                            try:
                                rgb = fitz.utils.getColor(span_color)
                            except Exception:
                                rgb = None
                    if rgb and colour_match(rgb, target_color=black):
                        black_text_parts.append(span_text)
                    else:
                        non_black_text_parts.append(span_text)
        fill_text = "".join(black_text_parts)
        box_text = "".join(non_black_text_parts)

        allowed, detected_field_type = allowed_text(
            box_text, field_type=box.get("field_type")
        )
        if box_text and not allowed:
            continue
        box["field_type"] = detected_field_type
        box["chars"] = box_text
        box["fill"] = fill_text
        filtered.append(box)
    return filtered


def remove_duplicates(boxes: List[Dict]) -> List[Dict]:
    """
    Remove duplicate boxes on the same page based on rounded coordinates.

    Args:
        boxes (list of dict): List of box dictionaries.

    Returns:
        list of dict: Boxes with duplicates removed.
    """
    page_groups = defaultdict(list)
    for box in boxes:
        page_groups[box["page_num"]].append(box)
    cleaned = []
    for _page_num, page_boxes in page_groups.items():
        seen = set()
        for box in page_boxes:
            key = (
                round(box["x0"], 3),
                round(box["y0"], 3),
                round(box["x1"], 3),
                round(box["y1"], 3),
            )
            if key not in seen:
                seen.add(key)
                cleaned.append(box)
    return cleaned


def sort_boxes(boxes: List[Dict], decimal_places: int = 0) -> List[Dict]:
    """
    Sort boxes by page number, top-to-bottom (descending), then left-to-right.

    Args:
        boxes (list of dict): List of boxes to sort.
        decimal_places (int): Precision for vertical grouping (bottom coordinate rounding).

    Returns:
        list of dict: Sorted boxes.
    """
    return sorted(
        boxes,
        key=lambda b: (b["page_num"], -round(b["bottom"], decimal_places), b["left"]),
    )


def process_boxes(pdf_path: str, csv_path: str) -> Dict[int, List[Dict]]:
    """
    Full pipeline to extract, filter, deduplicate, sort, layout annotate, and save boxes from a PDF.

    Args:
        pdf_path (str): Path to input PDF file.
        csv_path (str): Path to output CSV file for annotated box data.

    Returns:
        dict: Dictionary keyed by page number containing processed boxes with layout metadata.

    Notes:
        - Extract filled white boxes matching TARGET_COLOUR.
        - Filter boxes by valid height and allowed text content.
        - Remove duplicate boxes by coordinate proximity.
        - Sort boxes by page, vertical then horizontal order.
        - Compute layout fields such as IDs, block grouping, lines.
        - Assign numeric block field types using heuristics.
        - Write the full annotated box data to CSV.
    """
    logger.info(f"Extracting boxes from PDF: {pdf_path}")
    boxes = extract_boxes(pdf_path)
    logger.info(f"Extracted {len(boxes)} white boxes.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Error opening input PDF: {e}")
        return defaultdict(list)
    if logger.isEnabledFor(logging.DEBUG):
        write_csv(boxes, csv_path.replace(".csv", "-extracted.csv"))
    filtered_boxes = []
    for page_num in range(1, len(doc) + 1):
        page_boxes = [p for p in boxes if p["page_num"] == page_num]
        filtered_boxes.extend(filter_boxes(doc[page_num - 1], page_boxes))
    doc.close()

    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, csv_path.replace(".csv", "-grouped.csv"))
    filtered_boxes = remove_duplicates(filtered_boxes)
    filtered_boxes = sort_boxes(filtered_boxes, decimal_places=-1)

    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, csv_path.replace(".csv", "-filtered.csv"))
    page_dict = calculate_layout_fields(filtered_boxes)

    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, csv_path.replace(".csv", "-layout.csv"))
    page_dict = assign_numeric_blocks(page_dict)

    write_csv(page_dict, csv_path)
    return page_dict
