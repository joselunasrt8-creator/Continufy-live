# Continufy-live

`Continufy-live` is a bounded empirical research repository investigating whether AI-assisted content operations solve a measurable workflow problem worth further testing.

It is **not currently a clipping product, production architecture, validated business, or evidence of customer demand**.

The repository began with a livestream-clipping feasibility investigation and later added a broader prospective paid-pilot protocol. Those are related research tracks, not evidence that clipping or any particular product form has been selected.

## Governing question

> Is there a real content-operation workflow problem for which an AI-assisted intervention produces measurable value under legitimate access and prospective observation?

The repository should answer that question before product architecture is allowed to outrun evidence.

## Research lineage

### 1. Public-data feasibility baseline

The initial investigation examined what could legitimately be learned from public data about livestream clipping operations.

The investigation, method, evidence limits, and determination are in [`research/issue-1-feasibility.md`](research/issue-1-feasibility.md). Machine-readable companion artifacts include:

- [`research/source-inventory.csv`](research/source-inventory.csv)
- [`research/observation.schema.json`](research/observation.schema.json)
- [`research/pilot/observations.csv`](research/pilot/observations.csv)
- [`research/pilot/acquisition-log.csv`](research/pilot/acquisition-log.csv)

Run:

```text
python3 scripts/validate_baseline.py
```

The validator operates without network access or third-party packages.

The important boundary from this work is that public observations alone cannot establish the complete creator-controlled workflow, legitimate access, provenance, or the intervention's effect on that workflow.

### 2. Frozen latency observation path

A participant-acquisition protocol exists for the earlier latency investigation and supports **manual participant outreach only**.

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

Until a qualifying participant provides the required legitimate access, provenance, and observation authority, Issue #7 and Issue #5 remain blocked.

Do not build clipping software, automate outreach, synthesize participant evidence, or weaken the frozen latency protocol to bypass that boundary.

### 3. Prospective paid-pilot path

Issue #11 freezes a separate and broader AI-assisted content-operation pilot instrument at [`research/issue-11/PROTOCOL.md`](research/issue-11/PROTOCOL.md).

It treats clipping as only one possible transformation and preserves the earlier latency work as historical evidence rather than converting it into product validation.

Its terminal protocol-readiness determination is:

```text
READY_FOR_PROSPECTIVE_PAID_PILOT
```

That means the protocol is ready for the next prospective step defined by the research. It does **not** mean that customer demand, willingness to pay, intervention effectiveness, retention, product-market fit, or a production architecture has been demonstrated.

### Current program state

- Issue #11 is complete at `READY_FOR_PROSPECTIVE_PAID_PILOT`.
- Issue #20 has frozen clipping as a supporting transformation for the first offer at [`research/issue-20/CLIPPING_ROLE.md`](research/issue-20/CLIPPING_ROLE.md): `READY_TO_TEST_CLIPPING_AS_SUPPORTING_TRANSFORMATION`.
- Issue #18 has frozen the $300 differentiated outreach hypothesis at [`research/issue-18/OUTREACH_BRIEF.md`](research/issue-18/OUTREACH_BRIEF.md): `READY_FOR_DIFFERENTIATED_OUTREACH`.
- Issue #12 is the active gate for acquiring the first eligible paid customer and remains `MANUAL_ACQUISITION_REQUIRED` until real external evidence satisfies it.
- A public prospect-screening shortlist is in [`research/issue-12/PROSPECT_SHORTLIST.md`](research/issue-12/PROSPECT_SHORTLIST.md); it is desk research only and does not satisfy acquisition eligibility.
- Issue #13 is an execution surface, not an acquisition shortcut. The frozen v1 protocol governs a cohort with a stopping rule of 5 completed eligible paid pilots, 10 enrolled customers, or 90 days after first enrollment, whichever occurs first. Every enrolled pilot requires the same customer-specific authority, payment, scope, provenance, and measurement gates. Additional outreach or enrollment requires explicit acquisition authorization; Issue #13 alone does not provide it.

Run its dependency-free semantic checks with:

```text
python3 research/issue-11/test_pilot.py
python3 research/issue-11/validate_pilot.py research/issue-11/fixtures/valid_not_started.json
```

## Current evidence state

The repository currently supports conclusions about **research readiness and evidence boundaries**, not business validation.

Supported:

- a bounded public-data feasibility baseline exists;
- public evidence has known limitations;
- a frozen latency-observation protocol exists;
- participant access is required for claims that depend on private workflow state or provenance;
- a broader prospective paid-pilot protocol exists and has semantic validation machinery; and
- clipping has not been established as the uniquely correct intervention.

Not yet established:

- that latency is the primary customer problem;
- that AI clipping creates measurable economic value;
- that the broader content-operation intervention creates measurable economic value;
- that a customer will pay under the frozen pilot terms;
- that a participant will retain the intervention after the experiment;
- that the intervention beats a simpler baseline;
- that observed improvements generalize beyond a participant or workflow;
- that Continufy-live should become a standalone product; or
- that any specific production architecture is justified.

## Claim ladder

Claims should advance only when the evidence required for the next claim exists.

```text
Protocol readiness
        ↓
Legitimate participant access
        ↓
Prospective baseline observation
        ↓
Governed intervention
        ↓
Measured workflow effect
        ↓
Economic / willingness-to-pay evidence
        ↓
Retention or repeated-use evidence
        ↓
Broader product hypothesis
```

This is an evidence ladder, not a guarantee that every rung will be reached. A negative or null result may terminate the product hypothesis.

## Experimental discipline

Future work should preserve these rules:

1. **Observation before explanation** — do not assume the bottleneck is editing, clipping, publishing, or another stage before measuring it.
2. **Prospective criteria** — define inclusion, measurement, and decision rules before observing the intervention outcome.
3. **Legitimate access** — do not infer private workflow facts that require participant authority or provenance.
4. **Strong baseline** — compare the intervention against the participant's real baseline or a justified simpler alternative.
5. **No synthetic success** — fixtures may test machinery but cannot substitute for participant observations or economic evidence.
6. **Bounded claims** — protocol readiness, workflow improvement, willingness to pay, retention, and market demand are different claims.
7. **Preserve negative results** — a failed intervention, null effect, or refusal to pay is evidence.
8. **Stop when blocked** — lack of legitimate evidence is a research boundary, not permission to invent another proxy.

## Business-model boundary

The frozen v1 experiment tests a **paid customer-service model**: transform one authorized customer-owned or licensed recording into a bounded multi-platform package and observe burden, usefulness, payment, and continuation.

An **AI-native owned-media model** is economically and operationally different. It may begin with an original idea or research corpus, generate new audiovisual assets, publish through an operator-controlled channel, accumulate audience and intellectual property, and monetize through platform revenue, sponsorships, affiliates, licensing, products, or memberships. That model has no external pilot customer and is therefore outside the eligible-source, payment, approval, and continuation semantics of v1.

Course pages, creator claims, public view counts, and tool demonstrations may motivate hypotheses or inform workflow design. They do not establish reproducible production economics, attributable revenue, durable audience demand, or owned-media viability. Testing that model requires a separate prospective protocol and evidence record, now tracked by [Issue #17](https://github.com/joselunasrt8-creator/Continufy-live/issues/17); its observations must not be merged into the paid-service cohort or used to amend v1 after enrollment.

## Relationship to the Continufy ecosystem

Continufy-live is a domain research surface. It may test Continufy components when doing so answers a prospectively defined research question, but it is not required to validate the Continufy architecture as a whole.

Likewise, successful use of another Continufy component inside this repository would establish only the evidence actually measured in that experiment.

```text
Research readiness ≠ product readiness
Protocol validity ≠ intervention effectiveness
Workflow improvement ≠ willingness to pay
Willingness to pay ≠ market demand
AI capability ≠ customer value
Internal validation ≠ independent adoption
```

## Current objective

The highest-value next evidence is not additional product architecture. It is legitimate prospective observation of a real workflow under the applicable frozen protocol, followed by a measured intervention only when the protocol permits it.

The repository should remain capable of concluding that:

- the hypothesized problem is not important;
- clipping is not the relevant intervention;
- AI assistance does not materially improve the workflow;
- the improvement is real but not economically valuable;
- the customer will not pay or retain it;
- a simpler intervention performs equally well; or
- the opportunity is strong enough to justify a narrower product hypothesis.

Any of those is a legitimate research result.
