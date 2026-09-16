#!/usr/bin/env python3
"""Validate Issue 12 acquisition records without acquiring or contacting anyone."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "acquisition.schema.json").read_text(encoding="utf-8"))
TERMINALS = set(SCHEMA["properties"]["transition_determination"]["enum"])
EVIDENCE_REQUIRED = {
    "SERVICE_AGREEMENT", "PAYMENT_SETTLEMENT", "SOURCE_AUTHORITY",
    "CREATION_PERMISSION", "EVIDENCE_RETENTION_PERMISSION",
    "MEASUREMENT_PERMISSION", "DATA_ACCESS",
}
PROHIBITED_KEYS = {"name", "email", "phone", "address", "credential", "token", "password", "private_message", "payment_instrument", "raw_content"}


class ValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def parse_time(value: str | None, field: str) -> None:
    if value is None:
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid {field} timestamp") from exc
    if parsed.tzinfo is None:
        fail(f"{field} requires an offset")


def determine(record: dict) -> str:
    response = record["response_state"]
    withdrawal = record["withdrawal_cancellation"]["status"]
    if response in {"DECLINED", "INELIGIBLE", "WITHDRAWN", "CANCELLED", "NO_RESPONSE"}:
        return "NO_ELIGIBLE_PAID_PILOT_CUSTOMER_ACQUIRED"
    if withdrawal != "NONE":
        return "NO_ELIGIBLE_PAID_PILOT_CUSTOMER_ACQUIRED"
    authority_dependencies = {"SOURCE_AUTHORITY", "SOURCE_ACCESS", "CREATION_PERMISSION", "EVIDENCE_RETENTION_PERMISSION", "PUBLICATION_AUTHORITY", "MEASUREMENT_PERMISSION", "DATA_ACCESS", "APPROVER", "PUBLICATION_CONTROLLER", "PRIVACY", "CREDENTIAL", "PLATFORM_POLICY"}
    if response in {"ACCEPTED_UNPAID", "PAID"} and authority_dependencies & set(record["unresolved_dependencies"]):
        return "BLOCKED_BY_AUTHORITY_OR_ACCESS"
    if eligible(record):
        return "PAID_PILOT_CUSTOMER_ELIGIBLE"
    return "MANUAL_ACQUISITION_REQUIRED"


def eligible(record: dict) -> bool:
    scope = record["accepted_scope"]
    source = record["source_authority"]
    offer = record["offer"]
    permissions = record["permissions"]
    evidence_types = {item["type"] for item in record["evidence"]}
    publication = permissions["publication"]
    destinations_match = scope is not None and {p["destination"] for p in publication} == set(scope["destinations"])
    publication_valid = destinations_match and all(
        p["mode"] == "NOT_AUTHORIZED" or bool(p["permission_ref"]) for p in publication
    )
    return all([
        record["response_state"] == "PAID",
        not record["synthetic"],
        scope is not None,
        offer["proposed_price"] is not None and 250 <= offer["proposed_price"] <= 400,
        offer["accepted_price"] is not None and offer["accepted_price"] > 0,
        offer["accepted_at"] is not None,
        bool(offer["service_agreement_ref"]),
        offer["settled_amount"] is not None and offer["settled_amount"] > 0,
        bool(offer["payment_settlement_ref"]),
        source["basis"] in {"CUSTOMER_OWNED", "LEGITIMATELY_LICENSED"},
        source["complete"], source["retrievable"], source["selected_before_outcomes"], bool(source["authority_ref"]),
        permissions["creation"]["status"] == "GRANTED" and bool(permissions["creation"]["permission_ref"]),
        permissions["evidence_retention"]["status"] == "GRANTED" and bool(permissions["evidence_retention"]["permission_ref"]),
        permissions["measurement_data_access"]["status"] == "GRANTED" and bool(permissions["measurement_data_access"]["permission_ref"]),
        publication_valid,
        not record["unresolved_dependencies"],
        EVIDENCE_REQUIRED <= evidence_types,
    ])


def validate(record: dict) -> None:
    if not isinstance(record, dict):
        fail("record must be an object")
    required = set(SCHEMA["required"])
    if set(record) != required:
        fail(f"record fields differ; missing={sorted(required-set(record))}, extra={sorted(set(record)-required)}")
    if PROHIBITED_KEYS & set(walk_keys(record)):
        fail("PII, private messages, credentials, payment instruments, and raw content are prohibited")
    if record["protocol_id"] != SCHEMA["properties"]["protocol_id"]["const"]:
        fail("invalid protocol_id")
    if record["transition_determination"] not in TERMINALS:
        fail("invalid terminal determination")
    if record["synthetic"] != record["candidate_id"].startswith("SYNTH-"):
        fail("synthetic status and candidate ID must correspond")
    parse_time(record["first_identified_at"], "first_identified_at")
    for key in ("presented_at", "accepted_at"):
        parse_time(record["offer"][key], f"offer.{key}")
    parse_time(record["withdrawal_cancellation"]["at"], "withdrawal_cancellation.at")
    withdrawal = record["withdrawal_cancellation"]
    if (withdrawal["status"] == "NONE") != (withdrawal["at"] is None and withdrawal["reason_ref"] is None):
        fail("withdrawal/cancellation status, timestamp, and reference are inconsistent")
    for name in ("creation", "evidence_retention", "measurement_data_access"):
        permission = record["permissions"][name]
        if (permission["status"] == "GRANTED") != bool(permission["permission_ref"]):
            fail(f"{name} grant and evidence reference are inconsistent")
    for publication in record["permissions"]["publication"]:
        if (publication["mode"] == "NOT_AUTHORIZED") != (publication["permission_ref"] is None):
            fail("publication mode and evidence reference are inconsistent")

    evidence_by_ref = {}
    for item in record["evidence"]:
        evidence_by_ref.setdefault(item["reference"], set()).add(item["type"])

    typed_refs = [
        (record["offer"]["service_agreement_ref"], "SERVICE_AGREEMENT", "service_agreement_ref"),
        (record["offer"]["payment_settlement_ref"], "PAYMENT_SETTLEMENT", "payment_settlement_ref"),
        (record["source_authority"]["authority_ref"], "SOURCE_AUTHORITY", "source_authority.authority_ref"),
        (record["permissions"]["creation"]["permission_ref"], "CREATION_PERMISSION", "creation.permission_ref"),
        (record["permissions"]["evidence_retention"]["permission_ref"], "EVIDENCE_RETENTION_PERMISSION", "evidence_retention.permission_ref"),
        (record["permissions"]["measurement_data_access"]["permission_ref"], "MEASUREMENT_PERMISSION", "measurement_data_access.permission_ref"),
    ]
    typed_refs += [
        (item["permission_ref"], "PUBLICATION_PERMISSION", f"publication[{item['destination']}].permission_ref")
        for item in record["permissions"]["publication"]
        if item["permission_ref"] is not None
    ]
    for ref, expected_type, field in typed_refs:
        if ref is not None and expected_type not in evidence_by_ref.get(ref, set()):
            fail(f"{field} must resolve to {expected_type} evidence")

    expected = determine(record)
    if record["transition_determination"] != expected:
        fail(f"transition determination must be {expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+")
    args = parser.parse_args()
    eligible_count = 0
    for filename in args.records:
        record = json.loads(Path(filename).read_text(encoding="utf-8"))
        validate(record)
        eligible_count += record["transition_determination"] == "PAID_PILOT_CUSTOMER_ELIGIBLE"
        print(f"PASS {filename}: {record['transition_determination']}")
    if eligible_count > 1:
        fail("Issue 12 permits exactly one eligible paid-pilot customer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
