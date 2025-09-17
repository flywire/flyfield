# Frequently Asked Questions (FAQ)

This section addresses common questions and provides troubleshooting tips for **flyfield** users.

***

## Installation Issues

### Q: I installed flyfield using pipx, but the command is not recognized. What should I do?

**A:** This usually happens if the pipx install directory is not in your system's PATH environment variable. To fix:

1. Run the command:
```
pipx ensurepath
```

2. Restart your terminal or command prompt.
3. Verify by running:
```
flyfield --help
```

Ensure you run the command in the same user context where pipx was installed.

***

## Usage & Workflow

### Q: How can I check which version of flyfield I have installed?

**A:** Use the command:

```
flyfield --version
```

This prints the installed version.

***

### Q: How do I speed up processing on large PDFs?

**A:** The `--fields` step (field generation) can be slow. Best practices:

- Run `--fields` only once per PDF version.
- Reuse cached CSV and markup PDF files for subsequent steps.

***

### Q: My field codes are inconsistent when extracting from a subset of pages. Why?

**A:** Field codes embed page number context. Always run extraction on the full PDF to maintain consistent codes. Use `--pdf-pages` to limit processing without renumbering.

***

### Q: Do I need to run a separate extraction step before generating fields?

**A:** No, extraction runs automatically unless you provide `--input-csv`, which skips it.

***

### Q: Why are some expected fields missing from markup output?

**A:** flyfield detects only pure white vector boxes within configured size ranges.

Possible causes for missing fields:

- Boxes are shaded, colored, or not pure white.
- The PDF is raster/scanned rather than vector.
- Boxes outside height thresholds.

Use `--debug` to examine intermediate CSV files.

***

### Q: Why should I always use a copy of the original PDF before processing?

**A:** flyfield modifies PDFs by creating output files with appended suffixes. Using copies prevents accidental overwrites of original documents.

***

### Q: Why capture data from filled PDFs? What if the form changes yearly?

**A:** Many fields remain stable across versions. Captured data helps:

- Reuse unchanged data.
- Reduce manual entry errors.
- Support audits and comparisons over time.

Remapping may be required if form layout changes significantly.

***

## Advanced Customization

### Q: Can I customize field naming or positioning?

**A:** Yes. flyfield generates standalone Python scripts for:

- Adding fields (`*-field-generator.py`)
- Filling fields (`*-filler.py`)

You can edit these scripts to customize names, coordinates, max lengths, and formatting.

Run the modified scripts to regenerate PDFs or refill data.

***

## Troubleshooting

### Q: Why do filled fields not show up correctly in some PDF viewers?

**A:** PDF viewer compatibility varies. To improve results:

- Use Adobe Acrobat or well-supported viewers.
- Avoid PDFs with complex overlays or security restrictions.
- Flatten fields with external tools if necessary.

***

### Q: How can I extract data from a filled PDF?

**A:** Use the `--capture` option:

```
flyfield --input-pdf filled.pdf --capture
```

This exports filled fields to CSV, normalizing numeric values and uppercasing text.

***

## General Information

### Q: Does flyfield support scanned PDFs?

**A:** No. flyfield requires vector PDF files with proper vector graphics and white boxes.

***

### Q: Can flyfield handle PDFs with existing AcroForms?

**A:** flyfield detects white box placeholders in vector PDFs to generate aligned interactive form fields. While existing AcroForm fields can be filled directly using tools like PyPDFForm, flyfield might be useful for handling split numeric fields (e.g., money boxes), enabling accurate grouping and filling of these complex fields.

***

For more help, consult the [User Guide](usage.md), [Developer Guide](developer.md), or [Worked Example](example.md).

***