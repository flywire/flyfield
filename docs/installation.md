# Installation Guide for flyfield

This guide explains how to install **flyfield** and get it ready for use on your system.

---

## Prerequisites

- Python version 3.8 or higher  
- Access to a command-line terminal (Command Prompt, PowerShell, Terminal, etc.)

---

## Installation Methods

### 1. Recommended: Install via `pipx`

[`pipx`](https://pypa.github.io/pipx/) allows installing Python applications in isolated environments, avoiding conflicts.

To install flyfield using pipx, run:

```

pipx install flyfield

```

After installation, the `flyfield` command will be available globally.

---

### 2. Alternative: Install via `pip` in a Virtual Environment

1. Create and activate a virtual environment (optional but recommended):

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

2. Install flyfield with pip:

```

pip install flyfield

```

3. Verify installation:

- To verify the installed version of flyfield:

```
flyfield --version
```


---

## Development Installation (for contributors)

If you want to develop or contribute to the project:

1. Clone the repository:

```

git clone https://github.com/flywire/flyfield_docs.git
cd flyfield_docs

```

2. Install with development dependencies:

```

pip install -e .[dev]

```

3. Run tests with pytest:

```

pytest

```

---

## Troubleshooting

- If the `flyfield` command is not found after using `pipx`, run:

```

pipx ensurepath

```

Then restart your terminal.

- If you encounter permission errors during installation, try adding `--user` to your pip install command:

```

pip install --user flyfield

```

- Always keep your pip updated:

```

pip install --upgrade pip

```
