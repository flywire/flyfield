# Processing Workflow of flyfield

This document provides a detailed overview of the multi-stage processing pipeline **flyfield** uses to detect, generate, fill, and capture PDF form fields based on white box placeholders.

## Workflow Diagram

``` mermaid
--8<-- "docs/assets/flyfield_workflow.mmd"
```

***

## Workflow Overview

flyfield automates converting static **white box placeholders** in PDFs into interactive, fillable forms through these stages:

1. **Extraction of White Boxes**
Identifies candidate white rectangular boxes in the PDF.
2. **Filtering, Deduplication, and Sorting**
Removes irrelevant boxes, merges duplicates, and orders them for processing.
3. **Layout Annotation & Numeric Assignment**
Groups boxes into logical blocks, labels with codes, and detects numeric field patterns.
4. **Field Generation & Markup**
Creates interactive PDF fields aligned to detected placeholders and optionally adds visual markup for verification.
5. **Filling PDF Fields**
Uses CSV data to programmatically populate fields with values.
6. **Data Capture from Filled Forms**
Extracts filled field values back into CSV for reuse or analysis.

Each phase is implemented in separate Python modules allowing flexible scripting and customization.

***

## Detailed Steps

### 1. Extraction of White Boxes

- **Module:** `flyfield.extract.extract_boxes`
- Scans the PDF via PyMuPDF to locate filled white rectangles matching the target color (default RGB white `(1,1,1)`), considering only vector content.
- Converts coordinates from PyMuPDF's origin (top-left) to PDF standard origin (bottom-left).
- Extracted data includes page number, bounding box coordinates, text overlays, and fill colors.
- Outputs a raw CSV snapshot when run with the `--debug` flag, listing all candidate boxes.

### 2. Filtering, Deduplication, and Sorting

- **Module:** `flyfield.extract`
- Applies height thresholds (`MIN_BOX_HEIGHT` and `MAX_BOX_HEIGHT`) to filter box sizes.
- Uses content-based heuristics to exclude boxes with disallowed or pre-printed text.
- Removes duplicate entries by comparing rounded box coordinates.
- Sorts remaining boxes by page, top-to-bottom, then left-to-right order.
- Writes intermediate CSV files for grouping and filtering steps if debugging is enabled.

### 3. Layout Annotation & Numeric Assignment

- **Module:** `flyfield.layout`
- Assigns unique IDs to boxes in the format `{page}-{line}-{block}`, representing logical grouping within pages and rows.
- Groups horizontally aligned boxes into blocks based on configured gap thresholds.
- Calculates block dimensions and concatenates overlay text.
- Applies numeric field recognition rules to merge multi-block numeric patterns (e.g., monetary amounts split into multiple boxes) and assign types such as `"Currency"` or `"CurrencyDecimal"`.
- Writes a detailed layout CSV for validation and debugging.

### 4. Field Generation & Markup

- **Module:** `flyfield.markup_and_fields`
- Generates a standalone Python script that, when run, adds interactive AcroForm text fields positioned and sized according to box annotations.
- Runs the generation script automatically to create a new PDF with enabled form fields.
- Optionally, creates a markup PDF that overlays visual elements such as circles around boxes, rendered field codes rotated at 45°, facilitating human verification of detection accuracy.

### 5. Filling PDF Fields

- **Module:** `flyfield.markup_and_fields.run_fill_pdf_fields`
- Generates and executes a Python script to fill interactive form fields using a CSV file mapping field codes to fill values.
- Skips entries with empty or zero values to avoid overwriting.
- Parses currency and numeric fields, normalizing inputs by removing formatting as required.
- Produces a filled PDF annotated with entered data.
- Logs script output to assist with troubleshooting.

### 6. Data Capture from Filled Forms

- **Module:** `flyfield.io_utils.save_pdf_form_data_to_csv`
- Reads completed interactive forms via PyPDFForm.
- Extracts field values, coercing numeric types based on configured rules, and normalizes text (e.g., uppercase).
- Outputs a CSV aligned with original field codes to facilitate downstream processing, data review, or iterative filling.

***

!!! Note "Additional Notes"

	- Only vector PDFs with clear white boxes are supported; scanned or rasterized PDFs are not compatible.
	- Large PDFs may take longer during field generation (`--fields`), so it is recommended to run this step sparingly and cache outputs.
	- Debug mode (`--debug`) generates helpful intermediate CSVs for each processing stage, improving traceability and aiding issue diagnosis.
	- All generated scripts are standalone and can be customized for advanced workflows or integration into automated pipelines.

***
