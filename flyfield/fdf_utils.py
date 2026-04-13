import fitz  # PyMuPDF
import re
import os
import logging
from PyPDFForm import PdfWrapper
from typing import Dict, Any
from .utils import  is_currency_type, get_pdf_id


def extract_fdf_fields(pdf_path: str) -> tuple[Dict[str, str], list[str]]:
    """Extract form fields and document IDs from a PDF.

    Args:
        pdf_path: Path to the PDF.

    Returns:
        (fields_dict, pdf_ids) where fields_dict maps field names to FDF‑style values
        and pdf_ids is a two‑element list of /ID strings.
    """
    doc = fitz.open(pdf_path)
    
    # Extract ALL form fields
    fields = {}
    for page in doc:
        for widget in page.widgets():
            name = widget.field_name
            value = widget.field_value

            # FDF format conversion
            if value is None or value == "":
                fields[name] = "/Off"
            elif isinstance(value, bool):
                fields[name] = "/Yes" if value else "/Off"
            else:
                fields[name] = str(value)
    
    try:
        id_str = get_pdf_id(pdf_path)
        # Parse "[<A> <B>]" → ['<A>', '<B>']
        if id_str.startswith("[<") and id_str.endswith(">]"):
            ids = id_str[2:-2].split("><", 1)
            pdf_id = [f"<{ids[0].strip()}>", f"<{ids[1].strip()}>"]
        else:
            raise ValueError("Invalid ID")
    except Exception:
        logging.getLogger(__name__).info("No valid /ID in trailer; using dummy IDs")
        pdf_id = ["<dummy1>", "<dummy2>"]

    doc.close()
    return fields, pdf_id


def parse_fdf_to_dict(fdf_path: str) -> Dict[str, str]:
    """Parse FDF file to field dictionary.

    Args:
        fdf_path: Path to the FDF file.

    Returns:
        Dictionary mapping field_name → value.
    """
    for enc in ['utf-8', 'latin-1', 'cp1252', 'ascii']:
        try:
            with open(fdf_path, "r", encoding=enc) as f:
                content = f.read()
            logging.info(f"FDF loaded: {enc}")
            break
        except UnicodeDecodeError:
            logging.debug(f"FDF encoding {enc} failed, trying next")
            continue

    if content is None:
        # Binary fallback: read all bytes safely
        with open(fdf_path, "rb") as f:
            content = f.read().decode('latin-1', errors='replace')
        logging.warning("FDF binary fallback")

    # Verify FDF header
    if not content.strip().startswith('%FDF'):
        raise ValueError(f"Invalid FDF file: missing %%FDF header (first bytes: {content[:20]!r})")

    fields_match = re.search(r"/Fields\s*\[\s*([^]]+)\s*\]", content, re.DOTALL | re.IGNORECASE)
    if not fields_match:
        raise ValueError("No /Fields array")

    form_data = {}

    field_pattern = r'<<\s*/T\s*\(\s*([^)]+)\s*\)\s*/V\s*\(\s*([^)]*)\s*\)\s*>>'
    for match in re.finditer(field_pattern, fields_match.group(1), re.DOTALL):
        field_name, field_value = match.groups()
        # Unescape FDF values
        field_value = (field_value.replace('\\\\(', '(')
                             .replace('\\\\)', ')')
                             .replace('\\\\\\\\', '\\\\'))
        form_data[field_name] = field_value

    logging.info(f"Parsed {len(form_data)} fields")
    return form_data


def fill_pdf_from_fdf(template_pdf: str, fdf_path: str, output_pdf: str) -> Dict[str, int]:
    """Fill PDF from FDF using PyPDFForm.

    Args:
        template_pdf: Path to the template PDF.
        fdf_path: Path to the FDF file.
        output_pdf: Path for the filled output PDF.

    Returns:
        Dict with keys: "fields_count", "currency_padded", "output_pdf".
    """
    logging.debug(f"Filling {template_pdf} from {fdf_path}")
    form_data = parse_fdf_to_dict(fdf_path)
    filled_pdf = PdfWrapper(template_pdf).fill(form_data).read()
    
    with open(output_pdf, "wb") as f:
        f.write(filled_pdf)
    
    filled_count = len([v for v in form_data.values() if v.strip()])

    return {
        "fields_count": filled_count,
        "currency_padded": 0,
        "output_pdf": output_pdf
    }


def save_pdf_form_data_to_fdf(pdf_path: str, fdf_path: str, empty_fields: bool = False) -> str:
    """Save PDF form data as FDF.

    Args:
        pdf_path: Path to the filled PDF.
        fdf_path: Path to write the FDF.
        empty_fields: Whether to include empty (off) fields (default False).

    Returns:
        Path to the written FDF file.
    """
    fields, pdf_ids = extract_fdf_fields(pdf_path)

    if not empty_fields:
        fields = {k: v for k, v in fields.items() if v != "/Off"}

    filename = os.path.basename(pdf_path)
    fdf_content = f"""%FDF-1.4
1 0 obj
<< /FDF << /F ({filename}) /UF ({filename}) /Fields [
"""

    for field_name in sorted(fields):
        value = fields[field_name].replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        fdf_content += f"<< /T ({field_name}) /V ({value}) >>\n"

    fdf_content += f"""] /ID [{pdf_ids[0]} {pdf_ids[1]}] >> /Type /Catalog >>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""

    with open(fdf_path, "w", encoding="utf-8") as f:
        f.write(fdf_content)

    logging.info(f"FDF saved: {fdf_path}")
    return fdf_path
