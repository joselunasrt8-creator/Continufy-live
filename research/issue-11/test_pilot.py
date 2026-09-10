#!/usr/bin/env python3
"""Regression tests for false-valid Issue 11 pilot states."""
import json
import unittest
from pathlib import Path

from validate_pilot import ValidationError, validate

FIXTURE = Path(__file__).parent / "fixtures" / "valid_not_started.json"


class PilotValidationTests(unittest.TestCase):
    def record(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def invalid(self, record, phrase):
        with self.assertRaisesRegex(ValidationError, phrase):
            validate(record)

    def test_valid_synthetic_not_started_fixture(self):
        validate(self.record())

    def test_ai_usage_cannot_replace_stage_classification(self):
        record = self.record()
        record["assets"][0]["stages"][2]["classification"] = "not_applicable"
        self.invalid(record, "classification")

    def test_ai_usage_cannot_be_proof_of_value(self):
        record = self.record()
        record["claims"]["ai_usage_proves_value"] = True
        self.invalid(record, "proof of value")

    def test_views_cannot_be_revenue(self):
        record = self.record()
        record["outcomes"][0]["claimed_as_revenue"] = True
        self.invalid(record, "not revenue")

    def test_revenue_requires_deterministic_evidence(self):
        record = self.record()
        record["outcomes"].append({"asset_id": "SYNTH-ASSET-1", "window": "30d", "metric": "net_revenue", "value": 50, "missing_reason": None, "evidence_ref": "SYNTH-EVIDENCE", "attribution": "self_report_only", "claimed_as_revenue": True})
        self.invalid(record, "attributable evidence")

    def test_repeat_payment_requires_follow_on_settlement(self):
        record = self.record()
        record["continuation"]["decision"] = "paid_follow_on_settled"
        self.invalid(record, "separate settled")

    def test_publication_requires_authority(self):
        record = self.record()
        record["assets"][0].update(published=True, destination="channel-a")
        self.invalid(record, "explicit matching authority")

    def test_inconsistent_labor_and_cost_totals_fail(self):
        record = self.record()
        record["assets"][0]["active_minutes"] += 1
        self.invalid(record, "active_minutes")
        record = self.record()
        record["costs"]["direct_cost_total"] += 1
        self.invalid(record, "cost total")

    def test_synthetic_execution_is_not_empirical(self):
        record = self.record()
        record["execution_gate"].update(service_agreement_ref="SYNTH-AGREEMENT", source_permission_ref="SYNTH-PERMISSION", observation_consent_ref="SYNTH-CONSENT", scope_frozen=True, approver_id="SYNTH-APPROVER", publication_controller_id="SYNTH-CONTROLLER", payment_settlement_ref="SYNTH-PAYMENT", dependencies_satisfied=True)
        record["pilot_status"] = "active"
        self.invalid(record, "cannot be empirical")

    def test_execution_before_dependencies_fails(self):
        record = self.record()
        record["synthetic"] = False
        record["pilot_id"] = "pilot-1"
        record["customer_id"] = "customer-1"
        record["source"]["source_id"] = "source-1"
        record["pilot_status"] = "active"
        self.invalid(record, "before dependencies")


if __name__ == "__main__":
    unittest.main()
