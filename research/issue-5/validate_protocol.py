#!/usr/bin/env python3
"""Dependency-free integrity checks for the frozen Issue 5 protocol artifacts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL.md"
SCHEMA = ROOT / "observation.schema.json"

required_phrases = [
    "continufy-live-latency-v1.0.0",
    "LATENCY_BOTTLENECK_IDENTIFIED",
    "LATENCY_VALUE_UNRESOLVED",
    "NO_MEANINGFUL_LATENCY_BOTTLENECK",
    "BLOCKED_BY_ACCESS_OR_PROVENANCE",
    "An observation is a recorded row, not evidence by itself.",
    "Reduced latency is not business value.",
    "A research result is not permission to build.",
]

text = PROTOCOL.read_text(encoding="utf-8")
missing = [phrase for phrase in required_phrases if phrase not in text]
if missing:
    raise SystemExit(f"protocol missing frozen requirements: {missing}")

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
assert schema["properties"]["protocol_id"]["const"] == "continufy-live-latency-v1.0.0"
assert schema["additionalProperties"] is False
assert schema["properties"]["stages"]["minItems"] == 6
assert schema["properties"]["stages"]["maxItems"] == 6

for path in (PROTOCOL, SCHEMA):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{digest}  {path.name}")
print("protocol artifact validation: PASS")
