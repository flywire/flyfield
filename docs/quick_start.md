# Quick Start Guide for flyfield

This quick start guide provides essential commands and workflow steps to begin using **flyfield** for PDF form automation.

---

## Prerequisites

- Python 3.8 or above installed
- flyfield package installed (recommended via pipx):

```

pipx install flyfield

```

After installation, verify your installed version by running:

```

flyfield --version

```

---

## Basic Workflow

The key steps you'll typically perform using a copied PDF working file:

### 1. Copy the Source PDF (Recommended)

Begin by copying your original PDF to avoid overwriting:

```

copy your-form.pdf working-form.pdf

```

Outputs:
- `working-form.pdf` — copied working PDF file.

This protects the integrity of the original form and organizes output files by using the working copy.

---

### 2. Generate Interactive PDF Form Fields

Extraction of white box fields runs automatically unless an input CSV is provided.

```

flyfield --input-pdf working-form.pdf --fields

```

Outputs:
- `working-form-fields.pdf` — form with interactive fields.
- `working-form-field-generator.py` — script used for generation.
- `working-form.csv` — detected field codes and positions.

*Tip:* The generated script can be customized if needed before running.

---

### 3. Create Markup PDF for Verification

This step is optional but recommended to visually verify detected fields. The `--pdf-pages` option limits processing to specific pages:

```

flyfield --input-pdf working-form.pdf --pdf-pages "1,3-4" --markup

```

Outputs:
- `working-form-markup.pdf` — PDF annotated with detected fields and codes.

Use this to confirm field detection accuracy and troubleshoot issues early.

---

### 4. Fill Form Fields Using CSV Data

Fill form fields with CSV data which must have `code` and `fill` columns:

```

flyfield --input-pdf working-form-fields.pdf --input-csv data.csv --fill

```

Outputs:
- `working-form-fields-filled.pdf` — filled PDF form.
- `working-form-fields-filler.py` — script used for filling.

---

### 5. Capture Data From Filled Form to CSV

Extract values entered or filled in the PDF form back to CSV for editing or reuse:

```

flyfield --input-pdf working-form-fields-filled.pdf --capture

```

Outputs:
- `working-form-fields-filled-capture.csv` — CSV containing filled form data.

---

## Additional Tips

- Always work with a copied working PDF file to safeguard originals.
- Avoid re-running `--fields` repeatedly on large PDFs; reuse generated CSV and markup outputs.
- Use the `--debug` flag for detailed logs during troubleshooting.
- Customize the generated Python scripts as needed for advanced workflows.
- Keep backups of your PDFs and CSV files to prevent accidental overwrite.
- Only vector PDFs with white boxes are supported; scanned PDFs are not compatible.

---

## Need More Help?

Start with the [Worked Example](example.md) for a practical guided workflow.  
See the full [User Guide](usage.md) for detailed commands and options.

---

This quick start gives you the foundation to efficiently automate your white box PDF forms using flyfield.
