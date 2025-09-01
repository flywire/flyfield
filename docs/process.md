# Processing Workflow of flyfield

This document provides a detailed overview of the step-by-step processing workflow that **flyfield** follows to detect, generate, fill, and capture PDF form fields based on white box placeholders.

---

## Overview

flyfield automates the conversion of static white box PDF forms into interactive, fillable documents through a multi-stage process:

1. **Extraction of White Boxes**  
2. **Field Filtering and Grouping**  
3. **Interactive Field Generation**  
4. **Form Field Filling**  
5. **Data Capture from Filled Forms**

---

## Step 1: Extraction of White Boxes

- Extraction runs automatically on input PDFs without an input CSV. You usually do not need a separate extraction step.  
- Vector graphics in the PDF are analyzed via PyMuPDF to find white rectangular placeholders.  
- Coordinates, pages, and unique field codes are recorded and output as a CSV.

---

## Step 2: Field Filtering and Grouping

- Raw extracted boxes may include noise; filtering removes boxes that do not fit expected dimensions or colors.  
- Grouping clusters related fields by proximity or page, helping organize form layout logically.  
- This stage is crucial to ensure fields correspond accurately to the intended form elements.

---

## Step 3: Interactive Field Generation

- Fields are generated only once per PDF version. This is computationally slower on large PDFs, so avoid repeated runs.  
- Interactive form fields are created based on the filtered field data (via PyPDFForm).  
- A marked-up PDF version is optionally produced to visualize field placement for verification.

---

## Step 4: Filling Form Fields

- PDF form fields can be programmatically filled by supplying a CSV file containing field codes and fill values.  
- Filling is done by running the generated fill scripts or via the CLI’s `--fill` option.  
- Output is a filled PDF form ready for use or review.

---

## Step 5: Data Capture from Filled Forms

- Filled PDF forms can be parsed to extract entered values back into CSV format.  
- This enables editing, auditing, or reusing the data in spreadsheets or databases.  
- The capture process reads interactive fields and maps their names and values into rows/columns.

---

## Additional Considerations

- The process requires **vector PDFs** with clear white box placeholders; scanned images or rasterized PDFs are unsupported.  
- Field extraction and generation steps may be time-consuming on large or complex PDFs; caching intermediate results is recommended.  
- Generated Python scripts provide hooks for customization at multiple stages of the workflow.

---

## Block Diagram

```

PDF Input → [White Box Extraction] → [Filtering/Grouping] → Field Generation → Markup → Filling → Data Capture

```

---

This workflow allows effective automation of PDF form processing, reducing manual effort and enabling digital document workflows.

For practical examples, see the [Worked Example](example.md) and related guides.
