# flyfield

Transform static white box PDF forms into interactive forms for fast automation.

***
## Overview

**flyfield** automatically analyzes static PDF forms, creates fillable fields, marks field locations for verification, fills and extracts data, and seamlessly converts money values between PDF text and spreadsheet/database numeric formats.

***
## Key Features

- Generate interactive form fields and marked-up PDFs from PDF white box forms
- Fill and export form data using CSV files
- Seamlessly convert money values between PDF text and CSV number formats
- Simple command-line interface for efficient workflows
- Open source and flexible for diverse PDF automation needs

***
## Installation

Install with pipx:

```
pipx install flyfield
```

Check version:

```
flyfield --version
```

Or install via pip:

```
pip install flyfield
```


***
## Usage

Run commands on PDF files as needed:

```
flyfield --input-pdf myfile.pdf --markup
```


### Options:

- `--markup` Generate a PDF highlighting white boxes
- `--fields` Add interactive form fields
- `--fill` Fill form fields using data from a CSV file
- `--capture` Export filled form data to CSV
- `--input-csv` Load field data from a CSV instead of extracting
- `--debug` Show detailed processing logs


### Example workflow:

```
flyfield --input-pdf form.pdf --markup --fields  
flyfield --input-pdf form-fields.pdf --input-csv form.csv --fill form-fill.csv  
flyfield --input-pdf form-filled.pdf --capture  
```


***
## For Developers

Clone and install development tools:

```
git clone https://github.com/flywire/flyfield.git  
cd flyfield  
pip install -e .[dev]  
```

Run tests:

```
tox  
```

Modules:

- `extract` — box detection
- `layout` — analyse, group and filter fields
- `markup_and_fields` — generate fields and markings
- `io_utils` — data I/O
- `utils` — utility functions

For CLI help:

```
python -m flyfield.cli --help  
```


***
## License

GNU GPL v3.0 or later. See [LICENSE](LICENSE).

***
## Contributing

Contributions welcome via issues and pull requests.

***
## Acknowledgements

- Powered by [PyMuPDF](https://pymupdf.readthedocs.io).
- Uses [PyPDFForm](https://pypdfform.readthedocs.io).
- Designed to simplify workflows involving white boxed PDF form fields.

***
