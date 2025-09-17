"""
Parse arguments and run main processing.
"""


import argparse
import logging
import os
import sys

import fitz

from . import config
from .extract import process_boxes
from .io_utils import load_boxes_from_csv, save_pdf_form_data_to_csv
from .markup_and_fields import (
    generate_form_fields_script,
    markup_pdf,
    run_fill_pdf_fields,
    run_standalone_script,
)
from .utils import add_suffix_to_filename, parse_pages, version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_log_handler = logging.StreamHandler()
_log_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
_log_handler.setFormatter(_log_formatter)
logger.addHandler(_log_handler)


def parse_arguments():
    """
    Parse command-line arguments for the flyfield CLI tool.

    Supports options for input PDF, CSV data, marking up, form field generation,
    filling, capturing data, debug logging, and page range filtering.

    The `--pdf-pages` option accepts comma-separated pages/ranges (e.g., "1-3,5,7-10")
    to limit processing to specific pages. If omitted, all pages are processed.

    Returns:
        argparse.Namespace: Parsed CLI arguments with attributes like:
            - input_pdf (str): Input PDF file path.
            - input_csv (str or None): Input CSV data file.
            - pdf_pages (list of int or None): List of pages specified.
            - markup, fields, fill, capture, debug (bool): Flags for actions.
    """
    parser = argparse.ArgumentParser(
        description=f"flyfield v{version()} - PDF form extraction and filling"
    )
    parser.add_argument("--version", action="version", version=version())
    parser.add_argument(
        "--input-pdf", default=config.DEFAULT_INPUT_PDF, help="Input PDF filename"
    )
    parser.add_argument(
        "--pdf-pages",
        type=str,
        default=None,
        help='Comma separated page numbers/ranges to process, e.g. "1,3-4"',
    )
    parser.add_argument(
        "--input-csv", help="Input CSV file for loading blocks (skip extraction)"
    )
    parser.add_argument(
        "--markup", action="store_true", help="Mark up blocks in the output PDF"
    )
    parser.add_argument(
        "--fields", action="store_true", help="Generate PDF with form fields"
    )
    parser.add_argument(
        "--fill", metavar="FILL_CSV", help="CSV file with values to fill PDF fields"
    )
    parser.add_argument(
        "--capture", action="store_true", help="Capture form field data into CSV"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Parse pages string into list of ints if provided

    if args.pdf_pages:
        args.pdf_pages = parse_pages(args.pdf_pages)
    else:
        args.pdf_pages = None
    return args


def main():
    """
    Main entry point for flyfield CLI tool.

    Parses arguments and runs appropriate PDF form processing.
    """
    args = parse_arguments()

    # Simplified logging setup with basicConfig

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    global logger
    logger = logging.getLogger(__name__)
    logger.debug("Debug logging enabled")

    input_pdf = args.input_pdf
    if not os.path.isfile(input_pdf):
        logger.fatal(f"Input PDF file does not exist: {input_pdf}")
        sys.exit(1)
    base_csv = os.path.splitext(input_pdf)[0] + ".csv"

    if args.pdf_pages:
        config.PDF_PAGES.clear()
        config.PDF_PAGES.extend(args.pdf_pages)
    page_dict = None
    if args.input_csv:
        page_dict = load_boxes_from_csv(args.input_csv)
        if page_dict is None:
            logger.fatal(f"Failed to load boxes from input CSV: {args.input_csv}")
            sys.exit(1)
    else:
        if args.capture:
            fitz.TOOLS.mupdf_display_errors(False)
        page_dict = process_boxes(input_pdf, base_csv)
        if args.capture:
            fitz.TOOLS.mupdf_display_errors(True)
        if page_dict is None:
            logger.fatal(f"Failed to process boxes for PDF: {input_pdf}")
            sys.exit(1)
    if args.markup:
        marked_up_pdf = add_suffix_to_filename(input_pdf, config.DEFAULT_MARKUP_SUFFIX)
        markup_pdf(input_pdf, page_dict, marked_up_pdf)
        logger.info(f"Markup PDF generated: {marked_up_pdf}")
        input_pdf = marked_up_pdf
    if args.fields:
        fields_pdf = add_suffix_to_filename(input_pdf, config.DEFAULT_FIELDS_SUFFIX)
        generator_script = (
            os.path.splitext(input_pdf)[0] + config.DEFAULT_FIELD_GENERATOR_SUFFIX
        )
        script_path = generate_form_fields_script(
            args.input_csv or base_csv, input_pdf, fields_pdf, generator_script
        )
        run_standalone_script(script_path)
        logger.info(f"Form fields added and saved: {fields_pdf}")
        input_pdf = fields_pdf
    if args.fill:
        filled_pdf = add_suffix_to_filename(input_pdf, config.DEFAULT_FILL_SUFFIX)
        filler_script = os.path.splitext(input_pdf)[0] + config.DEFAULT_FILLER_SUFFIX
        logger.info(f"Filling PDF fields with CSV: {args.fill}")
        run_fill_pdf_fields(args.fill, filled_pdf, input_pdf, filler_script, page_dict)
        logger.info(f"Filled PDF saved to {filled_pdf}")
    if args.capture:
        capture_csv = os.path.splitext(input_pdf)[0] + config.DEFAULT_CAPTURE_SUFFIX
        save_pdf_form_data_to_csv(input_pdf, capture_csv, page_dict)
        logger.info(f"Captured filled fields to {capture_csv}")


if __name__ == "__main__":
    main()
