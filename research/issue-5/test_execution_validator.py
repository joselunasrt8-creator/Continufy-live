#!/usr/bin/env python3
"""Synthetic valid/invalid fixtures for the execution-record validator."""
import copy
import json
import tempfile
import unittest
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import validate_observations as validator

ROOT = Path(__file__).resolve().parent
CASES = json.loads((ROOT / "fixtures/cases.json").read_text())
BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def stamp(minutes: int, provenance: str = "p1") -> dict:
    value = BASE + timedelta(minutes=minutes)
    return {"at": value.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "uncertainty_ms_lower": 0,
            "uncertainty_ms_upper": 0, "provenance_id": provenance}


def provenance(identifier: str) -> dict:
    return {"provenance_id": identifier, "source_id": f"source-{identifier}", "source_type": "audit_log",
            "collector_id": "collector-1", "collected_at": "2026-01-09T00:00:00.000Z",
            "sha256": "a" * 64, "storage_uri": f"immutable://{identifier}", "raw_timestamp": "raw",
            "stated_timezone": "UTC", "clock_offset_ms": 0}


def record(number: int = 1) -> dict:
    boundaries = [(1, 2), (2, 3), (3, 43), (43, 48), (48, 50), (50, 55)]
    stages = [{"name": name, "status": "completed", "started_at": stamp(start), "completed_at": stamp(end),
               "status_reason": None, "expected_source": None, "boundary_precision": "distinct", "attempts": []}
              for name, (start, end) in zip(validator.STAGES, boundaries)]
    return {"protocol_id": "continufy-live-latency-v1.0.0", "observation_id": f"obs_{number:03d}",
            "creator_id": f"creator_{(number - 1) % 3 + 1}", "session_id": f"session_{(number - 1) % 3 + 1}",
            "session_start_at": "2026-01-01T00:00:00.000Z", "occurred_at": stamp(0), "eligible": True,
            "exclusion_reason": None, "duplicate_of": None, "stages": stages, "provenance": [provenance("p1")],
            "terminal_status": "published", "published_at": stamp(55), "abandoned_at": None,
            "abandoned_by": None, "abandonment_reason": None, "outcome": None}


def invalid_case(name: str) -> dict:
    item = record()
    if name == "schema_extra_property": item["undeclared"] = True
    elif name == "stage_order": item["stages"][0], item["stages"][1] = item["stages"][1], item["stages"][0]
    elif name == "stage_chronology": item["stages"][2]["started_at"] = stamp(0)
    elif name == "missingness_timestamp":
        item["stages"][2].update(status="unobservable", status_reason="audit unavailable", expected_source="editor audit log", started_at=stamp(3), completed_at=None)
    elif name == "missing_provenance": item["occurred_at"]["provenance_id"] = "absent"
    elif name == "interval_overlap":
        item["stages"][2]["attempts"] = [{"attempt_id": "a1", "started_at": stamp(3), "ended_at": stamp(43),
            "actor_id": "human-1", "tool_name": "editor", "tool_version": "1", "automation": "manual",
            "classification_rationale": "human executed edit", "status": "succeeded", "is_rework": False,
            "supersedes_attempt_id": None, "failure_reason": None,
            "active_intervals": [{"start": stamp(4)["at"], "end": stamp(20)["at"], "provenance_id": "p1"}],
            "wait_intervals": [{"start": stamp(10)["at"], "end": stamp(30)["at"], "provenance_id": "p1", "reason": "tool_processing"}] }]
    elif name == "terminal_timestamp": item["published_at"] = stamp(56)
    elif name == "outcome_window":
        item["provenance"].append(provenance("p2")); item["outcome"] = {
            "views_168h": 10, "measured_at": "2026-01-08T00:54:00.000Z", "provenance_id": "p2"}
    return item


class ExecutionValidatorTests(unittest.TestCase):
    def test_declared_valid_fixtures(self):
        self.assertEqual(CASES["valid"], ["published_complete"])
        self.assertEqual(validator.validate_observation(record()), [])

    def test_every_declared_invalid_fixture_fails(self):
        for name in CASES["invalid"]:
            with self.subTest(name=name): self.assertTrue(validator.validate_observation(invalid_case(name)))

    def test_dataset_order_and_duplicate_ids(self):
        self.assertTrue(validator.validate_dataset([record(2), record(1)]))
        self.assertTrue(validator.validate_dataset([record(1), record(1)]))

    def test_floor_cap_inputs_and_decision_recomputation(self):
        self.assertEqual(validator.determination([record()]), "BLOCKED_BY_ACCESS_OR_PROVENANCE")
        cohort = [record(i) for i in range(1, 31)]
        cohort.sort(key=lambda o: (o["session_start_at"], o["session_id"], o["occurred_at"]["at"], o["observation_id"]))
        self.assertEqual(validator.validate_dataset(cohort), [])
        self.assertEqual(validator.determination(cohort), "LATENCY_BOTTLENECK_IDENTIFIED")
        self.assertIn("dataset: eligible-moment cap exceeded", validator.validate_dataset([record(i) for i in range(1, 62)]))

    def test_value_rule_recomputation(self):
        cohort = []
        for number in range(1, 31):
            item = record(number); width = number % 10 + 1
            for index, stage in enumerate(item["stages"]):
                stage["started_at"], stage["completed_at"] = stamp(index * width), stamp((index + 1) * width)
            item["published_at"] = stamp(6 * width)
            item["provenance"].append(provenance("p2"))
            measured = BASE + timedelta(minutes=6 * width, hours=168)
            item["outcome"] = {"views_168h": 6 * width, "measured_at": measured.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "provenance_id": "p2"}
            cohort.append(item)
        self.assertEqual(validator.determination(cohort), "NO_MEANINGFUL_LATENCY_BOTTLENECK")

    def test_cli_reports_null_readiness(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.json"; path.write_text(json.dumps([record()]))
            result = subprocess.run([sys.executable, str(ROOT / "validate_observations.py"), str(path)],
                                    check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("collection_readiness: NULL", result.stdout)


if __name__ == "__main__": unittest.main()
