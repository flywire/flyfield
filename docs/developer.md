# Developer Guide for flyfield

This guide provides technical details on the internal architecture of **flyfield**, instructions for setting up a development environment, and guidelines for contributing or customizing the project.

## Architecture Overview

flyfield is implemented in Python and consists of the following key components:

- **PDF Processing Layer**
Utilizes [PyMuPDF](https://pymupdf.readthedocs.io) for parsing PDFs and [PyPDFForm](https://pypi.org/project/pdfform/) for creating and manipulating interactive PDF form fields.
- **Extraction Module**
Scans vector PDF graphics to detect white box placeholders representing form fields.
- **Filtering and Grouping Logic**
Applies size, colour, and structural heuristics to filter out noise and cluster valid boxes into organized groups.
- **Field Generation and Filling**
Creates interactive PDF form fields and fills them programmatically using CSV data.
- **Script Generation**
Produces reusable standalone Python scripts to add or fill forms, allowing for advanced customization.

## Development Environment Setup

For safe development and testing:

- Always work with **copied PDFs** to avoid overwriting original documents.
- The repository contains:
    - `flyfield/` — core source code
    - `tests/` — unit and integration tests
    - `docs/` — documentation files

### Prerequisites

- Python 3.9 or later
- Git for version control
- Virtual environment tools (e.g. `venv`, `virtualenv`)
- Python dependencies specified in `requirements.txt`

### Installing and Running

```
git clone https://github.com/flywire/flyfield_docs.git
cd flyfield_docs
python -m venv env
source env/bin/activate   # or .\env\Scripts\activate on Windows
pip install -r requirements.txt
```

Run tests with:

```
pytest
```

The test suite covers extraction, filtering, field generation, filling, and data capture workflows.

## Customization Points

Areas commonly extended by developers include:

- **Filtering Criteria**
Adjust detection parameters for box size, colour, and positioning in extraction modules.
- **Field Naming Schemes**
Customize how field codes are assigned to match external system requirements.
- **Script Templates**
Modify the templates for generated Python scripts to handle special layouts or behaviours.

## Contribution Guidelines

- Use feature branches when working on new changes.
- Adhere to PEP 8 style guidelines and include docstrings for clarity.
- Write tests for new features or bug fixes.
- Submit pull requests with descriptive titles and explanations.

## Debugging and Logging

- Enable verbosity with the `--debug` CLI flag for detailed logs and intermediate files.
- For development, adjust Python's logging to DEBUG level as needed.

## Resources

- [API Documentation](api.md) — detailed function references
- [User Guide](usage.md) — CLI usage and workflows
- [Worked Example](example.md) — complete automation scenario

***

Thank you for contributing to flyfield! Your efforts help improve and extend the tool.

Happy coding and PDF automation!

***
