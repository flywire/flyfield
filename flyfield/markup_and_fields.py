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
from .utils import conditional_merge_list, format_money_space, parse_money_space, FLYFIELD_KEYWORDS, update_metadata

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
        output_pdf_path (str): Path where the filled PDF should be saved.
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
    input_pdf_path: str,
    output_pdf_path: str,
    script: str,
) -> str:
    """
    Generate a standalone Python script to create PDF form fields from CSV block data.

    Args:
        csv_path (str): CSV data path.
        input_pdf_path (str): Input PDF to annotate.
        output_pdf_path (str): Output annotated PDF.
        script (str): Output script file path.

    Returns:
        str: Path to the generated script file.
    """
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            page_fields = {}

            for row in reader:
                page_number = int(row["page_num"])

                if config.PDF_PAGES and page_number not in config.PDF_PAGES:
                    continue
                code = row["code"]
                if not code or row["block_length"] in ("", "0") or row.get("field_type") == "Skip":
                    continue

                block_length = int(float(row["block_length"])) if row["block_length"] not in ("", "0") else 0
                width = float(row["block_width"]) if row["block_width"] not in ("", "0") else 0
                y, height = float(row["bottom"]), float(row.get("height", 0))
                x, width_adjusted, extra_args = adjust_form_boxes(row, width, block_length)
                sanitised_code = re.sub(r"[^\w\-_]", "_", code)

                base_args = [
                    f'name="{sanitised_code}"',
                    f"page_number={page_number}",
                    f"x={x:.2f}",
                    f"y={y:.2f}",
                    f"width={width_adjusted:.2f}",
                ]

                field_line = f'text_field({", ".join(base_args + extra_args)}),'

                page_fields.setdefault(page_number, []).append(field_line)

            # Build PAGES dict with left-aligned fields
            pages_blocks = []
            for page_num, fields_list in sorted(page_fields.items()):
                fields_str = '\n'.join(fields_list)
                page_block = f"""    {page_num}: [
{fields_str}
    ],"""
                pages_blocks.append(page_block)

            pages_dict = ''.join(pages_blocks)   # or ''.join([...]) if you want it as one block

            script_content = f"""from PyPDFForm import Fields, PdfWrapper
import sys

try:
    from flyfield.utils import update_metadata
except ModuleNotFoundError:
    def update_metadata(path, keywords=None):
        print("WARNING: 'flyfield' module not found; metadata update skipped.", flush=True)

output_pdf_path = {repr(output_pdf_path)}
pdf = PdfWrapper({repr(input_pdf_path)}, preserve_metadata=True)

def text_field(name, page_number, x, y, width, **kwargs):
    \"\"\"
    Helper for common TextField defaults.
    \"\"\"
    return Fields.TextField(
        name=name,
        page_number=page_number,
        x=x,
        y=y,
        width=width,
        height=16.50,
        bg_color=(0, 0, 0, 0),
        border_color=(0, 0, 0, 0),
        border_width=0,
        tooltip='Enter data',  # Fails
        **kwargs,
    )

# ========== EDITABLE FIELD DESCRIPTIONS ==========
PAGES = {{
{pages_dict}
}}
# ==========================================

print("Creating PDF form fields...", flush=True)
for page_num, fields in sorted(PAGES.items()):
    print(f"Processing page {{page_num}}...", flush=True)
    pdf.bulk_create_fields(fields)

pdf.write(output_pdf_path)
update_metadata(output_pdf_path, keywords={repr(FLYFIELD_KEYWORDS)})
print(f"Form fields PDF saved to {{output_pdf_path}}", flush=True)
"""

        with open(script, "w", encoding="utf-8") as f:
            f.write(script_content)

    except Exception as e:
        logger.error(f"Failed to generate form fields script: {e}")
    return script


def run_standalone_script(script: str) -> None:
    """
    Execute a standalone script for PDF form field creation.

    Args:
        script (str): Path to the script to run.
    """
    print(f"Running generated form field creation script: {script}")
    try:
        result = subprocess.run([sys.executable, "-u", script], text=True)
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
    generator_script: str,
    boxes: Optional[Dict[int, List[Dict]]] = None,
) -> None:
    """
    Generates and runs a standalone Python script to fill PDF form fields using PyPDFForm,

    based on data from a CSV file with 'code' and 'fill' columns.

    Args:
        csv_path (str): Path to the CSV input file.
        output_pdf_path (str): Path where the filled PDF should be saved.
        template_pdf_path (str): Path to the input (template) PDF file.
        generator_script (str): Path where the generated fill script will be saved.
    """
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
                if field_type in ("DollarCents", "CurrencyDecimal"):
                    value = f"{round(float(value), 2):.2f}"
                if field_type in ("Dollars", "DollarCents"):
                    decimal = field_type == "DollarCents"
                    try:
                        amount = parse_money_space(value, decimal=decimal)
                        value = format_money_space(amount, decimal=decimal)
                    except Exception as e:
                        print(
                            f"Warning: Could not format value '{value}' "
                            f"for field_type '{field_type}': {e}"
                        )
                elif field_type in ("Currency", "CurrencyDecimal"):
                    value = re.sub(r"[^\d]", "", value)
                fill_data[field] = value
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return
    fill_dict_items = ",\n ".join(f'"{k}": {repr(v)}' for k, v in fill_data.items())

    script_content = f"""\
from PyPDFForm import PdfWrapper
import sys
from flyfield.utils import update_metadata

print("Starting to fill PDF fields...", flush=True)
try:
    output_pdf = "{output_pdf_path}"
    filled = PdfWrapper(
        "{template_pdf_path}",
        need_appearances=True,     # helps text rendering
        sign_enable=True,          # prepares for digital signatures
        preserve_metadata=True,    # keeps Title, Author, etc.
    ).fill(
        {{
 {fill_dict_items}
        }},
        flatten=False
    )
    filled.write(output_pdf)

    update_metadata(output_pdf, keywords={repr(FLYFIELD_KEYWORDS)})
    print(f"Filled PDF saved to {{output_pdf}}", flush=True)
except Exception as e:
    print(f"Exception during filling: {{e}}", file=sys.stderr, flush=True)
    sys.exit(1)
"""

    try:
        with open(generator_script, "w", encoding="utf-8") as script_file:
            script_file.write(script_content)
        print(f"Generated fill script saved to {generator_script}")
    except Exception as e:
        print(f"Error writing fill script to {generator_script}: {e}")
        return
    try:
        result = subprocess.run(
            [sys.executable, generator_script],
            capture_output=True,
            text=True,
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
