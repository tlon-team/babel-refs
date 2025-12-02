#!/usr/bin/env python3
"""
Split a translations JSON file into per-language JSON files.

Input JSON format (example):
{
  "Key1": {"ja": "value1", "es": "value2"},
  "Key2": {"es": "valor"}
}

Output files (under the same base folder as the input file):
json/ja/abstract-translations.json -> {"Key1": "value1"}
json/es/abstract-translations.json -> {"Key1": "value2", "Key2": "valor"}

Notes:
- Missing translations are simply omitted from that language's output.
- Creates language subfolders as needed (e.g., json/<lang>/).
- Tries to be robust to C/JS-style comments in the input by stripping them.

Usage:
  python scripts/split_by_language.py json/abstract-translations.json

Optional arguments:
  --out-base DIR   Base directory for language folders (default: parent of input)
  --filename NAME  Output filename to use in each language folder (default: basename of input)

"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any


def _strip_comments(text: str) -> str:
    """Remove /* ... */ and // ... comments from a JSON-like string.

    This is a best-effort pass to accommodate annotated files; it is not a full JSON5 parser.
    """
    # Remove /* block comments */
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Remove // line comments
    text = re.sub(r"(^|\s)//.*$", "", text, flags=re.MULTILINE)
    return text


def load_json(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    # Always attempt with comment stripping first to be tolerant
    cleaned = _strip_comments(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback to strict in case comment stripping broke something unexpectedly
        return json.loads(raw)


def split_by_language(
    input_path: Path, out_base: Path | None = None, out_filename: str | None = None
) -> None:
    data = load_json(input_path)

    if out_base is None:
        out_base = input_path.parent
    if out_filename is None:
        out_filename = input_path.name

    per_lang: Dict[str, Dict[str, Any]] = defaultdict(dict)

    for key, translations in data.items():
        if not isinstance(translations, dict):
            # Skip non-dict entries
            continue
        for lang, value in translations.items():
            if value is None:
                continue
            per_lang[str(lang)][str(key)] = value

    # Write outputs
    for lang, mapping in per_lang.items():
        lang_dir = out_base / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        out_path = lang_dir / out_filename
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2, sort_keys=True)

    # Print a brief summary
    print(f"Processed: {input_path}")
    for lang, mapping in sorted(per_lang.items()):
        print(f"  {lang}: {len(mapping)} entries -> {(out_base / lang / out_filename)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split a translations JSON into per-language JSON files."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to input translations JSON (e.g., json/abstract-translations.json)",
    )
    parser.add_argument(
        "--out-base",
        dest="out_base",
        type=Path,
        default=None,
        help="Base directory for language folders (default: parent of input)",
    )
    parser.add_argument(
        "--filename",
        dest="out_filename",
        type=str,
        default=None,
        help="Output filename to use in each language folder (default: basename of input)",
    )
    args = parser.parse_args()

    split_by_language(args.input, args.out_base, args.out_filename)


if __name__ == "__main__":
    main()
