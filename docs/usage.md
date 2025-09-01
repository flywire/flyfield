# User Guide and CLI Reference for flyfield

This guide covers all major command-line options, typical workflows, and tips for using **flyfield** effectively.

---

## Basic CLI Command Structure

```

flyfield [options]

```

---

## Commonly Used Options

| Option               | Description                                      |
|----------------------|--------------------------------------------------|
| `--version` | Show the tool's version and exit                          |
| `--input-pdf FILE`   | Specify the input PDF filename                   |
| `--pdf-pages PAGES`  | Page numbers or ranges to process, e.g. "1-3,5,7"|
| `--input-csv FILE`   | Specify CSV file for loading data or blocks      |
| `--markup`           | Generate a PDF with visual markup of fields      |
| `--fields`           | Generate and run script to add interactive fields|
| `--fill`             | Generate and run script to fill fields from CSV  |
| `--capture`          | Extract filled form data back into a CSV         |
| `--debug`            | Output additional debug files                    |
| `-h, --help`         | Show help message and exit                       |

---

## Typical Workflow Examples

### Generate fields and extract data automatically

Extraction runs automatically if no CSV is provided.

```

flyfield --input-pdf form.pdf --fields

```

- Produces `form-fields.pdf`, `form-field-generator.py`, and extracted `form.csv`.

### Add interactive fields to PDF

```

flyfield --input-pdf form.pdf --fields

```

- Warning: This can be slow for large PDFs. Run once per PDF version to cache.

### Create markup PDF to verify field locations

```

flyfield --input-pdf form.pdf --markup

```

- Generates `form-markup.pdf` for visual verification.

### Fill PDF form using CSV data

```

flyfield --input-pdf form-fields.pdf --input-csv data.csv --fill

```

- Fills fields based on CSV `code,fill` mappings.

### Capture filled data back to CSV

```

flyfield --input-pdf form-fields-filled.pdf --capture

```

- Saves filled data to CSV for reuse or editing.

---

## Options Combination

- You can combine options in a single command. For example:

```

flyfield --input-pdf form.pdf --markup --fields

```

- Note the `--fields` process can be slow on large PDFs; consider caching outputs.

---

## Editing Generated Scripts

- The `*-field-generator.py` and `*-fields-filler.py` scripts generated in field and fill steps can be edited to customize field placement, naming, or filling logic.
- After editing, run the scripts manually with Python to generate the desired PDF output.

---

## Tips and Troubleshooting

- Work with copied PDFs to safeguard originals.  
- Avoid rerunning `--fields` repeatedly; prefer reuse of CSV and markup outputs.  
- Use `--debug` for detailed logs.  
- The tool supports PDFs with vector graphics and strict white box fields; scanned PDFs are not supported.  
- Ensure CSV files are UTF-8 encoded and follow the `code, fill` format.

---

This guide should help users leverage the full power of flyfield for automated PDF form processing.

---

For additional details, refer to the [Worked Example](example.md) and [Quick Start Guide](quick_start.md).
