"""
Renumber uids in a MultiHiertt JSON file to a simple 1..N sequence.

Usage:
    python renumber_test_uids.py --input lightning_modules/datasets/test.json --output lightning_modules/datasets/test.json
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any


def load_examples(path: Path) -> List[Dict[str, Any]]:
    with path.open() as f:
        return json.load(f)


def renumber_uids(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for idx, example in enumerate(examples, start=1):
        example["uid"] = str(idx)
    return examples


def save_examples(examples: List[Dict[str, Any]], path: Path) -> None:
    with path.open("w") as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Renumber uids in MultiHiertt JSON to sequential integers starting at 1.")
    parser.add_argument("--input", required=True, type=Path, help="Path to the source JSON (e.g., lightning_modules/datasets/test.json).")
    parser.add_argument(
        "--output",
        required=False,
        type=Path,
        help="Path to write the updated JSON. Defaults to the input path for in-place update.",
    )
    args = parser.parse_args()

    output_path = args.output if args.output is not None else args.input

    examples = load_examples(args.input)
    examples = renumber_uids(examples)
    save_examples(examples, output_path)


if __name__ == "__main__":
    main()
