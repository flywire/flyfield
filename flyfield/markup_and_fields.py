import csv
import logging
import re
import subprocess
import sys
import fitz  # PyMuPDF
from .io_utils import read_csv_rows
from .utils import add_suffix_to_filename
from .config import (
    PDF_PAGES,
    DEFAULT_FIELD_GENERATOR_SUFFIX,
    DEFAULT_FIELDS_SUFFIX,
    DEFAULT_FILLER_SUFFIX,
    DEFAULT_MARKUP_SUFFIX,
    GAP,
    GAP_GROUP,
)

logger = logging.getLogger(__name__)

def markup_pdf(
    pdf_path, page_dict, output_pdf_path, mark_color=(0, 0, 1), mark_radius=1
):
    """
    Mark up PDF with visual circles and codes for each block for debugging purposes.

    Args:
        pdf_path (str): Input PDF path.
        page_dict (dict): Dictionary keyed by page number with lists of boxes with layout info.
        output_pdf_path (str): Output marked PDF filename.
        mark_color (tuple): RGB color tuple (floats 0-1) for marks. Default blue.
        mark_radius (int or float): Radius of circles to draw at block locations.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF for markup: {e}")
        return

    for page_num, boxes in sorted(page_dict.items()):
        if PDF_PAGES and page_num not in PDF_PAGES:
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

def adjust_form_boxes(row, width, block_length):
    """
    Adjust position and width of form boxes depending on field type and block length.

    Args:
        row (dict): Dictionary representing a box/box with its attributes.
        width (float): Original width of the block.
        block_length (int): Length of the block in terms of contained boxes.

    Returns:
        tuple: (adjusted x coordinate (float), adjusted width (float), list of extra arguments(str))
    """
    x = float(row["left"])
    field_type = row.get("field_type")
    extra_args = ["alignment=2"]

    if (
        block_length == 1
        and width > 14
        and field_type not in ("Currency", "CurrencyDecimal")
    ):
        width_adjusted = width
        if field_type == "Dollars":
            width_adjusted -= 21
        elif field_type == "DollarCents":
            width_adjusted -= 4
        return x, max(0, width_adjusted), extra_args

    if field_type in ("Currency", "CurrencyDecimal"):
        gap_adj = (2 * GAP + GAP_GROUP) / 3
        gap_start = (gap_adj * (block_length % 3)) / 2
        gap_end = gap_adj if field_type == "CurrencyDecimal" else (gap_adj * 3) / 2
    else:
        gap_adj = GAP
        gap_start = gap_end = gap_adj / 2 + 1
        extra_args[0] = "alignment=0"

    x -= gap_start
    width_adjusted = width + gap_start + gap_end
    extra_args += [
        f"max_length={block_length}" if block_length else "max_length=None",
        "comb=True",
    ]
    return x, max(0, width_adjusted), extra_args

def generate_form_fields_script(csv_path, input_pdf, output_pdf_with_fields, script_path):
    """
    Generate a standalone Python script for creating form fields in a PDF from CSV data.

    Args:
        csv_path (str): Path to CSV file with block data.
        input_pdf (str): Input PDF path to annotate.
        output_pdf_with_fields (str): Output PDF path where form fields will be written.
        script_path (str): Path to generated script file.

    Returns:
        str: Path to the generated script file.
    """
    lines = [
        "from PyPDFForm import PdfWrapper",
        f'pdf = PdfWrapper("{input_pdf}")',
    ]
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            current_page = None
            for row in reader:
                code = row["code"]
                if not code or row["block_length"] in ("", "0") or row.get("field_type") == "Skip":
                    continue
                page_number = int(row["page_num"])
                if page_number != current_page:
                    lines.append(f'print("Starting page {page_number}...", flush=True)')
                    current_page = page_number
                block_length = int(float(row["block_length"])) if row["block_length"] not in ("", "0") else 0
                width = float(row["block_width"]) if row["block_width"] not in ("", "0") else 0
                y, height = float(row["bottom"]), float(row.get("height", 0))
                x, width_adjusted, extra_args = adjust_form_boxes(row, width, block_length)
                sanitized_code = re.sub(r"[^\w\-\_]", "_", code)
                base_args = [
                    'widget_type="text"',
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
                lines.append(f"pdf.create_widget({', '.join(args)})")
        lines.extend([
            f'pdf.write("{output_pdf_with_fields}")',
            'print("Created form fields PDF.", flush=True)',
        ])
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        logger.error(f"Failed to generate form fields script: {e}")
    return script_path

def run_standalone_script(script_path):
    """
    Execute the generated Python script to create form fields in the PDF.

    Args:
        script_path (str): Path to the generated form field creation script.
    """
    print(f"Running generated form field creation script: {script_path}")
    try:
        result = subprocess.run([sys.executable, "-u", script_path], text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Generated script failed with exit code {result.returncode}")
    except Exception as e:
        logger.error(f"Error running generated script: {e}")

def run_fill_pdf_fields(csv_path, output_pdf_path, template_pdf_path, generator_script_path):
    """
    Generates and runs a standalone Python script to fill PDF form fields using PyPDFForm,
    based on data from a CSV file with 'code' and 'fill' columns.

    Args:
        csv_path (str): Path to the CSV input file.
        output_pdf_path (str): Path where the filled PDF should be saved.
        template_pdf_path (str): Path to the input (template) PDF file.
        generator_script_path (str): Path where the generated fill script will be saved.
    """
    fill_data = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stripped_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                if all(v == "" or v == "0" for v in stripped_row.values()):
                    continue
                field = stripped_row.get("code")
                value = stripped_row.get("fill")
                if field and value not in ("", "0"):
                    fill_data[field] = value
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return

    fill_dict_items = ",\n        ".join(f'"{k}": {repr(v)}' for k, v in fill_data.items())
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
        result = subprocess.run([sys.executable, generator_script_path], capture_output=True, text=True)
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
