# Installation Guide for flyfield

This guide provides detailed instructions to install and prepare **flyfield** on your system.

### Prerequisites

- Python 3.9 or later installed
- Access to a command-line interface (Command Prompt, PowerShell, or Terminal)

***

## Installation Methods

### 1. Recommended: Install via pipx

[`pipx`](https://pypa.github.io/pipx/) installs Python CLI programs in isolated environments and avoids dependency conflicts.

To install **flyfield**:

```
pipx install flyfield
```

After installation, verify it works:

```
flyfield --version
```

You should see the installed version number.

***

### 2. Alternative: Install via pip in a Virtual Environment

1. Create and activate a virtual environment:

- On macOS/Linux:

```
python3 -m venv env
source env/bin/activate
```

- On Windows:

```
python -m venv env
.\env\Scripts\activate
```

2. Install flyfield:
```
pip install flyfield
```

3. Verify installation:
```
flyfield --version
```

***

## Development Installation (for contributors)

For contributors or advanced users wanting editable installs:

1. Clone the repository:
```
git clone https://github.com/flywire/flyfield_docs.git
cd flyfield_docs
```

2. Install with dev dependencies:
```
pip install -e .[dev]
```

3. Run the test suite:
```
pytest
```

***

## Troubleshooting

- **flyfield command not found after pipx install**
Run:

```
pipx ensurepath
```

Then restart your terminal.
- **Permission errors on pip install**
Use:

```
pip install --user flyfield
```

- **Old pip version causes issues**
Upgrade pip:

```
pip install --upgrade pip
```

- **Dependencies required**
flyfield depends on:
    - [PyMuPDF](https://pymupdf.readthedocs.io/) for parsing and extraction
    - [PyPDFForm](https://pypi.org/project/pypdfform/) for adding interactive form fields

***
