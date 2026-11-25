import os
import sys
import re
# Allow running this file directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.loader import load_hr_document
def preprocess_text(raw_text: str) -> str:
    """Cleans separator lines and converts headings into Markdown format."""
    # Remove separator lines (=====)
    text = re.sub(r"(?m)^={5,}\s*$", "", raw_text)
    # Convert main sections into Level 1 Markdown headers (#)
    text = re.sub(
        r"(?m)^SECTION\s+(\d+):\s*(.+)$",
        r"# SECTION \1: \2",
        text
    )
    # Convert numbered subsections into Level 2 Markdown headers (##)
    text = re.sub(
        r"(?m)^(\d+\.\d+)\s+(.+)$",
        r"## \1 \2",
        text
    )
    # Convert FAQ questions into Level 3 Markdown headers (###)
    text = re.sub(
        r"(?m)^Q:\s*(.+)$",
        r"### Q: \1",
        text
    )

    return text
