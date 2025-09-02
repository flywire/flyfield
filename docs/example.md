# Worked Example: Automating a Tax Return PDF Form

This detailed step-by-step example demonstrates how to use **flyfield** for extracting, marking up, generating form fields, filling, and capturing data from a real complex form: the Australian Tax Office Trust Tax Return 2024. It starts with copying the original PDF to a new working filename to safeguard the source and uses this filename as the base for every output file in the workflow.

## Prerequisites 5

- **flyfield** installed and operational.
- Source PDF: [Trust-tax-return-2024.pdf](assets/Trust-tax-return-2024.pdf).
- CSV file containing field codes and associated data: [**example-fields-filled-capture.csv**](assets/example-fields-filled-capture.csv)

??? example "View CSV contents"

    ```
    --8<-- "docs/assets/example-fields-filled-capture.csv"
    ```

<br>

## Workflow Overview

Once the original PDF is copied, all subsequent steps work exclusively on the new working file. Each time flyfield is run without the `--input-csv FILE` option, it automatically extracts white box fields and generates the CSV, so a dedicated extraction step is not needed.

The five core automation steps are:

1. Copy the original PDF to a working filename.
2. Generate interactive form fields.
3. Create a marked-up PDF to verify field positions.
4. Fill form fields using CSV data.
5. Capture filled form data back into a CSV for editing or reuse.

## Step 1: Copy the Source PDF

Begin by copying the original tax return PDF:

```sh
copy Trust-tax-return-2024.pdf example.pdf
```

Outputs:

- `example.pdf` — copied working PDF file.

This protects the integrity of the original form by avoiding accidental overwrites or corruption. It also keeps all outputs organized and traceable by using the base filename `example.pdf`.

## Step 2: Generate Interactive PDF Form Fields

```sh
flyfield --input-pdf example.pdf --fields
```

Outputs:

- `example-fields.pdf` — form with interactive fields.
- `example-field-generator.py` — script used to generate fields.
- `example.csv` — updated field codes and positions.


## Step 3: Create Markup PDF for Verification

```sh
flyfield --input-pdf example.pdf --markup
```

Outputs:

- `example-markup.pdf` — visualizes all detected fields and codes for easy validation against the original.
- `example.csv` — updated field codes and positions.


## Step 4: Fill Form Fields With CSV Data

```sh
flyfield --input-pdf example-fields.pdf --input-csv example-fields-filled-capture.csv --fill
```

Outputs:

- `example-fields-filled.pdf` — form with CSV data filled in.
- `example-fields-filler.py` — script used for filling.


## Step 5: Capture Data From Filled Form

```sh
flyfield --input-pdf example-fields-filled.pdf --capture
```

Outputs:

- `example-fields-filled-capture.csv` — exported filled values for editing or reuse.


## Notes and Tips

- Starting with a copy safeguards the original form and simplifies file management.
- Running flyfield generally triggers automatic extraction unless a CSV input file is provided.
- Minimize repeated use of `--fields` on large PDFs because field generation can be slow.
- Ensure CSV fields align perfectly before filling.
- Use the markup step regularly to confirm all field detection and spot issues early.
- The generated Python scripts enable advanced users to customize field generation and data filling.
