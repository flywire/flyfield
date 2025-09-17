# Quick Start Guide

This quick start guide helps you get up and running with **flyfield** efficiently.

---

### What You Need (Prerequisites)

Before you begin using **flyfield**, you need the following:

- **Familiarity with Command Line**

You should know how to open and use the terminal (Linux/macOS) or command prompt/PowerShell (Windows) to run commands. This is necessary to execute flyfield commands properly.

- **Python Installation**

flyfield requires Python 3.9 or later. To check your Python version, open a terminal or command prompt and run:

```
python --version
```

If Python is not installed or if the version is below 3.9, download and install the latest Python version from [python.org](https://www.python.org/downloads/). Follow the installer instructions suitable for your operating system.

- **Installing flyfield**

The recommended method to install flyfield is using `pipx`, which allows you to install and run Python CLI tools in isolated environments. To install pipx (if you don't have it), run:

```
python -m pip install --user pipx
python -m pipx ensurepath
```

Once pipx is installed, install flyfield by running:

```
pipx install flyfield
```

After installation, verify that flyfield is correctly installed by running:

```
flyfield --version
```

This should print the installed version number without errors.

- **PDF and Data Files**
Have a copy of the PDF form you want to automate, for example:

```
Trust-tax-return-2024.pdf
```

Also prepare or obtain a CSV file containing your field codes and corresponding values in a `code,fill` column format, for example:

```
example-fields-filled-capture.csv
```

---

!!! Note "Typical Workflow Overview"

	1. Make a copy of your original PDF (keep it safe)
	2. Generate a markup PDF that shows detected field boxes to verify visually
	3. Extract and generate interactive form fields on selected pages
	4. Fill the PDF fields using data from your CSV file
	5. Capture filled form data back into CSV for review or reuse

---

!!! Tip "Useful Tips"

	- Ensure your CSV files are UTF-8 encoded and properly formatted
	- Use the `--debug` flag for more detailed logs if encountering issues

---

### Want More?

For a detailed, step-by-step walkthrough with real-world examples and commands, see the [Worked Example](example.md).

---

This streamlined guide gives you the essentials to start using **flyfield** safely and confidently, pointing to deeper tutorial content for extended learning.
