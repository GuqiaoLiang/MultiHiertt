"""
Convert HTML tables in MultiHiertt JSON files to XLSX.

For each example UID, this script writes one XLSX per table:
  <out>/<uid>/table{n}.xlsx

Usage:
    python3 convert_tables_to_xlsx.py --src lightning_modules/datasets/test.json --out extracted_xlsx/test
"""

import argparse
import json
import pathlib
from typing import Any, Dict, List


def load_examples(path: pathlib.Path) -> List[Dict[str, Any]]:
    with path.open() as f:
        return json.load(f)


def export_tables(uid: str, tables: List[str], out_dir: pathlib.Path, pd_module) -> None:
    example_dir = out_dir / uid
    example_dir.mkdir(parents=True, exist_ok=True)
    for idx, html in enumerate(tables):
        try:
            dfs = pd_module.read_html(html)
        except ValueError:
            # No tables parsed; skip.
            continue
        for sub_idx, df in enumerate(dfs):
            suffix = f"{idx}" if len(dfs) == 1 else f"{idx}_{sub_idx}"
            xlsx_path = example_dir / f"table{suffix}.xlsx"
            df.to_excel(xlsx_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HTML tables in MultiHiertt JSON to XLSX files.")
    parser.add_argument("--src", required=True, type=pathlib.Path, help="Path to source JSON (e.g., lightning_modules/datasets/test.json).")
    parser.add_argument("--out", required=True, type=pathlib.Path, help="Output directory to store XLSX files.")
    args = parser.parse_args()

    examples = load_examples(args.src)
    args.out.mkdir(parents=True, exist_ok=True)

    # Import pandas lazily so the script can give a clear error if it's missing.
    try:
        import pandas as pd  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - informative failure path
        raise SystemExit(
            "pandas is required to convert HTML tables to XLSX. "
            "Install it (e.g., `python3 -m pip install -r requirements.txt`) and rerun."
        ) from exc

    for example in examples:
        uid = example.get("uid", "unknown_uid")
        tables = example.get("tables", [])
        export_tables(uid, tables, args.out, pd)


if __name__ == "__main__":
    main()
