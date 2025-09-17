# User Guide and CLI Reference

This guide details the command-line interface (CLI) options and typical workflows for using **flyfield** effectively.


## CLI Basic Structure

Run flyfield commands with the following general syntax:

```
flyfield [options]
```

***

## Common Command-Line Options

| Option | Description |
| :-- | :-- |
| `--version` | Show the installed flyfield version and exit  |
| `--input-pdf FILE` | Specify the input PDF filename to process  |
| `--pdf-pages PAGES` | Select pages to process, e .g., `"1,3-5,7"`  |
| `--input-csv FILE` | Specify a CSV file with field data, skipping extraction  |
| `--markup` | Generate a markup PDF showing detected fields and codes  |
| `--fields` | Generate interactive form fields on the PDF  |
| `--fill FILE` | Fill form fields using values from the specified CSV file  |
| `--capture` | Extract filled form data back into a CSV  |
| `--debug` | Enable verbose debug outputs for troubleshooting  |
| `-h`, `--help` | Show help message and exit  |

***

## Typical Workflow Examples

### Generate Fields and Extract Data

If you have no CSV, flyfield automatically detects white box placeholders and generates fields.

```
flyfield --input-pdf form.pdf --fields
```

Produces:

- `form-fields.pdf` — PDF with interactive fields added.
- `form-fields.csv` — CSV of detected fields and positions.
- `form-field-generator.py` — Script used for field generation.

***

### Create Markup for Verification

Generate an annotated PDF showing detected boxes, aiding manual verification:

```
flyfield --input-pdf form.pdf --markup
```

***

### Fill Form Fields with CSV Data

Populate form fields from a CSV file containing mappings of codes to values:

```
flyfield --input-pdf form-fields.pdf --fill data.csv
```

***

### Capture Filled Form Data

Export filled data to CSV, enabling review or re-use:

```
flyfield --input-pdf filled-form.pdf --capture
```

***

## Combining Options

You can combine multiple options, for example:

```
flyfield --input-pdf form.pdf --markup --fields
```

**Note:** The `--fields` step may be slow on large PDFs; reuse cached results when possible.

***

## Customizing Generated Scripts

Generated Python scripts (`field-generator.py` and `filler.py`) are editable:

- Modify field naming, placement, or attributes.
- Apply custom formatting or logic.
- Rerun scripts manually to apply changes.

***

!!! Tip "Tips and Troubleshooting"

	- Always work on a **copy** of the original PDF to prevent data loss.
	- Save time by avoiding redundant extraction; reuse CSVs and PDFs.
	- Use `--debug` to produce detailed logs and CSV snapshots.
	- flyfield supports only **vector PDFs** with clear white box placeholders.
	- Ensure CSV files are UTF-8 encoded and contain at least two columns: `code` and `fill`.

***

For additional guidance, see:

- [Quick Start Guide](quick_start.md)
- [Worked Example](example.md)

***

This guide empowers users to utilize flyfield’s CLI for reliable automated PDF form workflows.

***
