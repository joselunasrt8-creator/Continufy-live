#!/usr/bin/env python3
"""Dependency-free semantic validator for frozen Issue 9 recruitment records."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "recruitment.schema.json").read_text(encoding="utf-8"))
STATES = set(SCHEMA["properties"]["recruitment_state"]["enum"])
TERMINAL = {"NO_RESPONSE", "DECLINED", "INELIGIBLE", "DUPLICATE", "WITHDRAWN", "CANDIDATE_FOR_GATE_VERIFICATION"}
TRANSITIONS = {
    "NOT_CONTACTED": {"CONTACTED", "INELIGIBLE", "DUPLICATE"},
    "CONTACTED": {"CONTACTED", "NO_RESPONSE", "DECLINED", "INTERESTED", "INELIGIBLE", "WITHDRAWN"},
    "INTERESTED": {"ACCESS_DISCUSSION_REQUIRED", "DECLINED", "INELIGIBLE", "WITHDRAWN"},
    "ACCESS_DISCUSSION_REQUIRED": {"CANDIDATE_FOR_GATE_VERIFICATION", "DECLINED", "INELIGIBLE", "WITHDRAWN"},
}
GATES = [f"G{i:02d}" for i in range(1, 12)]
DISCUSSION_GATES = GATES[2:]
SENSITIVE_KEYS = {"password", "token", "credential", "email", "message", "message_body", "private_message", "footage", "creator_name", "contact_information"}


class ValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid RFC3339 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        fail("timestamps require an offset")
    return parsed.astimezone(timezone.utc)


def validate(record: dict) -> None:
    if not isinstance(record, dict):
        fail("record must be an object")
    required = set(SCHEMA["required"])
    if set(record) != required:
        fail(f"record fields differ; missing={sorted(required-set(record))}, extra={sorted(set(record)-required)}")
    if SENSITIVE_KEYS & set(record):
        fail("sensitive/private fields are prohibited")
    props = SCHEMA["properties"]
    if record["protocol_id"] != props["protocol_id"]["const"]:
        fail("invalid protocol_id")
    for key in ("candidate_type", "acquisition_channel", "market_segment", "determination", "outreach_policy", "recruitment_state", "response_classification", "service_relationship_status", "research_discussion_status", "research_consent_status", "observation_authority_status", "terminal_recruitment_status"):
        if record[key] not in props[key]["enum"]:
            fail(f"invalid {key}")
    if record["acquisition_channel"] == "OTHER_CLASSIFIED" and not record["channel_detail"]:
        fail("OTHER_CLASSIFIED requires channel_detail")
    if record["outcome_blind_confirmed"] is not True or record["prohibited_selection_factors"] != []:
        fail("outcome-aware selection is prohibited")
    if not isinstance(record["synthetic"], bool):
        fail("synthetic must be boolean")
    synth_prefixes = all(str(record[k]).startswith("SYNTH-") for k in ("candidate_id", "identity_ref", "source_reference"))
    if record["synthetic"] != synth_prefixes:
        fail("synthetic records and identifiers must be unmistakably synthetic")
    if record["synthetic"] and any(not p["reference"].startswith("SYNTH-") for p in record["provenance"]):
        fail("synthetic fixtures cannot contain real recruitment evidence")
    allowed_basis = set(props["eligibility_basis"]["items"]["enum"])
    if not set(record["eligibility_basis"]) <= allowed_basis:
        fail("invalid eligibility basis")
    allowed_exclusions = set(props["exclusion_reasons"]["items"]["enum"])
    if not set(record["exclusion_reasons"]) <= allowed_exclusions:
        fail("invalid exclusion reason")
    required_basis = {"SHORT_FORM_USE_OR_INTENT", "LEGITIMATE_CONTACT_MECHANISM", "PLATFORM_RELEVANCE", "WORKFLOW_ACCESS_DISCUSSIBLE"}
    if record["determination"] == "INCLUDED":
        has_workflow = bool({"ACTIVE_LIVESTREAMING", "EXISTING_CLIPPING_WORKFLOW"} & set(record["eligibility_basis"]))
        if record["exclusion_reasons"] or not has_workflow or not required_basis <= set(record["eligibility_basis"]):
            fail("included record lacks deterministic eligibility")
    elif not record["exclusion_reasons"]:
        fail("excluded record requires a reason")

    duplicate = record["duplicate"]
    if set(duplicate) != {"status", "canonical_candidate_id"} or duplicate["status"] not in {"UNIQUE", "DUPLICATE"}:
        fail("invalid duplicate object")
    if duplicate["status"] == "DUPLICATE":
        if not duplicate["canonical_candidate_id"] or duplicate["canonical_candidate_id"] == record["candidate_id"]:
            fail("duplicate requires another canonical candidate")
        if record["recruitment_state"] != "DUPLICATE" or record["outreach_attempt_timestamps"]:
            fail("duplicates cannot receive outreach or inflate candidates")
    elif duplicate["canonical_candidate_id"] is not None:
        fail("unique record cannot reference a canonical duplicate")

    history = record["state_history"]
    if not history or history[0]["from"] is not None or history[0]["to"] != "NOT_CONTACTED":
        fail("history must begin at NOT_CONTACTED")
    prior = "NOT_CONTACTED"
    previous_at = instant(history[0]["at"])
    for event in history[1:]:
        at = instant(event["at"])
        if at < previous_at or event["from"] != prior or event["to"] not in TRANSITIONS.get(prior, set()):
            fail("invalid outreach transition")
        prior, previous_at = event["to"], at
    if prior != record["recruitment_state"] or prior not in STATES:
        fail("history does not end at recruitment_state")

    attempts = [instant(value) for value in record["outreach_attempt_timestamps"]]
    limit = 1 if record["outreach_policy"] == "MARKETPLACE_SINGLE_APPLICATION" else 2
    if len(attempts) > limit:
        fail("outreach attempt limit exceeded")
    if any(b - a < timedelta(hours=168) for a, b in zip(attempts, attempts[1:])):
        fail("outreach attempts must be at least 168 hours apart")
    contacted_events = sum(event["to"] == "CONTACTED" for event in history)
    if contacted_events != len(attempts):
        fail("CONTACTED events and attempt timestamps must correspond")
    if record["recruitment_state"] == "NO_RESPONSE":
        if len(attempts) != limit or previous_at - attempts[-1] < timedelta(hours=168):
            fail("NO_RESPONSE requires exhausted attempts and 168-hour wait")
    if record["recruitment_state"] in {"DECLINED", "WITHDRAWN"} and record["terminal_recruitment_status"] != "TERMINATED":
        fail("decline/withdrawal must terminate immediately")
    if (record["recruitment_state"] in TERMINAL) != (record["terminal_recruitment_status"] == "TERMINATED"):
        fail("terminal status inconsistent with state")
    expected_response = {
        "NOT_CONTACTED": "NONE", "CONTACTED": "NONE", "NO_RESPONSE": "NO_RESPONSE",
        "DECLINED": "DECLINED", "INTERESTED": "INTERESTED",
        "ACCESS_DISCUSSION_REQUIRED": "INTERESTED", "INELIGIBLE": "INELIGIBLE",
        "DUPLICATE": "NONE", "WITHDRAWN": "WITHDRAWN",
        "CANDIDATE_FOR_GATE_VERIFICATION": "INTERESTED",
    }
    if record["response_classification"] != expected_response[record["recruitment_state"]]:
        fail("response classification inconsistent with state")

    if record["market_segment"] == "PERFORMANCE_DISTRIBUTION" and record["creator_workflow_access"]:
        fail("performance campaign cannot imply creator workflow authority")
    if record["service_relationship_status"] in {"ACCEPTED", "ACTIVE", "ENDED"} and record["research_consent_status"] == "AGREED_FOR_GATE_VERIFICATION":
        consent_refs = [p for p in record["provenance"] if p["type"] == "RESEARCH_CONSENT_ARTIFACT" and p["controlled_storage"]]
        if not consent_refs:
            fail("service acceptance cannot imply research consent")

    for provenance in record["provenance"]:
        if set(provenance) != {"type", "reference", "controlled_storage", "scope"}:
            fail("invalid provenance fields")
        if provenance["type"] not in props["provenance"]["items"]["properties"]["type"]["enum"]:
            fail("invalid provenance type")
        if provenance["type"] in {"PRIVATE_COMMUNICATION", "MARKETPLACE_APPLICATION", "SERVICE_AGREEMENT", "RESEARCH_CONSENT_ARTIFACT", "OBSERVATION_AUTHORITY_ARTIFACT"} and not provenance["controlled_storage"]:
            fail("private provenance must reference controlled storage")

    if record["recruitment_state"] == "CANDIDATE_FOR_GATE_VERIFICATION":
        consent_refs = any(p["type"] == "RESEARCH_CONSENT_ARTIFACT" and p["controlled_storage"] for p in record["provenance"])
        authority_refs = any(p["type"] == "OBSERVATION_AUTHORITY_ARTIFACT" and p["controlled_storage"] for p in record["provenance"])
        conditions = [record["determination"] == "INCLUDED", duplicate["status"] == "UNIQUE", record["market_segment"] == "CREATOR_SERVICE", record["controller_identified"], record["creator_workflow_access"], record["research_discussion_status"] == "COMPLETED", record["research_consent_status"] == "AGREED_FOR_GATE_VERIFICATION", record["observation_authority_status"] == "AGREED_FOR_GATE_VERIFICATION", record["potential_issue7_gates"] == GATES, consent_refs, authority_refs]
        if not all(conditions):
            fail("candidate lacks required gate-verification conditions")
        if set(record["gate_discussion"]) != set(DISCUSSION_GATES):
            fail("G03-G11 discussions must all be present")
        if any(item["status"] != "DISCUSSIBLE" or not item["owner_source_ref"] for item in record["gate_discussion"].values()):
            fail("G03-G11 require prospective owners/sources")
    elif record["potential_issue7_gates"] and record["market_segment"] != "CREATOR_SERVICE":
        fail("non-creator-service paths cannot claim potential Issue 7 gates")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+")
    args = parser.parse_args()
    seen: dict[str, str] = {}
    count = 0
    for name in args.records:
        path = Path(name)
        record = json.loads(path.read_text(encoding="utf-8"))
        validate(record)
        if record["duplicate"]["status"] == "UNIQUE" and not record["synthetic"]:
            identity = record["identity_ref"]
            if identity in seen:
                fail(f"duplicate identity not linked: {identity}")
            seen[identity] = record["candidate_id"]
            count += 1
        print(f"PASS {path}")
    print(f"real unique candidate count: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
