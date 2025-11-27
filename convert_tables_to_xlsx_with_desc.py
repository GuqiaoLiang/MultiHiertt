"""
Convert HTML tables in a MultiHiertt JSON file to XLSX and attach table descriptions.

For each example UID, this script writes one XLSX per table:
  <out>/<uid>/table{n}.xlsx

Each XLSX contains:
  - Sheet \"table\": the table content
  - Sheet \"description\": description text captured from paragraphs between \"## Table k ##\" markers

Usage:
    python3 convert_tables_to_xlsx_with_desc.py --src lightning_modules/datasets/train.json --out extracted_xlsx/train_desc
"""

import argparse
import json
import pathlib
import re
from typing import Any, Dict, List, Tuple

import pandas as pd

# Paragraph markers look like "## Table 0 ##".
TABLE_MARKER_RE = re.compile(r"##\s*Table\s*(\d+)\s*##")
# Characters Excel will reject.
INVALID_XL_CHARS = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]")


def load_examples(path: pathlib.Path) -> List[Dict[str, Any]]:
    with path.open() as f:
        return json.load(f)


def extract_descriptions(paragraphs: List[str]) -> Dict[int, str]:
    """
    Build a mapping: table index -> description text.

    We treat paragraphs between \"## Table k ##\" and the next table marker as the description for table k.
    """
    starts: List[Tuple[int, int]] = []  # (table_idx, paragraph_pos)
    for pos, para in enumerate(paragraphs):
        m = TABLE_MARKER_RE.search(para)
        if m:
            starts.append((int(m.group(1)), pos))

    descriptions: Dict[int, str] = {}
    for i, (table_idx, start_pos) in enumerate(starts):
        end_pos = starts[i + 1][1] if i + 1 < len(starts) else len(paragraphs)
        chunk = paragraphs[start_pos + 1 : end_pos]
        text = "\n".join(chunk).strip()
        descriptions[table_idx] = text
    return descriptions


def sanitize_for_excel(text: str) -> str:
    """Remove characters that cannot be stored in an Excel cell."""
    return INVALID_XL_CHARS.sub("", text)


def export_tables(uid: str, tables: List[str], paragraphs: List[str], out_dir: pathlib.Path) -> None:
    desc_map = extract_descriptions(paragraphs)
    example_dir = out_dir / uid
    example_dir.mkdir(parents=True, exist_ok=True)

    for idx, html in enumerate(tables):
        try:
            dfs = pd.read_html(html)
        except ValueError:
            # No tables parsed; skip.
            continue

        for sub_idx, df in enumerate(dfs):
            suffix = f"{idx}" if len(dfs) == 1 else f"{idx}_{sub_idx}"
            xlsx_path = example_dir / f"table{suffix}.xlsx"
            desc_text = sanitize_for_excel(desc_map.get(idx, ""))

            with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="table")
                # Store description text in a second sheet.
                pd.DataFrame({"description": [desc_text]}).to_excel(writer, index=False, sheet_name="description")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HTML tables in MultiHiertt JSON to XLSX files with descriptions.")
    parser.add_argument("--src", required=True, type=pathlib.Path, help="Path to source JSON (e.g., lightning_modules/datasets/train.json).")
    parser.add_argument("--out", required=True, type=pathlib.Path, help="Output directory to store XLSX files.")
    args = parser.parse_args()

    examples = load_examples(args.src)
    args.out.mkdir(parents=True, exist_ok=True)

    for example in examples:
        uid = example.get("uid", "unknown_uid")
        tables = example.get("tables", [])
        paragraphs = example.get("paragraphs", [])
        export_tables(uid, tables, paragraphs, args.out)


if __name__ == "__main__":
    main()
