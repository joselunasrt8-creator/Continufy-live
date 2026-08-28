# Issue 9: outcome-blind participant acquisition protocol

**Protocol ID:** `continufy-recruitment-v1.0.0`  
**Status:** frozen before outreach  
**Frozen on:** 2026-08-28  
**Bounded determination:** `READY_FOR_MANUAL_PARTICIPANT_OUTREACH`

This protocol authorizes only bounded, manual recruitment. It does not record an
empirical observation, enroll anyone into Issue 5, verify an Issue 7 gate,
authorize automation, or authorize use of footage. The Issue 5 protocol
`continufy-live-latency-v1.0.0` and Issue 7's
`BLOCKED_BY_ACCESS_OR_PROVENANCE` determination remain unchanged; G01--G11
remain `UNVERIFIED`.

## 1. Canonical unit and transaction loops

The **recruitment unit** is one prospective authorized workflow relationship:
one creator or creator team that controls one live-source-to-short-form
publication workflow, together with any clipper, editor, agency, or researcher
needed to expose that workflow. A discovery lead that is only a clipper or
agency may be recorded, but cannot advance until it is anchored to exactly one
creator-controlled workflow. Multiple listings, people on the same team, or
channels do not create additional units. Distinct creator-controlled workflows
are distinct units even if they share an agency.

Every unit has exactly one market segment:

* `CREATOR_SERVICE`: authorized work for the creator/controller, potentially
  exposing source, review, publication, and analytics handoffs.
* `PERFORMANCE_DISTRIBUTION`: approved assets and rules are distributed for
  performance compensation. This can expose brief, editing rules, posting,
  submission, verification, and payout, but does not by itself expose or
  authorize the creator's internal live workflow.
* `OPEN_FAN_CLIPPING`: public material is clipped without a commercial
  relationship. Skill demonstration is not consent, authority, or workflow
  access, so this segment is ineligible for gate-verification transition.

## 2. Frozen channel taxonomy

The machine-readable values are `FREELANCE_MARKETPLACE`,
`CREATOR_JOB_BOARD`, `CREATOR_HIRING_COMMUNITY`, `EDITOR_CLIPPING_DISCORD`,
`CREATOR_DISCORD`, `DIRECT_CREATOR_OUTREACH`, `DIRECT_CLIPPER_EDITOR_OUTREACH`,
`CLIPPING_AGENCY`, `PERFORMANCE_CLIPPING_MARKETPLACE`,
`PERFORMANCE_CLIPPING_COMMUNITY`, `RESEARCHER_AS_CLIPPER_SERVICE`, and
`OTHER_CLASSIFIED`. `OTHER_CLASSIFIED` requires a non-empty classification in
`channel_detail`. The channel is a provenance-bearing acquisition surface, not
an eligibility or authority claim. Upwork/Fiverr are examples of the first;
YTJobs/general creator job boards of the second; Reddit or other creator/editor
hiring groups of the third; creator and editor Discords remain distinct; and
Whop Content Rewards, Vyro, and Clipping.net are examples of performance
marketplaces. These examples are not endorsements or comparative findings.

## 3. Outcome-blind identification and eligibility

Identification may use only: `ACTIVE_LIVESTREAMING`, `SHORT_FORM_USE_OR_INTENT`,
`OBSERVABLE_CLIPPING_NEED`, `EXISTING_CLIPPING_WORKFLOW`,
`LEGITIMATE_CONTACT_MECHANISM`, `PLATFORM_RELEVANCE`, and
`WORKFLOW_ACCESS_DISCUSSIBLE`. It must set `outcome_blind_confirmed=true` and
`prohibited_selection_factors=[]`. Views, engagement, revenue, virality,
conversion, observed clip success/failure, or any downstream performance may
not be used to identify, include, exclude, sequence, or stop on a candidate.

Creator size, posting frequency, seven-day duration, channel priority, price,
and proposed quantities (40 prospects, 30 messages, 10 applications, 5
community responses, 5 invitations, 3 calls, or 1 pilot) are **outside the
canonical protocol**. They are unvalidated market-research heuristics, not
scientific findings, eligibility thresholds, quotas, or stopping rules. An
operator may pre-register a bounded operational batch separately, but it may
not change these rules, use outcomes, or claim representativeness.

A unit is `INCLUDED` exactly when all are true: at least one relevant live/VOD
workflow exists; short-form use or intent is present; a legitimate permitted
contact/application route is available; platform relevance exists; and the
creator/controller, or an operator able prospectively to identify that
controller, could discuss authorized workflow access. This includes an active
creator seeking help, a relevant creator workflow, a creator-linked editor, or
an agency/operator capable of exposing an authorized workflow.

A unit is `EXCLUDED` using one or more frozen reasons:
`NO_RELEVANT_LIVE_WORKFLOW`, `NO_SHORT_FORM_USE_OR_INTENT`,
`NO_LEGITIMATE_CONTACT_MECHANISM`, `INACCESSIBLE_OR_PRIVATE_SOURCE`,
`AUTOMATED_OR_SPAM_LISTING`, `EXPIRED_OR_CLOSED_LISTING`,
`OPEN_FAN_ONLY`, `PERFORMANCE_ONLY_NO_CREATOR_WORKFLOW`, or
`CANNOT_IDENTIFY_WORKFLOW_CONTROLLER`. An inaccessible/private community is
not entered or scraped. Performance-only leads remain useful market-learning
records but are excluded from creator-workflow gate transition. Performance is
never an exclusion reason.

## 4. Identity resolution and duplicates

Before contact, manually normalize only public, non-sensitive signals: public
account/listing identifiers, disclosed team/agency affiliation, creator
controller, platform, and workflow. Compute/store a privacy-preserving internal
ID; do not store unnecessary names or contact data. Search the local registry
for the same controller plus workflow. The earliest `date_identified`, then
lexicographically smallest `candidate_id`, is canonical. Later matches are
`DUPLICATE`, point `canonical_candidate_id` to that unit, receive no outreach,
and are excluded from candidate counts. Add the newly discovered surface as
provenance on the canonical controlled record instead of creating another
countable unit. Ambiguous matches are resolved before contact, never silently
counted twice.

## 5. Manual outreach procedure

1. Validate the record while it is `NOT_CONTACTED`. Only an `INCLUDED`,
   `UNIQUE`, outcome-blind unit may be contacted. A human checks platform terms
   and community rules immediately before contact. No accounts, scraping,
   automation, or bulk messaging are authorized by this protocol.
2. Use the route attached to the source. `GENERIC_TWO_ATTEMPT` permits at most
   two human-sent attempts, at least 168 hours apart. After the second attempt,
   wait at least 168 hours before assigning `NO_RESPONSE`.
   `MARKETPLACE_SINGLE_APPLICATION` permits one application and no generic
   follow-up; the marketplace's stricter limits or closed workflow supersede
   this protocol. Assign `NO_RESPONSE` no sooner than 168 hours after that
   application. A platform-authorized inbound reply is a response, not another
   outbound attempt.
3. Initial outreach may occur only after a passing validation and rules check.
   Record timestamps, not message bodies. An explicit `DECLINED` or
   `WITHDRAWN` response immediately terminates all outreach. `NO_RESPONSE`,
   `INELIGIBLE`, and `DUPLICATE` are also terminal. Do not re-contact a terminal
   unit under another channel.
4. Classify a positive response `INTERESTED`; if authority/access is not yet
   clear, move to `ACCESS_DISCUSSION_REQUIRED`. Discussion is manual and may
   lead to gate-verification candidacy only under section 9.

Valid state transitions are:

```
NOT_CONTACTED -> CONTACTED | INELIGIBLE | DUPLICATE
CONTACTED -> CONTACTED | NO_RESPONSE | DECLINED | INTERESTED | INELIGIBLE | WITHDRAWN
INTERESTED -> ACCESS_DISCUSSION_REQUIRED | DECLINED | INELIGIBLE | WITHDRAWN
ACCESS_DISCUSSION_REQUIRED -> CANDIDATE_FOR_GATE_VERIFICATION | DECLINED | INELIGIBLE | WITHDRAWN
```

The `CONTACTED -> CONTACTED` self-transition represents only the permitted
second generic attempt. All terminal states have no outgoing transition.

## 6. Disclosure layers

Platform-appropriate wording may vary, but the following layers must remain
separate and be recorded separately:

* **SERVICE OFFER:** clipping/service purpose, bounded pilot scope, authorized
  footage only, creator approval/control, and no need to disclose credentials.
* **RESEARCH DISCLOSURE:** service participation does not imply research;
  observation is optional and separately discussed; service may be discussed
  or purchased while research is declined.
* **RESEARCH CONSENT:** a separate explicit, withdrawable agreement describing
  scope, artifacts, retention, and participants. A listing, reply, marketplace
  acceptance, service agreement, or payment is not consent.
* **OBSERVATION AUTHORITY:** separate evidence from the controller and relevant
  platform/data owners covering what may be observed and retained. Consent is
  not automatically authority.

No credentials are requested or stored. Posting access is scoped delegated
access, never credential ownership. Technical access is not authority.

## 7. Researcher-as-clipper/service path

`RESEARCHER_AS_CLIPPER_SERVICE` is a channel within `CREATOR_SERVICE`. The
service may expose source access, moment discovery, VOD review, editing, review,
revision, publication handoff, analytics handoff, and payment. Nevertheless,
paid work is not research consent; service permission is not observation
authority; footage access is not artifact-retention permission; posting access
is not credential ownership; and creator approval is not platform authority.

Advancement requires the same section 9 evidence as every other unit: separate
research consent to begin verification, separately scoped observation/retention
authority, an identified controller, and a prospective owner/source discussion
for every G03--G11 item. A service agreement alone leaves consent and authority
`NOT_ESTABLISHED`.

## 8. Performance-distribution path

Performance marketplaces and communities must use
`PERFORMANCE_DISTRIBUTION`; their machine-readable
`creator_workflow_access=false` unless separate controller evidence establishes
a creator-service workflow. Campaign acceptance, approved assets, rules,
posting, verification, or payout never changes research consent or observation
authority. A performance-only record is `INELIGIBLE` with
`PERFORMANCE_ONLY_NO_CREATOR_WORKFLOW` and cannot expose G03--G11 for Issue 7.
If a separately authorized creator-service workflow later exists, create or
link the canonical creator-controlled unit and re-evaluate prospectively; do
not rewrite campaign participation as authority.

## 9. Deterministic transition to Issue 7

`CANDIDATE_FOR_GATE_VERIFICATION` is permitted only from
`ACCESS_DISCUSSION_REQUIRED` when the record is included, unique,
`CREATOR_SERVICE`, anchored to a controller, and all of the following are
explicit: research discussion `COMPLETED`; separate research consent
`AGREED_FOR_GATE_VERIFICATION`; observation authority
`AGREED_FOR_GATE_VERIFICATION`; controlled evidence references for both; no
credentials; `creator_workflow_access=true`; and each G03--G11 has a prospective
responsible owner/source marked `DISCUSSIBLE`. `potential_issue7_gates` must be
exactly G01--G11. These are permissions and plans to **begin verification**, not
verified gates. G01--G11 remain `UNVERIFIED` until Issue 7 validates real
evidence. Interest, acceptance, a call, or a paid trial is insufficient.

## 10. Record, provenance, privacy, and operation

`recruitment.schema.json` freezes the record. `validate_recruitment.py` enforces
cross-field and transition rules that JSON Schema alone cannot express. Public
repository records contain privacy-preserving IDs and controlled evidence
references only. Never commit passwords, tokens, credentials, message bodies,
emails, private Discord/marketplace messages, source footage, names not needed
for identity resolution, or sensitive participant data.

Provenance types are `PUBLIC_LISTING`, `PUBLIC_PROFILE`, `PUBLIC_COMMUNITY`,
`PRIVATE_COMMUNICATION`, `MARKETPLACE_APPLICATION`, `SERVICE_AGREEMENT`,
`RESEARCH_CONSENT_ARTIFACT`, `OBSERVATION_AUTHORITY_ARTIFACT`, and `INFERENCE`.
Private items use opaque references
to appropriately controlled storage, never reproduced content. Public
contactability is not consent; a public editor listing establishes at most a
demand signal. Inference is labeled and cannot establish consent or authority.

Synthetic records set `synthetic=true`, use `SYNTH-` IDs and synthetic
references, and are permanently barred from real evidence or candidate counts.
Run the dependency-free tests before operating and validate each record before
and after every manual state change. Recruitment success is not collection
readiness: no Issue 5 observation begins until Issue 7 independently verifies
all gates.

## 11. Frozen boundaries and determination

Public availability != permission; contactability != consent; conversation !=
observation authority; service agreement != research consent; marketplace
acceptance != research authorization; technical access != authority;
recruitment != empirical observation; recruitment success != collection
readiness; validation != authorization; research result != permission to build.

The bounded determination is `READY_FOR_MANUAL_PARTICIPANT_OUTREACH`: after
merge, a human may follow this protocol for manual acquisition only. It does not
mean anyone consented, any Issue 7 gate passed, Issue 5 collection may begin,
software should be built, or publication automation is authorized.
