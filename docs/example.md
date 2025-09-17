# Worked Example: Automating a Tax Return PDF Form

This detailed step-by-step example demonstrates how to use **flyfield** for extracting, marking up, generating form fields, filling, and capturing data from a real complex form. It starts with copying the original PDF to a new working filename to safeguard the source and uses this filename as the base for every output file in the workflow.

***

## Prerequisites

Before following this example, you should be familiar with the **[Quick Start Guide](quick_start.md)**.

- **flyfield** installed and operational
- Source PDF: [Trust-tax-return-2024.pdf](assets/Trust-tax-return-2024.pdf)
- CSV file containing field codes and associated data: [example-fields-filled-capture.csv](assets/example-fields-filled-capture.csv)

??? example "Take a look at the CSV contents:"

    ```csv
    --8<-- "docs/assets/example-fields-filled-capture.csv"
    ```


***

!!! Note "Workflow Overview"

	1. Copy the original PDF to a working filename
	1. Create a marked-up PDF to verify field positions
	1. Generate interactive form fields
	1. Fill form fields using CSV data
	1. Capture filled form data back into a CSV for editing or reuse

## Step 1: Copy the Source PDF

Begin by copying the original tax return PDF:

```
copy Trust-tax-return-2024.pdf example.pdf
```

**Outputs:**

- `example.pdf` — copied working PDF file.

This protects the integrity of the original form by avoiding accidental overwrites or corruption. It also keeps all outputs organized and traceable by using a convenient base filename `example.pdf`.

***

## Step 2: Create Markup PDF for Verification

Create a visual markup of the fields for manual verification:

```
flyfield --input-pdf example.pdf --markup
```

**Outputs:**

- `example-markup.pdf` — PDF showing detected field boxes and codes.
- `example.csv` — updated field codes and metadata.

Review this file carefully to validate the correctness and alignment of detected form fields against the original.

***

## Step 3: Generate Interactive PDF Form Fields

The `--fields` option tells flyfield to detect placeholder boxes and add interactive fields.

On long documents (e.g. 20 pages), this process can be slow.

**Important best-practice:**

- Always process the full PDF to preserve consistent field codes that embed the original page number.
- Do **not** physically extract and save partial page PDFs before running — doing so changes the page numbering context, breaking reproducibility.

If you want to **limit processing** while preserving field code consistency, use the `--pdf-pages` option. This processes only selected pages but retains original numbering.

Example: restrict processing to pages 1, 2, 4–6, 11, 12, and 14:

Run the command:

```
flyfield --input-pdf example.pdf --pdf-pages="1,2,4-6,11,12,14" --fields
```

**Outputs:**

- `example-fields.pdf` — PDF with interactive form fields added
- `example-field-generator.py` — Python script used to generate those fields
- `example.csv` — extracted field codes and metadata

!!! tip "**Advanced User Bonus: Editing the Python Field Generator Script**"

	This generated Python script can be modified to customize or unify fields, for instance to link repeated field entries across pages.

	**Example:** Linking the Tax File Number (TFN) fields at the top of page 5 and page 1.

	1. Open `example-field-generator.py` in a text editor
	2. Locate the code block that defines fields at the top of page 5
	3. Change each field name in that section from something like`"5-1-1"`to reference the page 1 TFN field names, e.g., `"1-3-1"`, `"1-3-2"`, `"1-3-3"`
	4. Save your changes
	5. Regenerate the filled PDF by running:
	```
	python example-field-generator.py
	```

	This rebuilds `example-fields.pdf` with linked fields, so entering the TFN once will automatically update it on both pages.

***

## Step 4: Fill Form Fields With CSV Data

After confirming fields, supply a CSV file containing at least two columns, `code` and `fill`, to fill the interactive form fields with your CSV data:

```
flyfield --input-pdf example-fields.pdf --fill example-fields-filled-capture.csv
```

**Outputs:**

- `example-fields-filled.pdf` — filled PDF form with CSV data inserted
- `example-fields-filler.py` — Python script used to perform filling (editable for customization)

***

## Step 5: Capture Data From Filled Form

Capture the filled form data back into a CSV file for review or reuse:

```
flyfield --input-pdf example-fields-filled.pdf --capture
```

**Outputs:**

- `example-fields-filled-capture.csv` — extracted form data, which can be edited and reused.

***

!!! Note "Demonstrated"

	- Working safely with a **copy** of the original PDF to protect the source
	- Validating detected form fields visually by generating a **markup PDF**
	- Improving efficiency by **generating fields only on required pages**
	- Tailoring workflows by **direct editing and rerunning the generated Python field generation script**
	- Managing data consistency by **reusing CSV data** for filling and capturing

***

This example provides a practical, real-world automation workflow for PDF form processing using flyfield. It assumes basic familiarity covered by the Quick Start Guide, guiding users through safely and effectively managing complex tax return forms.
