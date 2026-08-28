#!/usr/bin/env python3
"""Deterministic execution-record validation for protocol v1.0.0."""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "observation.schema.json").read_text())
STAGES = ["identified", "captured", "edited_reframed", "captioned_packaged", "reviewed_approved", "published"]


def instant(value: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z", value):
        raise ValueError("must be RFC 3339 UTC with milliseconds")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def schema_errors(value: Any, rule: dict[str, Any], path: str = "$") -> list[str]:
    """Evaluate precisely the JSON Schema vocabulary used by this repository."""
    if "$ref" in rule:
        target: Any = SCHEMA
        for part in rule["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return schema_errors(value, target, path)
    errors: list[str] = []
    kinds = rule.get("type")
    if kinds:
        kinds = [kinds] if isinstance(kinds, str) else kinds
        match = {"object": isinstance(value, dict), "array": isinstance(value, list),
                 "string": isinstance(value, str), "integer": isinstance(value, int) and not isinstance(value, bool),
                 "boolean": isinstance(value, bool), "null": value is None}
        if not any(match.get(kind, False) for kind in kinds):
            return [f"{path}: wrong type (expected {' or '.join(kinds)})"]
    if "const" in rule and value != rule["const"]: errors.append(f"{path}: const mismatch")
    if "enum" in rule and value not in rule["enum"]: errors.append(f"{path}: enum mismatch")
    if isinstance(value, str):
        if "pattern" in rule and not re.search(rule["pattern"], value): errors.append(f"{path}: pattern mismatch")
        if len(value) < rule.get("minLength", 0): errors.append(f"{path}: too short")
        if rule.get("format") == "date-time":
            try: instant(value)
            except ValueError as exc: errors.append(f"{path}: {exc}")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in rule and value < rule["minimum"]: errors.append(f"{path}: below minimum")
        if "maximum" in rule and value > rule["maximum"]: errors.append(f"{path}: above maximum")
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        for key in rule.get("required", []):
            if key not in value: errors.append(f"{path}: missing {key}")
        if rule.get("additionalProperties") is False:
            for key in value.keys() - properties.keys(): errors.append(f"{path}: unexpected {key}")
        for key in value.keys() & properties.keys(): errors.extend(schema_errors(value[key], properties[key], f"{path}.{key}"))
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0): errors.append(f"{path}: too few items")
        if "maxItems" in rule and len(value) > rule["maxItems"]: errors.append(f"{path}: too many items")
        prefix = rule.get("prefixItems", [])
        for index, item in enumerate(value):
            child = prefix[index] if index < len(prefix) else rule.get("items")
            if isinstance(child, dict): errors.extend(schema_errors(item, child, f"{path}[{index}]"))
            elif child is False: errors.append(f"{path}[{index}]: forbidden item")
    for child in rule.get("allOf", []): errors.extend(schema_errors(value, child, path))
    if "oneOf" in rule and sum(not schema_errors(value, child, path) for child in rule["oneOf"]) != 1:
        errors.append(f"{path}: oneOf mismatch")
    condition = "if" in rule and not schema_errors(value, rule["if"], path)
    if condition: errors.extend(schema_errors(value, rule.get("then", {}), path))
    elif "else" in rule: errors.extend(schema_errors(value, rule["else"], path))
    return errors


def at(timestamp: dict[str, Any]) -> datetime:
    return instant(timestamp["at"])


def validate_observation(obs: dict[str, Any]) -> list[str]:
    errors = schema_errors(obs, SCHEMA)
    if errors: return sorted(set(errors))
    provenance = {p["provenance_id"] for p in obs["provenance"]}
    if len(provenance) != len(obs["provenance"]): errors.append("provenance: duplicate id")
    references = {obs["occurred_at"]["provenance_id"]}
    previous = at(obs["occurred_at"])
    attempt_ids: set[str] = set()
    for index, stage in enumerate(obs["stages"]):
        label = f"stages[{index}]"
        if stage["name"] != STAGES[index]: errors.append(f"{label}: wrong canonical order")
        times = stage["started_at"], stage["completed_at"]
        if stage["status"] in ("completed", "not_required") and None in times: errors.append(f"{label}: reached stage needs timestamps")
        if stage["status"] in ("unobservable", "not_reached") and any(times): errors.append(f"{label}: missing stage needs null timestamps")
        if stage["status"] != "completed" and not stage["status_reason"]: errors.append(f"{label}: status reason required")
        if (stage["status"] == "unobservable") != bool(stage["expected_source"]): errors.append(f"{label}: expected_source is required only when unobservable")
        if all(times):
            start, end = map(at, times); references.update(t["provenance_id"] for t in times)
            if start < previous or end < start: errors.append(f"{label}: chronology violation")
            if stage["status"] == "not_required" and start != end: errors.append(f"{label}: not_required is not zero-duration")
            previous = end
        for attempt in stage["attempts"]:
            if attempt["attempt_id"] in attempt_ids: errors.append(f"{label}: duplicate attempt id")
            if attempt["is_rework"] != bool(attempt["supersedes_attempt_id"]): errors.append(f"{label}: inconsistent rework")
            if (attempt["status"] == "failed") != bool(attempt["failure_reason"]): errors.append(f"{label}: inconsistent failure reason")
            if attempt["supersedes_attempt_id"] and attempt["supersedes_attempt_id"] not in attempt_ids: errors.append(f"{label}: superseded attempt is not earlier")
            attempt_ids.add(attempt["attempt_id"])
            start, end = at(attempt["started_at"]), at(attempt["ended_at"])
            references.update((attempt["started_at"]["provenance_id"], attempt["ended_at"]["provenance_id"]))
            if end < start: errors.append(f"{label}: attempt chronology violation")
            intervals = []
            for kind in ("active_intervals", "wait_intervals"):
                for interval in attempt[kind]:
                    left, right = instant(interval["start"]), instant(interval["end"])
                    references.add(interval["provenance_id"]); intervals.append((left, right))
                    if left < start or right > end or right < left: errors.append(f"{label}: interval outside attempt")
            intervals.sort()
            if any(b[0] < a[1] for a, b in zip(intervals, intervals[1:])): errors.append(f"{label}: intervals overlap")
    published_stage = obs["stages"][-1]["completed_at"]
    if obs["terminal_status"] == "published" and (published_stage is None or at(published_stage) != at(obs["published_at"])):
        errors.append("terminal: published timestamp mismatch")
    if obs["terminal_status"] == "abandoned": references.add(obs["abandoned_at"]["provenance_id"])
    if obs["outcome"] is not None:
        if instant(obs["outcome"]["measured_at"]) != at(obs["published_at"]) + timedelta(hours=168): errors.append("outcome: not measured at 168 hours")
        if obs["outcome"]["provenance_id"] not in provenance: errors.append("outcome: provenance missing")
    if not references <= provenance: errors.append("provenance: reference missing")
    return sorted(set(errors))


def validate_dataset(records: list[dict[str, Any]]) -> list[str]:
    errors, ids, keys = [], set(), []
    for index, obs in enumerate(records):
        errors.extend(f"observations[{index}].{error}" for error in validate_observation(obs))
        if obs.get("observation_id") in ids: errors.append(f"observations[{index}]: duplicate observation id")
        ids.add(obs.get("observation_id"))
        try: keys.append((instant(obs["session_start_at"]), obs["session_id"], at(obs["occurred_at"]), obs["observation_id"]))
        except (KeyError, TypeError, ValueError): pass
    if keys != sorted(keys): errors.append("dataset: noncanonical order")
    eligible = [obs for obs in records if obs.get("eligible")]
    if len(eligible) > 60: errors.append("dataset: eligible-moment cap exceeded")
    if len({obs.get("session_id") for obs in eligible}) > 12: errors.append("dataset: session cap exceeded")
    return sorted(set(errors))


def determination(records: list[dict[str, Any]]) -> str:
    eligible = [o for o in records if o["eligible"]]; published = [o for o in eligible if o["terminal_status"] == "published"]
    complete = [o for o in eligible if all(s["status"] in ("completed", "not_required") for s in o["stages"])]
    if (len(eligible) < 30 or len({o["creator_id"] for o in eligible}) < 3 or len({o["session_id"] for o in eligible}) < 3
            or len(published) < 10 or len(complete) / max(1, len(eligible)) < .8):
        return "BLOCKED_BY_ACCESS_OR_PROVENANCE"
    durations = {name: [] for name in STAGES}; shares = {name: [] for name in STAGES}
    for obs in published:
        total = (at(obs["published_at"]) - at(obs["occurred_at"])).total_seconds()
        for stage in obs["stages"]:
            value = (at(stage["completed_at"]) - at(stage["started_at"])).total_seconds()
            durations[stage["name"]].append(value); shares[stage["name"]].append(value / total if total else 0)
    def percentile(values: list[float], q: float) -> float:
        values = sorted(values); rank = (len(values) - 1) * q; low, high = math.floor(rank), math.ceil(rank)
        return values[low] + (values[high] - values[low]) * (rank - low)
    if any(percentile(shares[n], .5) >= .25 and percentile(durations[n], .75) >= 1800 for n in STAGES):
        return "LATENCY_BOTTLENECK_IDENTIFIED"
    outcomes = [o for o in published if o["outcome"] is not None]
    if len(outcomes) < 30 or len({o["creator_id"] for o in outcomes}) < 3: return "LATENCY_VALUE_UNRESOLVED"
    def ranks(values: list[float]) -> list[float]:
        result = [0.0] * len(values)
        for value in sorted(set(values)):
            positions = [i for i, candidate in enumerate(values) if candidate == value]
            rank = (min(positions) + max(positions)) / 2 + 1
            for position in positions: result[position] = rank
        return result
    def spearman(rows: list[dict[str, Any]]) -> float | None:
        x = ranks([(at(o["published_at"]) - at(o["occurred_at"])).total_seconds() for o in rows])
        y = ranks([math.log1p(o["outcome"]["views_168h"]) for o in rows])
        mx, my = sum(x) / len(x), sum(y) / len(y)
        denominator = math.sqrt(sum((v - mx) ** 2 for v in x) * sum((v - my) ** 2 for v in y))
        return sum((a - mx) * (b - my) for a, b in zip(x, y)) / denominator if denominator else None
    grouped = {creator: [o for o in outcomes if o["creator_id"] == creator] for creator in sorted({o["creator_id"] for o in outcomes})}
    creators = list(grouped); rng = random.Random(5); samples = []
    for _ in range(2000):
        rows = []
        for creator in rng.choices(creators, k=len(creators)): rows.extend(grouped[creator])
        value = spearman(rows)
        if value is not None: samples.append(value)
    if not samples: return "LATENCY_VALUE_UNRESOLVED"
    low, high = percentile(samples, .025), percentile(samples, .975)
    if low > 0 or high < 0: return "NO_MEANINGFUL_LATENCY_BOTTLENECK"
    return "LATENCY_VALUE_UNRESOLVED"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("dataset", type=Path); args = parser.parse_args()
    records = json.loads(args.dataset.read_text())
    if not isinstance(records, list): print("dataset: top level must be an array", file=sys.stderr); return 2
    errors = validate_dataset(records)
    if errors: print("\n".join(errors), file=sys.stderr); return 1
    print(f"records valid: {len(records)}\ndetermination: {determination(records)}\ncollection_readiness: NULL")
    return 0


if __name__ == "__main__": raise SystemExit(main())
