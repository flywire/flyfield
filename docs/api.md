# API Documentation for flyfield

This documentation provides a detailed reference to the **flyfield** Python API for programmatically working with PDF forms that use **white box placeholders**.

!!! info "Overview"

	The flyfield API automates workflows including:
	
	- Extracting *white box placeholders* from vector PDFs
	- Filtering, deduplicating, and grouping detected regions into logical fields
	- Generating interactive **AcroForm** fields in PDFs programmatically
	- Filling form fields with data from CSV files
	- Capturing data back from filled PDFs into CSV

The API is modular and can be imported into Python projects, offering programmable control beyond the CLI.

***

## Key Modules and Functions

### 1. Extraction (`extract.py`)

- **`extract_boxes(pdf_path: str) -> List[dict]`**
Extracts all white boxes from a PDF that match `config.TARGET_COLOUR` (pure white by default).
    - Converts coordinates to the standard bottom-left PDF system.
    - Returns a list of box dictionaries with metadata such as `page_num`, `bbox`, `chars`, and `field_type`.
- **`filter_boxes(page: fitz.Page, boxes: List[dict]) -> List[dict]`**
Filters raw boxes by:
    - Size (`MIN_BOX_HEIGHT`, `MAX_BOX_HEIGHT`)
    - Allowed text (`utils.allowed_text`)
    - Retains only candidate placeholders.
- **`remove_duplicates(boxes: List[dict]) -> List[dict]`**
Removes duplicates based on rounded coordinates on each page.
- **`sort_boxes(boxes: List[dict], decimal_places: int=0) -> List[dict]`**
Sorts results **top-to-bottom, then left-to-right**.
- **`process_boxes(pdf_path: str, csv_path: str) -> Dict[int, List[dict]]`**
Full extraction pipeline:

1. Extract → Filter → Deduplicate → Sort
2. Compute layout fields (`calculate_layout_fields`)
3. Assign numeric block types (`assign_numeric_blocks`)
4. Save annotated results to CSV
Returns a dictionary keyed by `page_num`.

***

### 2. Layout (`layout.py`)

- **`calculate_layout_fields(boxes: List[dict]) -> Dict[int, List[dict]]`**
Annotates box rows with:
    - IDs, line numbers, block grouping
    - Block length/width
    - Concatenated `block_fill` text or formatted money values
- **`assign_numeric_blocks(page_dict: Dict[int, List[dict]]) -> Dict[int, List[dict]]`**
Merges sequential numeric blocks (e.g. `### ### ##` patterns) into currency fields.
    - Assigns `"Currency"` or `"CurrencyDecimal"` where applicable.

***

### 3. CSV I/O (`io_utils.py`)

- **`load_boxes_from_csv(csv_path: str) -> Dict[int, List[dict]]`**
Reads CSV data into a page dictionary for further processing.
- **`write_csv(data, csv_path: str) -> None`**
Writes box/page data back to CSV in canonical format.
    - Ensures only one `fill` column is stored (`block_fill` or fallback `fill`).
- **`read_csv_rows(filename: str) -> List[dict]`**
Reads CSV into dictionaries, parsing numeric fills with `parse_money_space` or `parse_implied_decimal`.
- **`save_pdf_form_data_to_csv(pdf_path: str, csv_path: str, boxes: dict=None) -> None`**
Captures filled AcroForm values from a PDF and writes them to CSV.
    - Applies `NUMERIC_FIELD_TYPES` parsing rules.
    - Uppercases strings where applicable.

***

### 4. Markup and Field Scripts (`markup_and_fields.py`)

- **`markup_pdf(pdf_path: str, page_dict: Dict[int,List[dict]], output_pdf: str, mark_color=(0,0,1)) -> None`**
Creates a **debug PDF** marking detected fields with circles and rotated field codes.
- **`generate_form_fields_script(csv_path: str, input_pdf: str, output_pdf: str, script_path: str) -> str`**
Generates a **standalone Python script** that adds AcroForm fields to a given PDF, based on detected CSV data.
- **`run_standalone_script(script_path: str) -> None`**
Executes the generated script in a subprocess to apply fields.
- **`run_fill_pdf_fields(csv_path: str, output_pdf: str, template_pdf: str, generator_script: str, boxes: dict=None) -> None`**
Generates and runs a filler script that populates an interactive PDF with values from a CSV.
    - Supports monetary formatting via `format_money_space`.
    - Supports normalization of Currency/CurrencyDecimal values by stripping non-digits.

***

### 5. Utilities (`utils.py`)

- **`add_suffix_to_filename(filename: str, suffix: str) -> str`**
Adds a suffix before the file extension.
- **`colour_match(color: Tuple, target_color=(1,1,1), tol=1e-3) -> bool`**
Compares normalized RGB colors with tolerance.
- **`int_to_rgb(color_int: int) -> Tuple[float,float,float]`**
Converts an integer 0xRRGGBB color to normalized floats.
- **`clean_fill_string(line_text: str) -> str`**
Removes single spaces but preserves aligned spacing.
- **`allowed_text(text: str, field_type: Optional[str]) -> Tuple[bool, Optional[str]]`**
Checks whether a string value inside a field is allowed (filters out pre-printed text).
- **`format_money_space(amount: Union[float,int], decimal=True) -> str`**
Formats numeric values with:
    - Space as thousand separator
    - Space as decimal marker (if decimal=True)
- **`parse_money_space(s: str, decimal=True) -> Union[int,float]`**
Parses strings formatted above back into numbers.
- **`parse_implied_decimal(s: str) -> float`**
Parses numbers treating the last two digits as cents.
- **`parse_pages(pages_str: str) -> List[int]`**
Parses `"1,3-5,7"` into `[1,3,4,5,7]`.
- **`conditional_merge_list(main_list, ref_list, match_key, keys_to_merge)`**
Merges keys from a reference list into a main list when values of `match_key` match.

***

## Field Data Structure

flyfield represents form fields as dictionaries (not classes):


| Key | Type | Description |
| :-- | :-- | :-- |
| `code` | str | Unique identifier (`page-line-block` naming scheme) |
| `page_num` | int | PDF page number (1-based) |
| `x0,y0,x1,y1` | float | Bounding box coordinates (PDF bottom-left system) |
| `left, right` | float | Rounded left/right coordinates |
| `top, bottom` | float | Rounded positions |
| `line` | int | Line number on page |
| `block` | int | Block number within line |
| `block_length` | int | Number of boxes in block |
| `block_width` | float | Width of block in points |
| `field_type` | str | One of `"Dollars"`, `"DollarCents"`, `"Currency"`, etc. |
| `chars` | str | Non-black overlay text extracted |
| `fill` | str/num | Overlay text (user values, may be pre-filled) |
| `block_fill` | str/num | Aggregated/normalized block fill |


***

## Example Usage

```python
from flyfield.extract import process_boxes
from flyfield.io_utils import save_pdf_form_data_to_csv
from flyfield.markup_and_fields import  run_fill_pdf_fields
from flyfield import config

# Process boxes and save CSV
page_dict = process_boxes("example.pdf", "example.csv")

# Generate a markup PDF
from flyfield.markup_and_fields import markup_pdf
markup_pdf("example.pdf", page_dict, "example-markup.pdf")

# Fill fields with values from another CSV
run_fill_pdf_fields("example.csv",
                    "example-filled.pdf",
                    "example-fields.pdf",
                    "example-filler.py",
                    page_dict)

# Capture back to CSV after filling
save_pdf_form_data_to_csv("example-filled.pdf", "example-capture.csv", page_dict)
```


***

!!! info

	- flyfield depends on **PyMuPDF** (`fitz`) for box extraction and markup, and **PyPDFForm** for form field creation and filling.
	- Monetary/Currency parsing is opinionated.
	- All generated scripts (`-field-generator.py`, `-filler.py`) are standalone and reusable in case of workflow adjustments.
	- Debug logging (`--debug`) outputs stepwise CSVs for troubleshooting.

***

## Further Resources

- [Configuration Reference](config.md) — adjustable thresholds and suffixes
- [Developer Guide](developer.md) — core architecture and extension points
- [Worked Example](example.md) — end-to-end workflow with CSV integration

***

Automatic documentation from sources by [mkdocstrings](https://mkdocstrings.github.io/).

## Core Modules

::: flyfield.extract

::: flyfield.io_utils

::: flyfield.layout

::: flyfield.markup_and_fields

::: flyfield.utils

***
