# Developer Guide for flyfield

This guide provides technical insight into the internal architecture of **flyfield**, instructions for setting up a development environment, and guidelines for contributing or customizing the project.

---

## Architecture Overview

flyfield is primarily implemented in Python and builds upon the following core components:

- **PDF Processing Layer**:  
  Uses libraries like PyMuPDF for PDF parsing and PyPDFForm for creating interactive form fields.

- **Extraction Module**:  
  Detects white box placeholders by analyzing vector graphics content in PDFs.

- **Filtering and Grouping Logic**:  
  Applies heuristics to filter and cluster detected white boxes to form meaningful fields.

- **Field Generation and Filling**:  
  Generates interactive fields and fills them programmatically based on CSV data.

- **Script Generation**:  
  Emits Python scripts for custom field creation and filling workflows, allowing advanced customization.

---

## Development Setup

- Always start testing workflows with a copied PDF to prevent overwriting originals.  
- Code repository contains source in `flyfield/` directory; generated scripts and docs are separate.

### Prerequisites

- Python 3.8 or higher  
- Git  
- Virtual environment tool (`venv`, `virtualenv`, or similar)  
- Required Python dependencies (see `requirements.txt`)

---

### Cloning and Installation

```

git clone https://github.com/flywire/flyfield_docs.git
cd flyfield_docs
python -m venv env
source env/bin/activate   \# or .\env\Scripts\activate on Windows
pip install -r requirements.txt

```

---

## Running Tests

To run the automated test suite using `pytest`:

```

pytest

```

Tests cover core extraction, filtering, field generation, and filling logic.

---

## Code Structure

- `flyfield/` — core source code  
- `scripts/` — generated scripts for field creation and filling  
- `tests/` — unit and integration tests  
- `docs/` — documentation markdown files

---

## Customization Points

- **Filtering Criteria**: Adjust size, color, and position thresholds in extraction.py or filtering modules.  
- **Field Naming**: Modify logic generating field codes for compatibility with external systems.  
- **Script Templates**: Customize generated Python script templates in the `templates/` folder.

---

## Contribution Guidelines

- Fork the repository and create a feature branch.  
- Follow PEP 8 coding style and add meaningful docstrings.  
- Add or update tests for any new features or bug fixes.  
- Submit a pull request with clear descriptions of changes.

---

## Debugging and Logging

Use the `--debug` flags in the CLI or set the `logging` module level to debug when developing.

---

## Resources

- [API Documentation](api.md) for function-level details.  
- [User Guide](usage.md) for CLI-focused instructions.  
- [Worked Example](example.md) for real case workflows.

---

Thank you for your interest in contributing to flyfield!

Happy coding and improving PDF form automation.
