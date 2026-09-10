#!/usr/bin/env python3
"""Dependency-free semantic validator for Issue 11 pilot records."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "pilot.schema.json").read_text(encoding="utf-8"))
PROTOCOL_ID = "continufy-ai-content-paid-pilot-v1.0.0"
STAGES = [
    "source_intake", "research_selection", "transformation", "packaging",
    "human_review", "revision", "approval", "publishing_distribution",
    "performance_observation", "continuation_decision",
]
PERFORMED_CLASSES = {"human", "ai_assisted", "ai_executed_human_reviewed"}
ATTRIBUTABLE_METRICS = {"clicks", "leads", "sales", "net_revenue"}


class ValidationError(ValueError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        fail("timestamp requires an offset")
    return parsed


def validate(record: dict) -> None:
    required = set(SCHEMA["required"])
    if not isinstance(record, dict) or set(record) != required:
        fail("record fields differ from the frozen schema")
    if record["protocol_id"] != PROTOCOL_ID:
        fail("invalid protocol identity")
    claim_keys = set(SCHEMA["properties"]["claims"]["required"])
    if set(record["claims"]) != claim_keys or any(record["claims"].values()):
        fail("workflow facts or observations cannot be asserted as proof of value")
    ids = (record["pilot_id"], record["customer_id"], record["source"]["source_id"])
    if record["synthetic"] != all(value.startswith("SYNTH-") for value in ids):
        fail("synthetic status and identifiers are inconsistent")

    gate = record["execution_gate"]
    gate_refs = [gate[key] for key in ("service_agreement_ref", "source_permission_ref", "observation_consent_ref", "approver_id", "publication_controller_id", "payment_settlement_ref")]
    actual_gate = all(gate_refs) and gate["scope_frozen"] and record["source"]["eligible"]
    if gate["dependencies_satisfied"] != bool(actual_gate):
        fail("execution dependencies are not truthfully represented")
    if record["pilot_status"] != "not_started" and not gate["dependencies_satisfied"]:
        fail("pilot execution represented before dependencies are satisfied")
    if record["synthetic"] and record["pilot_status"] != "not_started":
        fail("synthetic fixtures cannot be empirical pilot execution")

    scope = record["scope"]
    if not 1 <= scope["asset_count"] <= 8 or len(set(scope["forms"])) < 2:
        fail("scope must contain 1-8 assets across at least two forms")
    if scope["revision_limit"] != 2 or not 1 <= len(set(scope["destinations"])) <= 3:
        fail("invalid bounded scope")
    if len(record["assets"]) != scope["asset_count"]:
        fail("asset count does not match frozen scope")

    authorities = {item["destination"]: item for item in record["publication_authorities"]}
    for asset in record["assets"]:
        if [stage["name"] for stage in asset["stages"]] != STAGES:
            fail("stages must use canonical order")
        for stage in asset["stages"]:
            if stage["status"] == "performed":
                if stage["classification"] not in PERFORMED_CLASSES or not stage["actor_id"]:
                    fail("performed stage lacks human/AI classification or actor")
            elif stage["classification"] != "not_applicable" or stage["actor_id"] is not None:
                fail("unperformed stage classification must be not_applicable")
            if stage["name"] in {"human_review", "approval"} and stage["status"] == "performed" and stage["classification"] != "human":
                fail("review and approval are human boundaries")
            for interval in stage["intervals"]:
                if instant(interval["end"]) < instant(interval["start"]):
                    fail("interval ends before it starts")
        calculated = {kind: 0.0 for kind in ("active_labor", "waiting", "approval", "rework")}
        for stage in asset["stages"]:
            for interval in stage["intervals"]:
                calculated[interval["kind"]] += (instant(interval["end"]) - instant(interval["start"])).total_seconds() / 60
        for kind, field in (("active_labor", "active_minutes"), ("waiting", "waiting_minutes"), ("approval", "approval_minutes"), ("rework", "rework_minutes")):
            if abs(calculated[kind] - asset[field]) > 0.001:
                fail(f"inconsistent {field}")
        if asset["rework_minutes"] > asset["active_minutes"]:
            fail("rework must be a subset of active labor")
        if asset["published"]:
            authority = authorities.get(asset["destination"])
            if not authority or authority["mode"] == "not_authorized" or not authority["authority_ref"] or asset["publication_authority_ref"] != authority["authority_ref"]:
                fail("publication lacks explicit matching authority")

    costs = record["costs"]
    components = sum(costs[key] for key in ("labor", "ai_api", "contractor", "media", "platform"))
    if abs(components - costs["direct_cost_total"]) > 0.001:
        fail("direct cost total is inconsistent")
    approved = sum(asset["status"] == "approved" for asset in record["assets"])
    expected_cpa = costs["direct_cost_total"] / approved if approved else None
    if costs["approved_asset_count"] != approved or (expected_cpa is None) != (costs["cost_per_delivered_asset"] is None):
        fail("cost-per-asset denominator is inconsistent")
    if expected_cpa is not None and abs(expected_cpa - costs["cost_per_delivered_asset"]) > 0.001:
        fail("cost per delivered asset is inconsistent")
    price = record["price"]
    if abs(price["settled"] - price["refund"] - price["net_paid"]) > 0.001:
        fail("net paid is inconsistent")

    asset_ids = {asset["asset_id"] for asset in record["assets"]}
    for outcome in record["outcomes"]:
        if outcome["asset_id"] not in asset_ids:
            fail("outcome refers to unknown asset")
        missing = outcome["value"] is None
        if missing != (outcome["missing_reason"] is not None) or missing != (outcome["evidence_ref"] is None):
            fail("missing outcome requires reason and prohibits evidence")
        if outcome["metric"] in {"views", "retention_percent", "retention_seconds"}:
            if outcome["claimed_as_revenue"] or outcome["attribution"] != "not_applicable":
                fail("attention metrics are not revenue or attribution")
        if outcome["metric"] == "net_revenue" and outcome["value"] is not None:
            if outcome["attribution"] != "deterministic" or not outcome["evidence_ref"]:
                fail("revenue claim lacks attributable evidence")
            if not outcome["claimed_as_revenue"]:
                fail("net revenue must be explicitly classified")
        elif outcome["claimed_as_revenue"]:
            fail("only attributable net revenue may be claimed as revenue")
        if outcome["metric"] in ATTRIBUTABLE_METRICS and outcome["value"] is not None and not outcome["evidence_ref"]:
            fail("funnel outcome lacks evidence")

    continuation = record["continuation"]
    repeat = continuation["decision"] == "paid_follow_on_settled"
    if repeat != (continuation["follow_on_settled"] > 0 and bool(continuation["payment_ref"])):
        fail("repeat payment requires a separate settled follow-on payment")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+")
    args = parser.parse_args()
    for filename in args.records:
        record = json.loads(Path(filename).read_text(encoding="utf-8"))
        validate(record)
        print(f"PASS {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
