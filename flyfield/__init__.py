"""
pdf_form_generator package

This package provides modular components for:
- PDF box extraction and layout processing
- CSV input/output
- PDF markup and form field generation/filling
"""

from .config import *
from .utils import *
from .extract import *
from .io_utils import *
from .markup_and_fields import *

# Optionally define __all__ to specify what is exported on import *
__all__ = [
    "config",
    "utils",
    "extract",
    "io_utils",
    "markup_and_fields",
]
