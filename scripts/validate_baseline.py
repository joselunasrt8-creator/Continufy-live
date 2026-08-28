#!/usr/bin/env python3
"""Deterministically validate the bounded Issue #1 research artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    schema = json.loads((ROOT / "research/observation.schema.json").read_text())
    assert schema["additionalProperties"] is False
    assert len(schema["required"]) == 10

    with (ROOT / "research/source-inventory.csv").open(newline="") as handle:
        sources = list(csv.DictReader(handle))
    assert sources and all(row["platform"] and row["status"] for row in sources)

    with (ROOT / "research/pilot/observations.csv").open(newline="") as handle:
        observations = list(csv.DictReader(handle))
    assert observations == [], "blocked pilot must not contain invented observations"

    with (ROOT / "research/pilot/acquisition-log.csv").open(newline="") as handle:
        attempts = list(csv.DictReader(handle))
    assert len(attempts) == 4 and all(row["result"] == "blocked" for row in attempts)
    assert all(int(row["records"]) == 0 for row in attempts)
    print(f"validated {len(sources)} sources, {len(attempts)} attempts, 0 observations")


if __name__ == "__main__":
    main()
