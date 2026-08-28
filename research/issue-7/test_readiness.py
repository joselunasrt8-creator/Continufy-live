#!/usr/bin/env python3
"""Deterministic tests for Issue 7 readiness logic."""
import copy
import json
import unittest
from pathlib import Path

import validate_readiness as validator

ROOT = Path(__file__).resolve().parent


def registry() -> dict:
    return json.loads((ROOT / "readiness.json").read_text(encoding="utf-8"))


class ReadinessTests(unittest.TestCase):
    def test_checked_in_registry_is_valid_and_blocked(self):
        item = registry()
        self.assertEqual(validator.validate(item), [])
        self.assertEqual(item["determination"], validator.BLOCKED)
        self.assertEqual(item["blocking_gate_ids"], sorted(validator.MANDATORY_GATES))

    def test_unverified_mandatory_gate_cannot_be_ready(self):
        item = registry()
        item["determination"] = validator.READY
        self.assertTrue(any(error.startswith("determination:") for error in validator.validate(item)))

    def test_optional_views_gate_does_not_block_ready(self):
        item = registry()
        for gate in item["gates"]:
            if gate["mandatory_for_collection"]:
                gate.update(
                    status="SATISFIED",
                    evidence_type="OBSERVED_REPOSITORY_EVIDENCE",
                    evidence_source="Auditable real-world access record",
                    responsible_data_owner_or_source="identified-owner",
                    evidence_provenance_reference="immutable://access-record",
                    verified_at="2026-08-28T00:00:00.000Z",
                )
        item["blocking_gate_ids"] = []
        item["determination"] = validator.READY
        self.assertEqual(validator.validate(item), [])
        self.assertEqual(item["gates"][-1]["status"], "NOT_REQUIRED")

    def test_synthetic_or_inference_cannot_satisfy_gate(self):
        for evidence_type, source in (
            ("INFERENCE", "Access seems likely"),
            ("OBSERVED_REPOSITORY_EVIDENCE", "Synthetic fixture passed"),
        ):
            with self.subTest(evidence_type=evidence_type):
                item = registry()
                gate = item["gates"][0]
                gate.update(
                    status="SATISFIED", evidence_type=evidence_type, evidence_source=source,
                    responsible_data_owner_or_source="owner",
                    evidence_provenance_reference="immutable://record",
                    verified_at="2026-08-28T00:00:00.000Z",
                )
                self.assertTrue(any(error.startswith("G01:") for error in validator.validate(item)))

    def test_missing_evidence_fields_remain_invalid_when_satisfied(self):
        item = copy.deepcopy(registry())
        item["gates"][0]["status"] = "SATISFIED"
        errors = validator.validate(item)
        self.assertTrue(any("SATISFIED requires" in error for error in errors))

    def test_protocol_id_is_exact(self):
        item = registry()
        item["protocol_id"] = "continufy-live-latency-v1.0.1"
        self.assertTrue(any(error.startswith("protocol_id:") for error in validator.validate(item)))


if __name__ == "__main__":
    unittest.main()
