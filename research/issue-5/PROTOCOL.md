# Issue 5: prospective live-moment-to-publication latency protocol

**Protocol ID:** `continufy-live-latency-v1.0.0`  
**Status:** frozen before collection  
**Frozen on:** 2026-08-28  
**Scope:** measurement only; this protocol does not authorize product development,
publishing automation, or operational changes.

## 1. Question and bounded determination

For prospectively enrolled creator live sessions, where in the manual or
tool-assisted workflow from a moment occurring to its first public publication
does elapsed time accumulate, and is latency associated with the prespecified
downstream metric?

Execution MUST emit exactly one of:

* `LATENCY_BOTTLENECK_IDENTIFIED`
* `LATENCY_VALUE_UNRESOLVED`
* `NO_MEANINGFUL_LATENCY_BOTTLENECK`
* `BLOCKED_BY_ACCESS_OR_PROVENANCE`

An observation is a recorded row, not evidence by itself. Aggregated evidence
may establish association, not causation. Automation is a classification, not
effectiveness. Reduced latency is not business value. Passing validation is not
authorization. A research result is not permission to build.

## 2. Design, population, and sampling

This is a prospective, descriptive observational cohort. The **unit of
observation** is one candidate publishable moment identified from one enrolled
live session, whether it is eventually published or abandoned. Multiple moments
from a session remain separate observations but share `creator_id` and
`session_id`; summaries cluster by session and creator.

The population is English-language, creator-operated, scheduled live video
sessions for which (a) the creator or authorized team controls clipping and
publication, (b) source recording and workflow records are prospectively
accessible, and (c) the intended destination is a short-form public video post.
Recruit creators and sessions before the session starts, without consulting any
clip- or account-performance outcome. Consecutively record every candidate
moment identified during each enrolled session.

### Inclusion

1. Creator, session, and destination are enrolled before `session_start_at`.
2. The moment occurs during the enrolled session and has a source timecode.
3. A human or configured tool identifies it for possible publication no later
   than 24 hours after session end.
4. The complete attempt, including abandonment, can be represented in the
   schema with required provenance.

### Exclusion

Exclude only with one schema enum: `not_enrolled_pre_session`,
`outside_session`, `not_short_form_video`, `duplicate_candidate`,
`test_or_training_event`, `no_authority_to_observe`, or
`provenance_impossible_at_enrollment`. Never exclude because of eventual
performance, publication, failure, long latency, tool choice, or creator size.
Duplicates are the same source interval pursued for the same destination; keep
the earliest-created observation and point later records to it.

**Observation window:** starts at scheduled session start and ends at the first
of (i) first successful public publication plus the fixed outcome window, (ii)
documented abandonment, or (iii) 168 hours after session end. Unpublished,
unabandoned attempts at (iii) are right-censored, not failures or exclusions.

## 3. Canonical stages and timestamp semantics

All instants are RFC 3339 UTC with milliseconds. Preserve source-system raw
timestamp, stated timezone, clock source, and ingestion time. `occurred_at` is
derived from the platform recording start plus source timecode; all other event
times are the source-system event time, never analyst entry time. NTP offset (or
`unknown`) is recorded per source. Equal timestamps are allowed. Negative
durations are invalid unless reconciled by a documented clock correction.

| Stage | Start | Complete (canonical stage timestamp) |
|---|---|---|
| Moment occurs | first frame of candidate source interval | `occurred_at`, the same instant |
| Identified | human begins noting/selecting, or tool emits candidate | candidate is persisted with retrievable source reference (`identified_at`) |
| Captured | first retrieval/export action starts | editable media containing the intended interval is durably available (`captured_at`) |
| Edited/reframed | first content edit, trim, crop, reframe, or media transform starts | editor declares picture/audio content ready for packaging (`edited_at`) |
| Captioned/packaged | first subtitle, title, description, hashtag, thumbnail, or destination-format action starts | media and required destination metadata are ready for review (`packaged_at`) |
| Reviewed/approved | first review opens; if policy requires no review, start equals package completion | authorized human approves the exact package, or policy-backed auto-approval is logged (`approved_at`) |
| Published | first upload/API submission begins | destination returns success and the post is publicly retrievable (`published_at`) |

A stage skipped because its work is genuinely unnecessary has equal start and
complete times and `stage_status=not_required`, with a reason. Combining work
does not erase stages: use the same boundaries where inseparable and flag
`boundary_precision=coincident`. A retry creates another attempt under the same
stage. Publication means the first publicly retrievable version; later reposts
are outside the primary endpoint.

## 4. Time accounting, tools, rework, and missingness

Each stage contains ordered attempts. An attempt has start/end, actor, tool,
status, and intervals of mutually exclusive **active labor** and **wait**:

* Active human labor is stopwatch or interaction-log time during which a person
  directly performs or evaluates the candidate. Concurrent wall time is counted
  once per observation (union of intervals), even with multiple humans; person
  minutes are additionally reported but not used in latency decomposition.
* Wait/queue time is wall time after work is ready but no human is actively
  working: tool processing, upload, review queue, scheduling, dependency, or
  other wait. Every wait has exactly one enum reason.
* Uninstrumented gaps are `unattributed_gap`, not silently assigned to labor or
  waiting. Total workflow latency is `published_at - occurred_at`; pre-identify
  latency, stage active labor, waits, and unattributed gaps partition it.

Automation is recorded per attempt as `manual` (human executes material steps),
`assisted` (tool proposes/transforms but human executes or accepts), or
`automated` (configured system executes without per-candidate human action).
Record tool name/version and the classification rationale. This says nothing
about quality, effectiveness, or value.

Failed attempts remain present with `failed` and a failure enum; repeated work
uses a new attempt with `is_rework=true` and `supersedes_attempt_id`. Abandoned
observations require time, actor, and reason. A stage not observed is
`unobservable` with reason and expected source; it MUST NOT be imputed. A stage
not reached is `not_reached`. Null timestamps require one of these statuses.

## 5. Provenance and uncertainty

Every canonical timestamp and labor/wait interval requires a provenance record:
immutable source identifier, source type (`platform_api`, `audit_log`,
`screen_recording`, `interaction_log`, `stopwatch`, or `contemporaneous_note`),
collector, collection time, SHA-256 of the exported artifact, and storage URI.
Self-report reconstructed after the fact is not valid timestamp provenance.
Identifiers are pseudonymous; access controls and consent remain prerequisites.

Timestamp uncertainty is a closed interval `[lower, upper]` in milliseconds
around the recorded instant, based on source resolution plus known clock offset;
`unknown` is explicit. Derived durations carry interval bounds by endpoint
interval arithmetic. Primary summaries report point estimates and bound ranges;
unknown uncertainty triggers the provenance rule below rather than invented
precision.

## 6. Metrics, confounders, and outcome window

Primary metrics are median and p75 wall-clock occurrence-to-publication latency,
stage elapsed time, active-labor time, wait time, unattributed time, rework count,
failure rate, abandonment rate, and censoring rate. Report observation-, session-,
and creator-level distributions; never treat nested clips as independent proof.

A **meaningful bottleneck** is frozen as a canonical stage that, among published
complete-provenance observations, has both (a) median share >=25% of total
latency and (b) p75 elapsed duration >=30 minutes. If multiple qualify, report
all ranked by median share. These are descriptive thresholds, not causal claims.

The only downstream outcome is destination-native public views accumulated in
the fixed interval `[published_at, published_at + 168 hours]`, captured at the
endpoint with API/audit provenance. Do not use rolling/current counts. If views
are unavailable or noncomparable, omit value analysis. Exploratory association
is Spearman correlation between total latency and `log1p(views_168h)`, with a
creator-cluster bootstrap 95% interval when at least 30 published observations
and 3 creators have complete outcomes. Record, without causal adjustment claims:
creator, session, platform, destination, session duration, moment offset,
source-interval duration, day/time, audience size measured before session,
concurrent live viewers at moment (if observable), content category, staffing,
tool classifications, network outage, destination incident, and scheduled versus
immediate release.

No observation or cohort decision may inspect downstream outcomes. Latency value
is considered **resolved for this protocol only** when the correlation interval
excludes zero; it remains correlational and does not establish business value.

## 7. Count, stopping, analysis, and decision rule

The minimum viable descriptive cohort is **30 eligible candidate moments**, from
at least **3 creators and 3 distinct sessions**, with at least 10 published
complete-provenance observations. This is a feasibility floor, not a powered
effect sample. Enroll sessions consecutively until the first session boundary at
which the floor is met, or until 12 enrolled sessions or 60 eligible moments,
whichever comes first. Never stop based on observed latency, bottleneck, views,
or correlation. Freeze the inclusion ledger before retrieving 168-hour outcomes.

Apply this precedence exactly:

1. `BLOCKED_BY_ACCESS_OR_PROVENANCE` if the cap is reached without the minimum,
   or fewer than 80% of eligible observations have provenance-complete canonical
   endpoints/stage statuses sufficient for latency decomposition.
2. `LATENCY_BOTTLENECK_IDENTIFIED` if at least one meaningful bottleneck exists.
   Report value analysis separately; this determination does not assert value.
3. `LATENCY_VALUE_UNRESOLVED` if no bottleneck qualifies and the prespecified
   value analysis cannot run or its interval includes zero.
4. `NO_MEANINGFUL_LATENCY_BOTTLENECK` if no bottleneck qualifies and the value
   analysis runs with its interval excluding zero. This label concerns the frozen
   thresholds only and makes no causal or product claim.

## 8. Deterministic records and validation

`observation.schema.json` is the normative per-observation structure. Records
are UTF-8 JSON, one object per file, with unique IDs. Dataset order is ascending
`session_start_at`, `session_id`, `occurred_at`, `observation_id`; enum spelling
and null semantics are exact. Raw artifacts are immutable. Corrections append a
revision with author, time, reason, and prior record SHA-256; they never overwrite.

Before analysis, two reviewers independently compare a deterministic 20% sample
(SHA-256 of `observation_id` ascending, first ceiling(0.2*n)) against raw
artifacts. Resolve discrepancies by an append-only correction. The validator
must pass schema, ID uniqueness, ordering, stage chronology/nullable-status
rules, attempt interval containment and non-overlap, provenance/hash shape,
eligibility ledger completeness, outcome-window timing, cohort floor/cap, and
decision-rule recomputation. Any failed check blocks analysis. `validate_protocol.py`
validates the frozen protocol artifacts themselves; execution-data validation is
required before collection begins and is deliberately not an application or
publishing implementation.

## 9. Access gates and freeze control

Prospective collection is **not ready** until named data owners confirm: consent
and observation authority; durable access to source recordings/timecodes;
workflow audit, interaction, or stopwatch capture; destination publication
timestamps/public retrievability; immutable artifact storage; clock-offset
capture; and (only for optional value analysis) 168-hour view access. Log access
approval without treating it as authorization to automate or build.

Any change after the first enrolled session requires a new protocol version and
must be reported as an amendment; v1.0.0 remains immutable. Analyses may not
silently reinterpret definitions or thresholds.
