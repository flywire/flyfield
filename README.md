# flyfield

A tool to automatically detect white boxes in PDFs and convert them into interactive, automated form fields—aimed at users and developers looking to streamline PDF form workflows.

---

## Overview

**flyfield** is a Python library and command-line tool designed to automate the conversion of white box placeholders within PDFs into fully interactive form fields. This enables users and developers to analyze form layouts, generate fillable fields, fill forms programmatically using CSV data, and capture filled data for further use.

Powered by [PyMuPDF](https://pymupdf.readthedocs.io) and [PyPDFForm](https://pypdfform.readthedocs.io), flyfield provides a modular, extensible solution for reliable PDF form automation.

---

## Key Features

- **White box detection:** Precisely extract white box regions as potential form fields from vector PDFs.
- **Layout analysis:** Group extracted fields by page, line, and block with flexible gap detection.
- **Form field generation:** Automatically produce Python scripts to create interactive PDF form fields aligned with detected boxes.
- **Markup visualization:** Generate annotated PDFs marking detected fields for verification.
- **Form filling and capture:** Fill PDF forms programmatically from CSV data and extract filled data into CSV format.
- **CLI integration:** User-friendly command-line interface to orchestrate workflows from extraction to data capture.
- **Open Source and Extensible:** Easily customize and extend for specific PDF processing needs.

---

## Installation

For isolated installation, use [pipx](https://pipxproject.github.io/pipx/):

```

pipx install flyfield

```

Verify the installed version:

```

flyfield --version

```

Alternatively, install with `pip`:

```

pip install flyfield

```

---

## Usage

Execute commands against PDF files as needed:

```

flyfield --input-pdf myfile.pdf --markup

```

Common options:

- `--markup` → Generate a marked-up PDF showing detected white boxes.
- `--fields` → Generate and run scripts to add interactive form fields.
- `--fill` → Fill form fields using CSV data.
- `--capture` → Extract filled form data back to CSV.
- `--input-csv` → Provide CSV input for field data, bypassing extraction.
- `--debug` → Enable verbose debug output.

Example workflow:

```

flyfield --input-pdf form_template.pdf --markup --fields
flyfield --input-pdf form_template-fields.pdf --input-csv form_template.csv --fill
flyfield --input-pdf form_template-filled.pdf --capture

```

---

## For Developers

Clone the repository and install development dependencies:

```

git clone https://github.com/flywire/flyfield.git
cd flyfield
pip install -e .[dev]

```

Run the test suite with coverage enabled:

```

tox

```

The project is modular with separate components, including:

- `extract` for box detection
- `layout` for field grouping and filtering
- `markup_and_fields` for field generation and markup
- `io_utils` for data input/output
- `utils` for utility functions

Get CLI help with:

```

python -m flyfield.cli --help

```

---

## License

Licensed under the **GNU General Public License v3.0 or later** (GPL-3.0-or-later). See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please open issues to report bugs or request features, and submit pull requests with tests and documentation improvements.

---

## Acknowledgements

- Built using [PyMuPDF](https://pymupdf.readthedocs.io) for PDF handling.
- Uses [PyPDFForm](https://pypdfform.readthedocs.io) for interactive form creation.
- Inspired by the need for robust automation of PDF workflows involving white boxed form fields.

---
