# Continufy-live empirical baseline

This repository currently contains a bounded investigation of public data for
livestream clipping operations. It is **not** a clipping product or a proposed
application architecture.

The investigation, method, evidence limits, and determination are in
[`research/issue-1-feasibility.md`](research/issue-1-feasibility.md). The
machine-readable companion artifacts are:

- [`research/source-inventory.csv`](research/source-inventory.csv)
- [`research/observation.schema.json`](research/observation.schema.json)
- [`research/pilot/observations.csv`](research/pilot/observations.csv)
- [`research/pilot/acquisition-log.csv`](research/pilot/acquisition-log.csv)

`python3 scripts/validate_baseline.py` checks the artifacts without network
access or third-party packages.

## Current execution boundary

The recruitment protocol is complete and supports **manual participant outreach only**.

Current research state:

```text
Participant acquisition protocol
        ↓
READY_FOR_MANUAL_PARTICIPANT_OUTREACH
        ↓
Manual outreach
        ↓
Legitimate access / provenance verification
        ↓
Issue #7 gates G01–G11
        ↓
Issue #5 observation collection
```

Until a qualifying participant provides legitimate access, provenance, and observation authority, Issue #7 and Issue #5 remain blocked. Do not build clipping software, automate outreach, or weaken the frozen latency protocol to bypass that boundary.

## Prospective paid-pilot protocol

Issue #11 freezes a separate, broader AI-assisted content-operation pilot
instrument at [`research/issue-11/PROTOCOL.md`](research/issue-11/PROTOCOL.md).
It treats clipping as only one possible transformation and preserves the earlier
latency research as historical evidence. Its terminal protocol-readiness
determination is `READY_FOR_PROSPECTIVE_PAID_PILOT`: Issue #12 may begin customer
acquisition, but no outreach, pilot execution, publication, or product work is
authorized by these artifacts.

Run its dependency-free semantic checks with:

```text
python3 research/issue-11/test_pilot.py
python3 research/issue-11/validate_pilot.py research/issue-11/fixtures/valid_not_started.json
```
