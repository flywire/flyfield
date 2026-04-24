"""Configuration module for pdf_form_field."""


# Default file paths

DEFAULT_INPUT_PDF = "input.pdf"
DEFAULT_CAPTURE_SUFFIX = "-capture"
DEFAULT_FIELD_GENERATOR_SUFFIX = "-field-generator.py"
DEFAULT_FILLER_SUFFIX = "-filler.py"
DEFAULT_MARKUP_SUFFIX = "-markup"
DEFAULT_FIELDS_SUFFIX = "-fields"
DEFAULT_FILL_SUFFIX = "-filled"

# Color constants (normalized RGB)

COLOR_WHITE = (1, 1, 1)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 1)


# Target color for extraction (normalized RGB)

TARGET_COLOUR = COLOR_WHITE        # White for fill colour detection
USER_FILL_COLOR = COLOR_BLACK      # User-entered text
PREPRINT_COLOR_TOLERANCE = 0.01    # Non-exact match = pre-printed

MARKUP_STROKE_COLOR = COLOR_BLUE   # Markup stroke
MARKUP_TEXT_COLOR = COLOR_BLUE     # Markup text

# Thresholds for layout grouping and gaps (arbitrary units, related to PDF coords)

GAP = 1.9
GAP_GROUP = 7.6
GAP_THRESHOLD = 3.0
F = 1  # Fudge factor, maybe invisible margin

# Constants for height filtering (units are PDF coordinate points)

MIN_BOX_HEIGHT = 15.0
MAX_BOX_HEIGHT = 30.0  # Filters out signature boxes

# Field types considered numeric for special processing

NUMERIC_FIELD_TYPES = ["Currency", "CurrencyDecimal", "DollarCents", "Dollars"]

# Pages to test on, if set (list of page numbers)
# This is a mutable list, so CLI/main should clear and extend this to set pages.

PDF_PAGES = []
