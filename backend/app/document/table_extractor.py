import re
from typing import List, Dict, Any

def extract_tables_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses pipe-delimited, tab-delimited, or multi-space aligned tables from raw text.
    """
    tables = []
    lines = text.split("\n")
    current_table = []

    for line in lines:
        stripped = line.strip()
        # Pipe-delimited row (e.g. Markdown or ASCII table)
        if "|" in stripped:
            cells = [c.strip() for c in stripped.split("|") if c.strip() and not set(c.strip()).issubset({"-", "=", "+", ":" })]
            if len(cells) >= 2:
                current_table.append(cells)
                continue

        # Space or tab delimited columns
        columns = [c.strip() for c in re.split(r"\t+|\s{2,}", stripped) if c.strip()]
        if len(columns) >= 2:
            current_table.append(columns)
        else:
            if len(current_table) >= 2:
                tables.append({"rows": current_table})
            current_table = []

    if len(current_table) >= 2:
        tables.append({"rows": current_table})

    return tables
