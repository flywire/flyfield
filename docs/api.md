# API Documentation for flyfield

This documentation provides a detailed reference to the **flyfield** Python API for programmatically working with PDF forms that use white box placeholders.

---

## Overview

The flyfield API helps automate workflows including:

- Extracting white box placeholders in PDFs  
- Filtering and grouping detected fields  
- Generating interactive form fields programmatically  
- Filling form fields with data from CSV files  
- Extracting filled data back to CSV format  

The API is designed to integrate with Python projects, offering programmable control beyond the CLI workflows.

---

## Key Modules and Classes

### 1. Extraction Module

#### `extract_boxes(pdf_path: str) -> List[Field]`

- Typically called automatically during CLI workflows unless an input CSV file is supplied, avoiding manual extraction steps.  
- Scans the PDF at `pdf_path` for white box placeholders.  
- Returns a list of `Field` objects representing detected form field locations with metadata like page number, coordinates, and unique codes.

---

### 2. Filtering and Grouping

#### `filter_fields(fields: List[Field], min_size: Tuple[float,float]=None, max_size: Tuple[float,float]=None) -> List[Field]`

- Filters out fields outside specified size bounds or other criteria.  
- Useful for refining detected candidates before form field generation.

#### `group_fields(fields: List[Field], max_dist: float=10.0) -> Dict[str, List[Field]]`

- Groups fields spatially or by page for batch processing or logical association.  
- `max_dist` defines maximum distance between grouped fields.

---

### 3. Field Generation

#### `generate_fields(input_pdf: str, fields: List[Field], output_pdf: str) -> None`

- Best practice is to run once per PDF version since this step can be time-consuming.  
- Creates interactive form fields in the PDF corresponding to white box locations.  
- Saves the resulting PDF as `output_pdf`.  
- Generated Python script for generation is storable for further edits.

---

### 4. Filling Fields

#### `fill_fields(input_pdf: str, input_csv: str, output_pdf: str) -> None`

- Fills the interactive form fields of `input_pdf` using data from CSV file `input_csv`.  
- Outputs a filled PDF as `output_pdf`.  
- CSV expected to contain `code` and `fill` columns matching field codes.

---

### 5. Capturing Filled Data

#### `capture_data(input_pdf: str, output_csv: str) -> None`

- Extracts all filled form data from a completed PDF form and writes to CSV.  
- Includes field `code` and entered `fill` value.

---

## Supporting Classes

### Field

Represents a detected form field placeholder.

| Attribute   | Type    | Description                                |
|-------------|---------|--------------------------------------------|
| `code`      | `str`   | Unique identifier for the field, e.g., `1-2-3` |
| `page`      | `int`   | PDF page number                             |
| `bbox`      | `tuple` | Bounding box coordinates (x0, y0, x1, y1) |
| `value`     | `str`   | Optional default or filled value           |

---

## Example Usage

```
from flyfield import extract_boxes, filter_fields, generate_fields, fill_fields, capture_data

# Extract white box placeholders
fields = extract_boxes("example.pdf")

# Filter fields by size if needed
fields = filter_fields(fields, min_size=(20, 10))

# Generate interactive fields PDF
generate_fields("example.pdf", fields, "example-fields.pdf")

# Fill fields with CSV data
fill_fields("example-fields.pdf", "data.csv", "example-fields-filled.pdf")

# Capture filled data back to CSV
capture_data("example-fields-filled.pdf", "captured_data.csv")
```

---

## Notes

- The API modules depend on libraries such as PyMuPDF and PyPDFForm for PDF manipulation.  
- Generated scripts during CLI usage correspond roughly to calls to API functions and can be used as templates.  
- Exception handling and logging is exposed via verbose and debug modes for troubleshooting.

---

## Further Resources

- [Developer Guide](developer.md) for architectural details and contribution guidelines.  
- [Worked Example](example.md) for an end-to-end demonstration of the API in action.
