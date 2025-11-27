"""
Build a GRP-style JSON from MultiHiertt train data.

Output schema per entry:
{
  "task_id": "Test 1",
  "title": "<question text>",
  "spreadsheets": ["extracted_xlsx/train/Train_1/table0.xlsx", ...],
  "prompt": "<question text>",
  "answer": "<answer text>",
  "expected_output_file": [],
  "feedback": ""
}
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_train(train_path: Path) -> List[Dict[str, Any]]:
    with train_path.open() as f:
        return json.load(f)


def gather_spreadsheets(base_dir: Path, uid: str) -> List[str]:
    """List XLSX files for a given UID folder."""
    folder = base_dir / f"Train_{uid}"
    if not folder.exists():
        return []
    return sorted(str(p) for p in folder.glob("*.xlsx"))


def derive_title(paragraphs: List[str], question: str, uid: str) -> str:
    """
    Try to pick a short, meaningful title from the paragraphs.
    - Prefer a paragraph starting with "Table" (but skip "Table of Contents" and markers).
    - Otherwise use the first non-empty paragraph.
    - Fall back to the question or a generic label.
    """
    first_non_empty = ""
    for para in paragraphs:
        text = para.strip()
        if not text or text.startswith("##"):
            continue
        if not first_non_empty:
            first_non_empty = text
        lower = text.lower()
        if lower.startswith("table ") and "table of contents" not in lower:
            return text
    if first_non_empty:
        return " ".join(first_non_empty.split()[:15])
    return question or f"Task {uid}"


def build_entry(example: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    uid = str(example.get("uid", "")).strip()
    question = example.get("qa", {}).get("question", "")
    answer = example.get("qa", {}).get("answer", "")
    paragraphs = example.get("paragraphs", [])
    spreadsheets = gather_spreadsheets(base_dir, uid)
    title = derive_title(paragraphs, question, uid)
    return {
        "task_id": f"Test {uid}",
        "title": title,
        "spreadsheets": spreadsheets,
        "prompt": question,
        "answer": answer,
        "expected_output_file": [],
        "feedback": "",
    }


def main() -> None:
    train_path = Path("lightning_modules/datasets/train.json")
    out_path = Path("train_GRP.json")
    base_dir = Path("extracted_xlsx/train")

    examples = load_train(train_path)
    output = [build_entry(ex, base_dir) for ex in examples]

    with out_path.open("w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
