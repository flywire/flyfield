"""
Configuration constants used throughout the project.
"""

# Default file paths
DEFAULT_INPUT_PDF = "input.pdf"
DEFAULT_CAPTURE_SUFFIX = "-capture.csv"
DEFAULT_FIELD_GENERATOR_SUFFIX = "-field-generator.py"
DEFAULT_FILLER_SUFFIX = "-filler.py"
DEFAULT_MARKUP_SUFFIX = "-markup"
DEFAULT_FIELDS_SUFFIX = "-fields"
DEFAULT_FILL_SUFFIX = "-filled"

# Color constants (normalized RGB)
COLOR_WHITE = (1, 1, 1)
COLOR_BLACK = (0, 0, 0)

# Target color for extraction (normalized RGB)
TARGET_COLOUR = (1, 1, 1)  # RGB normalized white for fill colour detection

# Thresholds for layout grouping and gaps (arbitrary units, related to PDF coords)
GAP_THRESHOLD = 3.0
GAP = 1.9
GAP_GROUP = 7.6

# Constants for height filtering (units are PDF coordinate points)
MIN_BOX_HEIGHT = 15.0
MAX_BOX_HEIGHT = 30.0  # Filters out signature boxes

# Field types considered numeric for special processing
NUMERIC_FIELD_TYPES = ["Currency", "CurrencyDecimal", "DollarCents", "Dollars"]

# Pages to test on, if set (list of page numbers)
PDF_PAGES = None
