#!/usr/bin/env python3
"""Synthetic semantic tests for the Issue 9 recruitment validator."""
import copy
import json
import unittest
from pathlib import Path

from validate_recruitment import GATES, ValidationError, validate

ROOT = Path(__file__).resolve().parent
BASE = json.loads((ROOT / "fixtures" / "valid_candidate.json").read_text(encoding="utf-8"))


def event(source, destination, at):
    return {"from": source, "to": destination, "at": at}


class RecruitmentValidationTests(unittest.TestCase):
    def record(self):
        return copy.deepcopy(BASE)

    def assert_invalid(self, record, contains):
        with self.assertRaisesRegex(ValidationError, contains):
            validate(record)

    def test_valid_synthetic_candidate(self):
        validate(self.record())

    def test_invalid_channel_and_segment(self):
        record = self.record()
        record["acquisition_channel"] = "UNLISTED_NETWORK"
        self.assert_invalid(record, "invalid acquisition_channel")
        record = self.record()
        record["market_segment"] = "VIRAL_CLIPS"
        self.assert_invalid(record, "invalid market_segment")

    def test_outcome_aware_selection_rejected(self):
        record = self.record()
        record["prohibited_selection_factors"] = ["high_views"]
        self.assert_invalid(record, "outcome-aware")

    def test_duplicate_has_no_outreach_and_points_to_canonical(self):
        record = self.record()
        record["candidate_id"] = "SYNTH-CAND-00000002"
        record["duplicate"] = {"status": "DUPLICATE", "canonical_candidate_id": "SYNTH-CAND-00000001"}
        record["determination"] = "EXCLUDED"
        record["exclusion_reasons"] = ["CANNOT_IDENTIFY_WORKFLOW_CONTROLLER"]
        record["recruitment_state"] = "DUPLICATE"
        record["state_history"].append(event("NOT_CONTACTED", "DUPLICATE", "2026-08-28T01:00:00Z"))
        record["terminal_recruitment_status"] = "TERMINATED"
        validate(record)
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
        self.assert_invalid(record, "duplicates cannot")

    def test_invalid_transition(self):
        record = self.record()
        record["recruitment_state"] = "CANDIDATE_FOR_GATE_VERIFICATION"
        record["state_history"].append(event("NOT_CONTACTED", "CANDIDATE_FOR_GATE_VERIFICATION", "2026-08-28T01:00:00Z"))
        record["terminal_recruitment_status"] = "TERMINATED"
        self.assert_invalid(record, "invalid outreach transition")

    def test_attempt_limit_and_interval(self):
        record = self.record()
        record["outreach_policy"] = "MARKETPLACE_SINGLE_APPLICATION"
        record["recruitment_state"] = "CONTACTED"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "CONTACTED", "2026-09-05T01:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z", "2026-09-05T01:00:00Z"]
        self.assert_invalid(record, "attempt limit")
        record = self.record()
        record["recruitment_state"] = "CONTACTED"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "CONTACTED", "2026-08-29T01:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z", "2026-08-29T01:00:00Z"]
        self.assert_invalid(record, "168 hours apart")

    def test_decline_and_withdrawal_are_terminal(self):
        for state in ("DECLINED", "WITHDRAWN"):
            record = self.record()
            record["recruitment_state"] = state
            record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", state, "2026-08-28T02:00:00Z")]
            record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
            record["terminal_recruitment_status"] = "ACTIVE"
            record["response_classification"] = state
            self.assert_invalid(record, "terminate immediately")

    def test_no_response_requires_exhaustion_and_wait(self):
        record = self.record()
        record["recruitment_state"] = "NO_RESPONSE"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "NO_RESPONSE", "2026-09-04T01:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
        record["terminal_recruitment_status"] = "TERMINATED"
        record["response_classification"] = "NO_RESPONSE"
        self.assert_invalid(record, "exhausted attempts")

    def test_service_acceptance_is_not_consent(self):
        record = self.record()
        record["service_relationship_status"] = "ACCEPTED"
        record["research_consent_status"] = "AGREED_FOR_GATE_VERIFICATION"
        self.assert_invalid(record, "service acceptance cannot imply")

    def test_researcher_as_clipper_does_not_satisfy_issue7(self):
        record = self.record()
        record["acquisition_channel"] = "RESEARCHER_AS_CLIPPER_SERVICE"
        record["service_relationship_status"] = "ACTIVE"
        record["creator_workflow_access"] = True
        record["potential_issue7_gates"] = GATES
        record["recruitment_state"] = "CANDIDATE_FOR_GATE_VERIFICATION"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "INTERESTED", "2026-08-28T02:00:00Z"), event("INTERESTED", "ACCESS_DISCUSSION_REQUIRED", "2026-08-28T03:00:00Z"), event("ACCESS_DISCUSSION_REQUIRED", "CANDIDATE_FOR_GATE_VERIFICATION", "2026-08-28T04:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
        record["terminal_recruitment_status"] = "TERMINATED"
        record["response_classification"] = "INTERESTED"
        self.assert_invalid(record, "lacks required gate-verification")

    def test_performance_campaign_cannot_imply_workflow_access(self):
        record = self.record()
        record["market_segment"] = "PERFORMANCE_DISTRIBUTION"
        record["creator_workflow_access"] = True
        self.assert_invalid(record, "performance campaign")

    def test_gate_candidate_requires_all_conditions(self):
        record = self.record()
        record["recruitment_state"] = "CANDIDATE_FOR_GATE_VERIFICATION"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "INTERESTED", "2026-08-28T02:00:00Z"), event("INTERESTED", "ACCESS_DISCUSSION_REQUIRED", "2026-08-28T03:00:00Z"), event("ACCESS_DISCUSSION_REQUIRED", "CANDIDATE_FOR_GATE_VERIFICATION", "2026-08-28T04:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
        record["terminal_recruitment_status"] = "TERMINATED"
        record["response_classification"] = "INTERESTED"
        self.assert_invalid(record, "lacks required gate-verification")

    def test_complete_conditions_allow_gate_verification_candidacy(self):
        record = self.record()
        record["recruitment_state"] = "CANDIDATE_FOR_GATE_VERIFICATION"
        record["state_history"] += [event("NOT_CONTACTED", "CONTACTED", "2026-08-28T01:00:00Z"), event("CONTACTED", "INTERESTED", "2026-08-28T02:00:00Z"), event("INTERESTED", "ACCESS_DISCUSSION_REQUIRED", "2026-08-28T03:00:00Z"), event("ACCESS_DISCUSSION_REQUIRED", "CANDIDATE_FOR_GATE_VERIFICATION", "2026-08-28T04:00:00Z")]
        record["outreach_attempt_timestamps"] = ["2026-08-28T01:00:00Z"]
        record["response_classification"] = "INTERESTED"
        record["terminal_recruitment_status"] = "TERMINATED"
        record["research_discussion_status"] = "COMPLETED"
        record["research_consent_status"] = "AGREED_FOR_GATE_VERIFICATION"
        record["observation_authority_status"] = "AGREED_FOR_GATE_VERIFICATION"
        record["creator_workflow_access"] = True
        record["potential_issue7_gates"] = GATES
        record["gate_discussion"] = {gate: {"status": "DISCUSSIBLE", "owner_source_ref": f"SYNTH-OWNER_{gate}"} for gate in GATES[2:]}
        record["provenance"] += [
            {"type": "RESEARCH_CONSENT_ARTIFACT", "reference": "SYNTH-CONSENT_0001", "controlled_storage": True, "scope": "Synthetic permission to begin gate verification"},
            {"type": "OBSERVATION_AUTHORITY_ARTIFACT", "reference": "SYNTH-AUTHORITY_0001", "controlled_storage": True, "scope": "Synthetic scoped observation authority"},
        ]
        validate(record)

    def test_private_fields_and_real_evidence_in_fixture_rejected(self):
        record = self.record()
        record["email"] = "person@example.invalid"
        self.assert_invalid(record, "fields differ")
        record = self.record()
        record["provenance"][0]["reference"] = "PUBLIC-REAL_0001"
        self.assert_invalid(record, "cannot contain real")


if __name__ == "__main__":
    unittest.main()
