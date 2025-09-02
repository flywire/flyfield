# Frequently Asked Questions (FAQ)

This FAQ section addresses common questions and troubleshooting tips for **flyfield** users.

---

## Installation Issues

### Q: I successfully installed flyfield using pipx but the command does not run. What should I do?

**A:** This often occurs because the directory where pipx installs executables is not in your system's `PATH`. To fix:

1. Run the command:
```

pipx ensurepath

```
2. Restart your terminal or command prompt to apply the `PATH` changes.  
3. Verify the installation by running:
```

flyfield --help

```
Make sure you are running the command in the same user context where pipx is installed.

---

## Usage and Workflow


### Q: How do I check which version of flyfield I have?

**A:** Use the command:

```
flyfield --version
```

It will print the currently installed version.

###Q: How do I process only certain pages of a PDF?

**A:** Use the `--pdf-pages` option with a comma-separated list of pages or ranges, like `"1-3,5,7-10"`.

### Q: Do I need to run a separate extract step before generating fields?

**A:** Extraction occurs automatically on input PDFs unless you supply an input CSV. Usually, a separate extract step is not needed.

### Q: How can I speed up processing when dealing with large PDFs?

**A:** Running `--fields` is slow on large PDFs. Run it once per version and reuse generated CSVs and markup PDFs to speed up workflows.

### Q: The markup PDF shows fewer fields than expected. Why?

**A:** Only pure white vector boxes within size thresholds are detected. Colored or shaded boxes, scanned PDFs, or boxes outside size limits will be missed. Use `--debug` to troubleshoot.

### Q: Why should I copy the source PDF before running commands?

**A:** Working on a copy prevents overwriting or corrupting your original documents and helps keep outputs organized.

---

## Advanced Customization

### Q: Can I customize field names or placement?

**A:** Yes. The Python scripts generated (`*-field-generator.py` and `*-fields-filler.py`) are editable. You can:

- Change field naming schemes.  
- Adjust coordinates and sizes for fields.  
- Add special logic to merge or split fields.

Run the edited scripts manually with Python to regenerate PDFs as needed.

---

## Troubleshooting

### Q: My filled PDF from `--fill` does not display data correctly in all viewers. What can I do?

**A:** Compatibility varies between PDF viewers. For best results:

- Use Adobe Acrobat or well-supported PDF readers.  
- Avoid complex PDF overlays or security settings that might obscure fields.  
- Flatten PDF if needed using external tools after filling.

### Q: How do I extract data from a filled PDF form?

**A:** Use the `--capture` option:

```

flyfield --input-pdf filled-form.pdf --capture

```

This generates a CSV with all filled fields and their values for editing or further processing.

---

## General Questions

### Q: Does flyfield work on scanned PDFs?

**A:** No. flyfield requires PDFs generated with **vector graphics**. Scanned images or raster PDFs are not supported.

### Q: Is there support for PDFs with text boxes instead of graphical white boxes?

**A:** flyfield focuses on detecting visible rectangular white boxes as placeholders, not interactive text boxes already embedded.

---

For further assistance, refer to the [User Guide](usage.md) or [Worked Example](example.md).
