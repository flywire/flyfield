# Introduction to flyfield

Welcome to the **flyfield** documentation! This toolset helps automate the creation, filling, and data extraction of interactive PDF forms that feature white box placeholders.

---

## What is flyfield?

flyfield is a Python library and command-line interface (CLI) utility designed to:

- Detect and extract white rectangular placeholders in vector PDFs.  
- Generate interactive form fields aligned precisely with those white boxes.  
- Fill PDF form fields programmatically using CSV data files.  
- Capture filled form data back into CSV for editing or reuse.

The project aims to simplify digitizing paper-like forms into machine-readable, automated workflows without manual data entry.

---

## Who is this for?

- Developers who need to automate PDF form workflows involving white box placeholders.  
- Workflow engineers who integrate PDF form interaction with spreadsheets or databases.  
- Technical teams digitizing complex tax, finance, or administrative forms.

---

## Why Use flyfield?

- **Speed up form processing** by automating field detection and filling.  
- **Reduce human data entry errors** through programmatic CSV integration.  
- **Simplify workflows** involving multiple PA forms or batch processing.  
- **Open-source and extensible** with modifiable Python scripts generated during CLI operations.

---

## Key Features

- **Automatic Detection and Extraction** of white box fields runs automatically unless input CSV data is provided.  
- **Visual Markup PDFs** for easy verification of detected fields.  
- **Python Script Generation** for advanced customization of form generation and filling.  
- **CSV-Based Data Exchange** to integrate with spreadsheets, databases, or downstream systems.

---

## How to Use This Documentation

- Start with the [Quick Start Guide](quick_start.md) to set up and essential commands.  
- Explore the [Worked Example](example.md) for detailed real-world usage.  
- Dive into the [User Guide](usage.md) for CLI commands and options.  
- Use the [API Documentation](api.md) for programmatic access beyond CLI.  
- Check [FAQ](faq.md) for common questions and troubleshooting. 
- For internal architecture and contributions, see the [Developer Guide](developer.md). 

---

We hope **flyfield** makes managing interactive PDF forms simpler and more efficient for your projects.

Happy automating!
