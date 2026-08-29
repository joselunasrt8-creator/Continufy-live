#!/usr/bin/env python3
"""Dependency-free validation of the bounded Issue 7 readiness registry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROTOCOL_ID = "continufy-live-latency-v1.0.0"
READY = "READY_FOR_PROSPECTIVE_COLLECTION"
BLOCKED = "BLOCKED_BY_ACCESS_OR_PROVENANCE"
STATUSES = {"SATISFIED", "UNSATISFIED", "UNVERIFIED", "NOT_REQUIRED"}
EVIDENCE_TYPES = {
    "OBSERVED_REPOSITORY_EVIDENCE", "PUBLIC_DOCUMENTATION", "INFERENCE",
    "UNVERIFIED_REAL_WORLD_CONDITION",
}
EXPECTED_GATES = {f"G{number:02d}" for number in range(1, 13)}
MANDATORY_GATES = {f"G{number:02d}" for number in range(1, 12)}


def validate(registry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry: top level must be an object"]
    if registry.get("protocol_id") != PROTOCOL_ID:
        errors.append(f"protocol_id: must equal {PROTOCOL_ID}")
    if registry.get("value_analysis") != "omitted":
        errors.append("value_analysis: this bounded readiness artifact must omit value analysis")
    gates = registry.get("gates")
    if not isinstance(gates, list):
        return errors + ["gates: must be an array"]
    ids = [gate.get("gate_id") for gate in gates if isinstance(gate, dict)]
    if len(ids) != len(gates) or len(set(ids)) != len(ids):
        errors.append("gates: every gate must be an object with a unique gate_id")
    if set(ids) != EXPECTED_GATES:
        errors.append("gates: must contain exactly G01 through G12")
    if ids != sorted(ids):
        errors.append("gates: must be ordered by gate_id")
    required = {
        "gate_id", "requirement", "status", "mandatory_for_collection", "evidence_type",
        "evidence_source", "responsible_data_owner_or_source", "evidence_provenance_reference",
        "verified_at", "unresolved_dependency_or_blocker",
    }
    by_id: dict[str, dict[str, Any]] = {}
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("gate_id")
        by_id[gate_id] = gate
        missing = sorted(required - gate.keys())
        if missing:
            errors.append(f"{gate_id}: missing fields {missing}")
        if gate.get("status") not in STATUSES:
            errors.append(f"{gate_id}: invalid status")
        if gate.get("evidence_type") not in EVIDENCE_TYPES:
            errors.append(f"{gate_id}: invalid evidence_type")
        if not isinstance(gate.get("requirement"), str) or not gate.get("requirement"):
            errors.append(f"{gate_id}: requirement must be nonempty")
        if not isinstance(gate.get("evidence_source"), str) or not gate.get("evidence_source"):
            errors.append(f"{gate_id}: evidence_source must explicitly describe evidence or its absence")
        expected_mandatory = gate_id in MANDATORY_GATES
        if gate.get("mandatory_for_collection") is not expected_mandatory:
            errors.append(f"{gate_id}: incorrect mandatory_for_collection")
        if expected_mandatory and gate.get("status") == "NOT_REQUIRED":
            errors.append(f"{gate_id}: mandatory gate cannot be NOT_REQUIRED")
        if gate.get("status") == "SATISFIED":
            for field in ("responsible_data_owner_or_source", "evidence_provenance_reference", "verified_at"):
                if not isinstance(gate.get(field), str) or not gate[field].strip():
                    errors.append(f"{gate_id}: SATISFIED requires nonempty {field}")
            if gate.get("evidence_type") in {"INFERENCE", "UNVERIFIED_REAL_WORLD_CONDITION"}:
                errors.append(f"{gate_id}: inference or an unverified condition cannot satisfy a gate")
            source = gate.get("evidence_source", "").lower()
            if "synthetic" in source or "fixture" in source:
                errors.append(f"{gate_id}: synthetic evidence cannot satisfy a real-world gate")
    mandatory_not_satisfied = sorted(
        gate_id for gate_id in MANDATORY_GATES
        if gate_id not in by_id or by_id[gate_id].get("status") != "SATISFIED"
    )
    expected_determination = BLOCKED if mandatory_not_satisfied else READY
    if registry.get("determination") != expected_determination:
        errors.append(f"determination: must be {expected_determination}")
    if registry.get("blocking_gate_ids") != mandatory_not_satisfied:
        errors.append(f"blocking_gate_ids: must equal {mandatory_not_satisfied}")
    if registry.get("empirical_observations_collected") is not False:
        errors.append("empirical_observations_collected: must be false")
    if registry.get("issue_5_modified") is not False:
        errors.append("issue_5_modified: must be false")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", nargs="?", type=Path,
                        default=Path(__file__).with_name("readiness.json"))
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    errors = validate(registry)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"readiness registry validation: PASS\ndetermination: {registry['determination']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
