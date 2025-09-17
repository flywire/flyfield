# Configuration and Constants for flyfield

This document describes configuration settings, constants, and customizable parameters available in **flyfield** to tailor processing and output.

## Configuration Overview

flyfield uses a combination of **CLI flags**, **internal constants**, and **Python APIs** to control behavior during extraction, field generation, filling, and capturing. At its core, flyfield relies on detecting **white vector boxes** in PDFs, applying heuristics, and mapping them into interactive form fields.

***

## CLI Configuration Options

| Option | Description |
| :-- | :-- |
| `--input-pdf FILE` | Specifies the input PDF file. |
| `--pdf-pages` | Comma-separated list or ranges of pages to process, e.g., `"1,3-5,7"`. |
| `--input-csv FILE` | Specify a CSV file for input blocks or captured data. Skips detection step. |
| `--markup` | Generate a markup PDF showing detected placeholders and field codes. |
| `--fields` | Generate interactive PDF fields from detected or CSV-loaded data. |
| `--fill FILE` | Provide a CSV file to fill PDF form fields with data. |
| `--capture` | Capture filled field data from PDF back into CSV. |
| `--debug` | Enable verbose debug output including intermediate CSV files. |


***

## Internal Configuration Constants

These constants (defined in `flyfield/config.py`) control thresholds, suffixes, and color detection used internally.

| Parameter | Description | Default Value |
| :-- | :-- | :-- |
| `DEFAULT_INPUT_PDF` | Default input PDF filename | `"input.pdf"` |
| `DEFAULT_CAPTURE_SUFFIX` | Filename suffix for captured filled fields CSV | `"-capture.csv"` |
| `DEFAULT_FIELD_GENERATOR_SUFFIX` | Filename suffix for generated field creation script | `"-field-generator.py"` |
| `DEFAULT_FILLER_SUFFIX` | Filename suffix for generated field filling script | `"-filler.py"` |
| `DEFAULT_MARKUP_SUFFIX` | Filename suffix for markup PDF | `"-markup"` |
| `DEFAULT_FIELDS_SUFFIX` | Filename suffix for generated fields PDF | `"-fields"` |
| `DEFAULT_FILL_SUFFIX` | Filename suffix for filled PDF | `"-filled"` |
| `COLOR_WHITE` | Normalized RGB tuple for target white detection | `(1, 1, 1)` |
| `COLOR_BLACK` | Normalized RGB tuple for black text filtering | `(0, 0, 0)` |
| `TARGET_COLOUR` | Color targeted for detection (default is white) | `(1, 1, 1)` |
| `GAP` | Minimum horizontal gap between boxes in the same block | `1.9` |
| `GAP_GROUP` | Gap threshold used for grouping blocks | `7.6` |
| `GAP_THRESHOLD` | Threshold for breaking blocks due to large gaps | `3.0` |
| `F` | Small fudge factor for positioning adjustments | `1` |
| `MIN_BOX_HEIGHT` | Minimum height of detected boxes (points) | `15.0` |
| `MAX_BOX_HEIGHT` | Maximum height of detected boxes (points) | `30.0` |
| `NUMERIC_FIELD_TYPES` | List of field types considered numeric | `["Currency", "CurrencyDecimal", "DollarCents", "Dollars"]` |
| `PDF_PAGES` | Global list of pages to process during a run | `[]` |


***

## Customizing Field Detection

flyfield’s field detection pipeline can be tuned by modifying constants or APIs:

- **Height Filters**
Adjust `MIN_BOX_HEIGHT` and `MAX_BOX_HEIGHT` to control acceptable box sizes.
- **Colour Filters**
Change `TARGET_COLOUR` to detect placeholders of different colours if necessary.
- **Horizontal Grouping Sensitivity**
Modify `GAP`, `GAP_GROUP`, and `GAP_THRESHOLD` to customize grouping behaviour of detected boxes.
- **Field Type Assignment**
Update `NUMERIC_FIELD_TYPES` to support additional or alternative numeric field types.

***

## CSV Handling

- CSV files must be UTF-8 encoded and contain structured metadata columns like `page_num`, `id`, `x0`, `y0`, etc., alongside the `fill` values.
- Numeric fields are parsed using:
    - `parse_money_space`
    - `parse_implied_decimal`
- Output formatting uses `format_money_space`.
- Running with the `--debug` flag writes intermediate CSV snapshots for detailed troubleshooting.

***

## Environment Variables

| Variable | Description |
| :-- | :-- |
| `flyfield_LOG_LEVEL` | Sets logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `flyfield_CONFIG_FILE` | Reserved for future support for user-configured JSON/YAML files |


***

## Example: Adjust Box Height Threshold

```python
from flyfield import config, extract

config.MIN_BOX_HEIGHT = 12.0  # Lower minimum height

boxes = extract.extract_boxes("example.pdf")
```


***

!!! info

	- Most users can rely solely on the CLI with default constants.
	- Developers can override these settings programmatically.
	- The generated Python scripts for field generation and filling remain customizable entry points.

***
