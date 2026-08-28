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
