"""
Functions for PDF markup and form field annotation.
"""


import csv
import logging
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from . import config
from .config import GAP, GAP_GROUP, F
from .utils import conditional_merge_list

logger = logging.getLogger(__name__)


def markup_pdf(
    pdf_path: str,
    page_dict: Dict[int, List[Dict]],
    output_pdf_path: str,
    mark_color: Tuple[float, float, float] = (0, 0, 1),
    mark_radius: float = 1,
) -> None:
    """
    Mark PDF with circles and codes at block locations for debugging.

    Args:
        pdf_path (str): Input PDF file.
        page_dict (dict): Pages and boxes with layout info.
        output_pdf_path (str): Output marked PDF file path.
        mark_color (tuple): RGB float tuple for marker color.
        mark_radius (int or float): Radius of circle marks.

    Returns:
        None
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF for markup: {e}")
        return
    for page_num, boxes in sorted(page_dict.items()):
        if config.PDF_PAGES and page_num not in config.PDF_PAGES:
            continue
        page = doc[page_num - 1]
        page_height = page.rect.height
        shape = page.new_shape()

        for box in boxes:
            # Only mark boxes that have a meaningful block_length

            if box.get("block_length") not in ("", 0, None):
                x, y_raw = box.get("x0"), box.get("y0")
                y = page_height - y_raw
                shape.draw_circle((x, y), mark_radius)

                point = fitz.Point(x + 4, y)
                shape.insert_text(
                    point,
                    str(box.get("code", "?")),
                    fontsize=8,
                    color=mark_color,
                    morph=(point, fitz.Matrix(1, 0, 0, 1, 0, 0).prerotate(45)),
                )
        shape.finish(color=mark_color, fill=None)
        shape.commit()
    try:
        doc.save(output_pdf_path)
    except Exception as e:
        logger.error(f"Failed to save output PDF: {e}")
    finally:
        doc.close()


def adjust_form_boxes(
    row: Dict,
    width: float,
    block_length: int,
) -> Tuple[float, float, List[str]]:
    """
    Adjust the position and width of form boxes depending on field type and block length.

    Args:
        row (dict): Box attributes.
        width (float): Original block width.
        block_length (int): Block length in contained boxes.

    Returns:
        tuple: (adjusted x, adjusted width, list of extra args)
    """
    x = float(row["left"])
    field_type = row.get("field_type")
    extra_args = ["alignment=2"]

    if (
        block_length == 1
        and width > 14
        and field_type not in ("Currency", "CurrencyDecimal")
    ):
        # Reduce width by size of layout characters

        width_adjusted = width
        if field_type == "Dollars":
            width_adjusted -= 21
        elif field_type == "DollarCents":
            width_adjusted -= 4
        return x, max(0, width_adjusted), extra_args
    if field_type in ("Currency", "CurrencyDecimal"):
        gap_adj = (2 * GAP + GAP_GROUP) / 3 / 2
        gap_start = (gap_adj * (((block_length - 1) % 3) + 1)) / 2 + F
        if field_type == "CurrencyDecimal":
            gap_start += F * 2
        gap_end = gap_adj + F * 2 if field_type == "Currency" else (gap_adj * 3) / 2
    else:
        gap_adj = GAP
        gap_start = gap_end = gap_adj / 2 + F
        extra_args[0] = "alignment=0"
    x -= gap_start
    width_adjusted = width + gap_start + gap_end
    extra_args += [
        f"max_length={block_length}" if block_length else "max_length=None",
        "comb=True",
    ]
    return x, max(0, width_adjusted), extra_args


def generate_form_fields_script(
    csv_path: str,
    input_pdf: str,
    output_pdf_with_fields: str,
    script_path: str,
) -> str:
    """
    Generate a standalone Python script to create PDF form fields from CSV block data.

    Args:
        csv_path (str): CSV data path.
        input_pdf (str): Input PDF to annotate.
        output_pdf_with_fields (str): Output annotated PDF.
        script_path (str): Output script file path.

    Returns:
        str: Path to the generated script file.
    """
    lines = [
        "from PyPDFForm import Fields, PdfWrapper",
        f'pdf = PdfWrapper("{input_pdf}")',
    ]
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            current_page = None
            for row in reader:
                page_number = int(row["page_num"])

                # Skip rows whose page number is not in PDF_PAGES if PDF_PAGES filter is set

                if config.PDF_PAGES and page_number not in config.PDF_PAGES:
                    continue
                code = row["code"]
                if (
                    not code
                    or row["block_length"] in ("", "0")
                    or row.get("field_type") == "Skip"
                ):
                    continue
                if page_number != current_page:
                    lines.append(f'print("Starting page {page_number}...", flush=True)')
                    current_page = page_number
                block_length = (
                    int(float(row["block_length"]))
                    if row["block_length"] not in ("", "0")
                    else 0
                )
                width = (
                    float(row["block_width"])
                    if row["block_width"] not in ("", "0")
                    else 0
                )
                y, height = float(row["bottom"]), float(row.get("height", 0))
                x, width_adjusted, extra_args = adjust_form_boxes(
                    row, width, block_length
                )
                sanitized_code = re.sub(r"[^\w\-_]", "_", code)
                base_args = [
                    #                    'widget_type="text"',
                    f'name="{sanitized_code}"',
                    f"page_number={page_number}",
                    f"x={x:.2f}",
                    f"y={y:.2f}",
                    f"height={height:.2f}",
                    f"width={width_adjusted:.2f}",
                    "bg_color=(0,0,0,0)",
                    "border_color=(0,0,0,0)",
                    "border_width=0",
                ]
                args = [*base_args, *extra_args]
                lines.append(f"pdf.create_field(Fields.TextField({', '.join(args)}))")
            lines.extend(
                [
                    f'pdf.write("{output_pdf_with_fields}")',
                    'print("Created form fields PDF.", flush=True)',
                ]
            )
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        logger.error(f"Failed to generate form fields script: {e}")
    return script_path


def run_standalone_script(script_path: str) -> None:
    """
    Execute a standalone script for PDF form field creation.

    Args:
        script_path (str): Path to the script to run.
    """
    print(f"Running generated form field creation script: {script_path}")
    try:
        result = subprocess.run([sys.executable, "-u", script_path], text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Generated script failed with exit code {result.returncode}"
            )
    except Exception as e:
        logger.error(f"Error running generated script: {e}")


def run_fill_pdf_fields(
    csv_path: str,
    output_pdf_path: str,
    template_pdf_path: str,
    generator_script_path: str,
    boxes: Optional[Dict[int, List[Dict]]] = None,
) -> None:
    """
    Generates and runs a standalone Python script to fill PDF form fields using PyPDFForm,

    based on data from a CSV file with 'code' and 'fill' columns.

    Args:
        csv_path (str): Path to the CSV input file.
        output_pdf_path (str): Path where the filled PDF should be saved.
        template_pdf_path (str): Path to the input (template) PDF file.
        generator_script_path (str): Path where the generated fill script will be saved.
    """
    from .utils import format_money_space, parse_money_space

    fill_data = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                # Clean row values

                stripped_row = {
                    k: v.strip() if isinstance(v, str) else v for k, v in row.items()
                }
                if all(v == "" or v == "0" for v in stripped_row.values()):
                    continue
                rows.append(stripped_row)
        # Flatten boxes if any and merge to rows

        if boxes:
            flat_boxes = [entry for sublist in boxes.values() for entry in sublist]
            conditional_merge_list(rows, flat_boxes, "code", ["field_type"])
        for row in rows:
            field = row.get("code")
            value = row.get("fill")
            field_type = row.get("field_type", "")
            if not field or value in ("", "0"):
                continue
            if field_type in ("Dollars", "DollarCents"):
                decimal = field_type == "DollarCents"
                try:
                    amount = parse_money_space(value, decimal=decimal)
                    value = format_money_space(amount, decimal=decimal)
                except Exception as e:
                    print(
                        f"Warning: Could not format value '{value}' for field_type '{field_type}': {e}"
                    )
            elif field_type in ("Currency", "CurrencyDecimal"):
                import re

                value = re.sub(r"\D", "", value)
            fill_data[field] = value
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return
    fill_dict_items = ",\n ".join(f'"{k}": {repr(v)}' for k, v in fill_data.items())
    script_content = f"""\
from PyPDFForm import PdfWrapper
print("Starting to fill PDF fields...", flush=True)
try:
    filled = PdfWrapper(
        "{template_pdf_path}",
        adobe_mode=False
    ).fill(
        {{
            {fill_dict_items}
        }},
        flatten=False
    )
    filled.write("{output_pdf_path}")
    print("Filled PDF saved to {output_pdf_path}", flush=True)
except Exception as e:
    print(f"Exception during filling: {{e}}", file=sys.stderr, flush=True)
    sys.exit(1)
"""

    try:
        with open(generator_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(script_content)
        print(f"Generated fill script saved to {generator_script_path}")
    except Exception as e:
        print(f"Error writing fill script to {generator_script_path}: {e}")
        return
    try:
        result = subprocess.run(
            [sys.executable, generator_script_path], capture_output=True, text=True
        )
        print("Fill script stdout:")
        print(result.stdout)
        print("Fill script stderr:")
        print(result.stderr)
        if result.returncode != 0:
            print(f"Fill script failed with exit code {result.returncode}")
        else:
            print("Fill script completed successfully.")
    except Exception as e:
        print(f"Error running fill script: {e}")
