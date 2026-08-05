from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .schemas import InferenceRecord


def write_jsonl(records: list[InferenceRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            d = asdict(record)
            if hasattr(record.generation_status, "value"):
                d["generation_status"] = record.generation_status.value
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def append_jsonl(record: InferenceRecord, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        d = asdict(record)
        if hasattr(record.generation_status, "value"):
            d["generation_status"] = record.generation_status.value
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
