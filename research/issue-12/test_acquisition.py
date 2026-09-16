#!/usr/bin/env python3
"""Regression tests for Issue 12 acquisition boundaries."""
import json
import unittest
from pathlib import Path

from validate_acquisition import ValidationError, determine, validate

FIXTURE = Path(__file__).parent / "fixtures" / "manual_acquisition_required.json"


class AcquisitionTests(unittest.TestCase):
    def record(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_unacquired_fixture_requires_manual_action(self):
        validate(self.record())

    def test_interest_is_not_paid_commitment(self):
        record = self.record()
        record["response_state"] = "INTERESTED"
        self.assertEqual(determine(record), "MANUAL_ACQUISITION_REQUIRED")

    def test_payment_does_not_supply_measurement_permission(self):
        record = self.record()
        record["response_state"] = "PAID"
        record["synthetic"] = False
        record["candidate_id"] = "candidate-001"
        record["unresolved_dependencies"] = ["MEASUREMENT_PERMISSION"]
        record["transition_determination"] = "BLOCKED_BY_AUTHORITY_OR_ACCESS"
        validate(record)

    def test_private_data_key_is_rejected(self):
        record = self.record()
        record["email"] = "not-allowed@example.invalid"
        with self.assertRaisesRegex(ValidationError, "fields differ|PII"):
            validate(record)

    def test_synthetic_record_can_never_be_eligible(self):
        record = self.record()
        record["response_state"] = "PAID"
        record["unresolved_dependencies"] = []
        self.assertNotEqual(determine(record), "PAID_PILOT_CUSTOMER_ELIGIBLE")

    def test_determination_cannot_be_manufactured(self):
        record = self.record()
        record["transition_determination"] = "PAID_PILOT_CUSTOMER_ELIGIBLE"
        with self.assertRaisesRegex(ValidationError, "must be MANUAL_ACQUISITION_REQUIRED"):
            validate(record)

    def test_withdrawal_terminates_eligibility(self):
        record = self.record()
        record["response_state"] = "WITHDRAWN"
        record["withdrawal_cancellation"] = {"status": "WITHDRAWN", "at": "2026-09-17T00:00:00Z", "reason_ref": "SYNTH-WITHDRAWAL"}
        record["transition_determination"] = "NO_ELIGIBLE_PAID_PILOT_CUSTOMER_ACQUIRED"
        validate(record)

    def eligible_record(self):
        record = self.record()
        record.update(synthetic=False, candidate_id="candidate-001", response_state="PAID", unresolved_dependencies=[])
        record["offer"].update(
            presented_at="2026-09-17T00:00:00Z", description_ref="offer-001",
            proposed_price=300, accepted_price=300,
            accepted_at="2026-09-18T00:00:00Z",
            service_agreement_ref="agreement-001", settled_amount=300,
            payment_settlement_ref="payment-001",
        )
        record["accepted_scope"] = {
            "source_id": "source-001", "source_type": "podcast", "asset_count": 2,
            "forms": ["short_form_video", "caption"], "destinations": ["destination-001"],
            "revision_limit": 2, "baseline_method": "customer contemporaneous estimate",
            "ready_at": "2026-09-19T00:00:00Z", "approver_id": "actor-approver",
            "publication_controller_id": "actor-controller",
        }
        record["source_authority"] = {"basis": "CUSTOMER_OWNED", "complete": True, "retrievable": True, "selected_before_outcomes": True, "authority_ref": "source-authority-001"}
        record["permissions"] = {
            "creation": {"status": "GRANTED", "permission_ref": "creation-001"},
            "evidence_retention": {"status": "GRANTED", "permission_ref": "retention-001"},
            "measurement_data_access": {"status": "GRANTED", "permission_ref": "measurement-001"},
            "publication": [{"destination": "destination-001", "mode": "NOT_AUTHORIZED", "permission_ref": None}],
        }
        types_and_refs = [
            ("SERVICE_AGREEMENT", "agreement-001"), ("PAYMENT_SETTLEMENT", "payment-001"),
            ("SOURCE_AUTHORITY", "source-authority-001"), ("CREATION_PERMISSION", "creation-001"),
            ("EVIDENCE_RETENTION_PERMISSION", "retention-001"), ("MEASUREMENT_PERMISSION", "measurement-001"),
            ("DATA_ACCESS", "data-access-001"),
        ]
        record["evidence"] = [{"type": kind, "reference": ref, "controlled_storage": True, "scope": "frozen pilot"} for kind, ref in types_and_refs]
        record["transition_determination"] = "PAID_PILOT_CUSTOMER_ELIGIBLE"
        return record

    def test_complete_real_evidence_is_eligible(self):
        validate(self.eligible_record())

    def test_reference_must_resolve_to_correct_evidence_type(self):
        record = self.eligible_record()
        for item in record["evidence"]:
            if item["reference"] == "agreement-001":
                item["type"] = "DATA_ACCESS"
                break
        record["evidence"].append({"type": "SERVICE_AGREEMENT", "reference": "unrelated-agreement", "controlled_storage": True, "scope": "frozen pilot"})
        with self.assertRaisesRegex(ValidationError, "service_agreement_ref must resolve to SERVICE_AGREEMENT evidence"):
            validate(record)

    def test_publication_reference_must_resolve_to_publication_evidence(self):
        record = self.eligible_record()
        record["permissions"]["publication"] = [{"destination": "destination-001", "mode": "CUSTOMER_PUBLISHES", "permission_ref": "publication-001"}]
        record["evidence"].append({"type": "DATA_ACCESS", "reference": "publication-001", "controlled_storage": True, "scope": "frozen pilot"})
        record["evidence"].append({"type": "PUBLICATION_PERMISSION", "reference": "unrelated-publication", "controlled_storage": True, "scope": "frozen pilot"})
        with self.assertRaisesRegex(ValidationError, "must resolve to PUBLICATION_PERMISSION evidence"):
            validate(record)


if __name__ == "__main__":
    unittest.main()
