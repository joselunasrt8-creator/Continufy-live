# Issue 11: prospective AI-assisted content revenue operation pilot protocol

**Protocol ID:** `continufy-ai-content-paid-pilot-v1.0.0`  
**Status:** frozen before acquisition or execution  
**Frozen on:** 2026-09-08  
**Terminal determination:** `READY_FOR_PROSPECTIVE_PAID_PILOT`  
**Scope:** measurement and governance only. Readiness permits Issue #12 to seek a
customer; it does not permit outreach under this issue, pilot execution,
publication, autonomous publishing, product development, or Issue #13.

## 1. Question, unit, and offer

Can a bounded AI-assisted content operation transform one source asset into a
multi-platform content package with lower production burden and sufficient
downstream commercial value to justify repeat customer payment?

The **unit of pilot** is one paid engagement with one customer, one authorized
source asset, one frozen deliverable package, and one continuation decision.
The **unit of content asset** is one independently reviewable deliverable made
from that source (for example a video, article, post, caption set, or thumbnail),
including rejected, failed, and cancelled assets. Assets are not impressions,
platform renditions, revisions, or source excerpts.

Eligible sources are customer-owned or legitimately licensed recordings,
livestream recordings, webinars, podcasts, interviews, presentations, and
recorded subject-matter sessions. They must be complete, retrievable,
permissioned for transformation and intended distribution, and supplied before
selection without consulting pilot outcomes. Clipping is only one possible
transformation; it is neither required nor the business category. Synthetic,
unlicensed, inaccessible, already transformed, or outcome-selected sources are
ineligible.

Before work, the parties freeze a package of **1–8 assets**, drawn from at least
two permitted forms (`short_form_video`, `long_form_video`, `written`,
`title`, `thumbnail`, `caption`), for at most three named destinations. Research,
selection, transformations, packaging metadata, review, revisions, and (only
when separately authorized) distribution may be included. At most two revision
rounds are included. Scope additions are separately recorded and excluded from
the primary burden comparison. The **$250–$400** range is an experimental offer
parameter only, recorded as the proposed price; it is not a validated market
price and does not imply payment.

## 2. Dependencies and authority gates

Issue #12 may begin acquisition only after this frozen instrument passes its
tests. A real pilot may not begin until a customer-specific record has all of:

1. signed service agreement and explicit proposed and actually paid amounts;
2. source ownership/licence, transformation permission, observation consent,
   and permission to retain the minimized evidence described below;
3. named customer approver and publication controller;
4. frozen source, assets, destinations, baseline method, price, dates, and
   outcome access;
5. payment settlement evidence (not an invoice, promise, or interest);
6. no unresolved privacy, credential, or platform-policy dependency.

No proposal, protocol validation, service acceptance, or payment grants
publication authority. Each destination is `not_authorized`,
`customer_publishes`, or `provider_manual_publish`. Publishing requires explicit
artifact-backed authority for the exact approved asset and destination.
Credentials must never enter this repository. Autonomous publication is
prohibited. The customer may publish; a human provider may publish only through
a separately authorized manual act. Revocation immediately blocks unpublished
assets.

This issue creates no real record and satisfies none of these execution gates.

## 3. Workflow and stage taxonomy

Every asset records these ordered stages, even when `not_required` or
`not_reached`:

1. `source_intake`; 2. `research_selection`; 3. `transformation`;
4. `packaging`; 5. `human_review`; 6. `revision`; 7. `approval`;
8. `publishing_distribution`; 9. `performance_observation`;
10. `continuation_decision`.

The transformation may produce permitted short-form, long-form, or written
assets; packaging may produce titles, thumbnails, or captions. Every performed
stage is classified `human`, `ai_assisted`, or `ai_executed_human_reviewed`:

* `human`: a human performs the material operation;
* `ai_assisted`: AI proposes or assists and a human materially performs/selects;
* `ai_executed_human_reviewed`: AI performs the transform, but a human reviews
  the complete output before it can advance.

There is no autonomous approval or publication class. `human_review` and
`approval` must be human, with named pseudonymous actors, timestamps, decision,
and evidence. AI use is a workflow fact, not evidence of usefulness or value.

## 4. Time, rework, and burden

All instants are RFC 3339 UTC. Turnaround starts when the eligible source,
permissions, scope, and required inputs are all received (`ready_at`) and ends
when the package is first approved (`approved_at`). Report elapsed wall time;
do not call customer or system delay labor. If cancelled first, turnaround is
censored at cancellation. Publishing and outcome time are outside turnaround.

Each stage has attempts with non-overlapping intervals classified as:

* `active_labor`: direct human production or evaluation;
* `waiting`: processing, queue, scheduling, or external dependency;
* `approval`: customer/authorized-reviewer evaluation time;
* `rework`: active labor repeated because a prior output was rejected or failed.

Rework is a subset of active labor, not added twice. Per-asset active minutes are
the union of active intervals; approval and waiting are separate. Pilot totals
are sums across assets, and shared work is allocated once using a frozen stated
rule. The comparison baseline is the customer's contemporaneous, documented
time estimate or a prospectively timed non-AI method for the same package; its
method and uncertainty must be explicit. Missing baseline means burden change
is `unknown`, never zero or reduced.

Direct cost is actual incremental labor cost (active hours × frozen loaded
hourly rate) plus itemized AI/API, contractor, media, and platform costs. It
excludes customer price, general overhead, sunk development, and unpaid time
unless an explicit zero rate is justified. `direct_cost_total` must equal the
components; `cost_per_delivered_asset` is total direct cost divided by approved
deliverable count, and is null when that count is zero. Currency is frozen per
pilot. Proposed price, invoice amount, amount actually settled, refund, and net
paid are distinct. A promise, invoice, deposit authorization, or interest is
not payment.

## 5. Provenance, privacy, and corrections

Source and content records contain pseudonymous IDs, source type, owner/license
attestation reference, immutable source fingerprint, source time range(s),
transformation lineage, AI tool/model/version where used, prompt/input reference
(not sensitive prompt contents), human decisions, and hashes of approved assets.
Every authority, payment, publication, metric, click, lead, sale, revenue, and
continuation claim requires a typed evidence reference, collector, collection
time, controlled-storage flag, and scope. Raw evidence remains outside Git.
Corrections append a revision with reason and prior-record hash; never overwrite.

Collect only data necessary for the frozen measures. Use pseudonymous customer,
actor, source, lead, and purchaser IDs; aggregate audience metrics where
possible. Do not store names, contact details, credentials, private messages,
raw customer content, payment instruments, or personal lead/customer data in
this repository. Record consent, retention deadline, access owner, and deletion
status. Synthetic fixtures use `SYNTH-` identifiers and can never count as
empirical observations.

## 6. Outcomes and attribution

Platform observations occur at fixed windows from each legitimate publication:
`24h`, `7d`, and `30d`; record unavailable windows rather than substituting a
later rolling count. Views are platform-defined qualified view counts. Retention
is the platform-defined average watch percentage or average watch seconds,
including metric definition and denominator. Cross-platform values are reported
separately unless definitions match. Views and retention are attention signals,
not revenue.

Clicks require a destination-specific tagged link or platform analytics record.
Leads require a frozen qualifying event and pseudonymous deduplication rule.
Sales require a settled transaction linked by a permitted deterministic key.
Revenue is net settled revenue (gross settled receipts less refunds, chargebacks,
and taxes collected) within 30 days of publication. It is **attributable** only
when a prospectively configured unique link/code or deterministic first-party
join connects the content exposure/click to that transaction. Self-report,
temporal proximity, views, correlation, or campaign-level lift is not
attributable evidence. Unlinked revenue may be recorded as `observed_unattributed`
but never summed as attributable.

Every claimed funnel event records its evidence and attribution method plus
uncertainty: `deterministic`, `ambiguous_multi_touch`, `self_report_only`, or
`unattributed`. Report counts and revenue by uncertainty; do not collapse them.
No observational association establishes causal lift. Operational usefulness
does not establish revenue causality.

At approval and after the 30-day window, the customer answers frozen 1–5 items
for output usability, brand fit, time saved, and overall usefulness, plus a
yes/no acceptance and optional comment. Missing answers stay missing. The
continuation decision is captured after the 30-day observation as
`paid_follow_on_settled`, `offered_not_paid`, `declined`, `undecided`, or
`not_observed`. Repeat payment is true only for a separate follow-on engagement
whose funds settled; the pilot payment itself never qualifies.

## 7. Failure, missingness, stopping, and determination

Each attempt is `approved`, `rejected`, `failed`, or `cancelled`, with reason,
actor, time, and whether it triggered revision. Revisions never erase originals.
Customer cancellation records initiator, time, stated reason, work completed,
refund, and the then-current asset states. Provider failure is not recoded as
customer cancellation. An undelivered or unpublished asset remains in the
denominator. Publication failure cannot be silently excluded.

Missing values are null with one reason: `not_applicable`, `not_authorized`,
`not_available_from_platform`, `not_observed`, `customer_declined`,
`evidence_lost`, or `window_not_elapsed`. No imputation converts missingness to
zero. Zero is valid only with evidence that the measurement was available and
observed. Late observations are flagged and do not replace frozen-window values.

Stop after the first **5 completed eligible paid pilots**, or after **10 enrolled
customers**, or **90 days after the first enrollment**, whichever occurs first.
Stop immediately for consent/authority revocation, material privacy or security
breach, or inability to preserve provenance; report the affected pilot as
stopped. Never stop because results look favorable or unfavorable. Analyze all
enrolled pilots, including cancellation and failure.

Execution (Issue #13 only) must emit exactly one terminal determination:

* `REPEAT_PAYMENT_SIGNAL_OBSERVED`: at least 3 completed pilots, at least 2 have
  a separate settled follow-on payment, and no governance stop occurred;
* `USEFULNESS_WITHOUT_REPEAT_PAYMENT`: at least 3 completed pilots, median
  overall usefulness is at least 4 among respondents, but the preceding repeat
  payment rule is not met;
* `NO_REPEAT_PAYMENT_SIGNAL`: at least 3 completed pilots and neither preceding
  rule is met;
* `PILOT_EVIDENCE_INSUFFICIENT`: fewer than 3 completed pilots or required
  primary burden, payment, usefulness, or continuation data are missing; or
* `PILOT_STOPPED_FOR_GOVERNANCE`: a mandatory governance stop occurred.

Precedence is governance stop, insufficient evidence, repeat payment,
usefulness-only, then no signal. These bounded labels do not validate software,
causal revenue lift, a market price, autonomous operation, or a product. A
successful pilot is not product authorization.

## 8. Frozen invariants and validation boundary

AI usage ≠ value. Content volume ≠ business outcome. Views ≠ revenue.
Correlation ≠ attribution. Interest ≠ willingness to pay. One payment ≠
recurring demand. Service execution ≠ software validation. Operational
usefulness ≠ causal revenue lift. Successful pilot ≠ product authorization.
Proposal ≠ authority. Validation ≠ execution.

`pilot.schema.json` defines the normative record shape.
`validate_pilot.py` enforces cross-field semantics that JSON Schema alone cannot
freeze, and `test_pilot.py` supplies synthetic regression cases. Passing them
means only that this prospective measurement/governance instrument is internally
consistent. Version 1.0.0 is immutable after first enrollment; any later change
requires a new version and documented amendment.
