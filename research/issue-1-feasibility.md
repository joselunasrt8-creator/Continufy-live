# Issue #1 — bounded public-data feasibility investigation

**Investigation date:** 2026-08-27 UTC  
**Mode:** empirical observation only; no product, architecture, authority, or publishing decision

## 1. Scope and repository finding

The repository at the supplied commit contains only `.gitkeep`: it has no
remote, issue export, source, tests, or Issue #1 text. Attempts to discover the
issue through an authenticated GitHub context were also blocked because no
remote or GitHub credentials are configured. Consequently, the user's supplied
Issue #1 statement is the operational scope, but the identity and exact text of
the repository-hosted issue could not be independently verified. This is an
explicit provenance gap, not an invitation to infer more scope.

The bounded question is whether legitimate public/official sources can support
a replayable observation chain:

`creator → livestream/VOD → moment → clip → downstream publication → outcome`

“Successful operation” is operationalized only as a cohort label that a future
protocol must pre-register (for example, a creator-consented operation and a
fixed-age view outcome). It is not inferred from popularity. No causal claim is
in scope.

## 2. Source inventory

The machine-readable inventory is [`source-inventory.csv`](source-inventory.csv).
The authoritative documentation targets consulted for the inventory are:

- Twitch [API reference](https://dev.twitch.tv/docs/api/reference/),
  [authentication](https://dev.twitch.tv/docs/authentication/),
  [rate limits](https://dev.twitch.tv/docs/api/guide/#twitch-rate-limits), and
  [VOD storage](https://help.twitch.tv/s/article/video-on-demand).
- Google [YouTube Data API reference](https://developers.google.com/youtube/v3/docs),
  [quota calculator](https://developers.google.com/youtube/v3/determine_quota_cost),
  [quota and compliance](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits),
  and [YouTube Analytics API](https://developers.google.com/youtube/analytics).
- TikTok [Display API](https://developers.tiktok.com/doc/display-api-overview/)
  and [Research API](https://developers.tiktok.com/products/research-api/).

These pages are cited as the official specifications to verify before a
credentialed run. During this run, the network proxy returned HTTP 403 before
those documentation hosts, so their contents were not captured as dated raw
evidence. Inventory claims are therefore a protocol design based on the named
official surfaces, not proof that an endpoint succeeded on the investigation
date.

### What the sources can and cannot establish

1. **Twitch Helix is the strongest first-party spine.** Clip records expose
   creator and broadcaster IDs, a nullable video ID/VOD offset, clip time,
   duration, and mutable view count. Video and stream records add stream/video
   metadata and snapshot audience measures. They do not expose an operation,
   editor workflow, selection rationale, downstream repost, conversion rate, or
   counterfactual unselected moments.
2. **YouTube can measure an independently identified downstream video.** Public
   video/channel resources can supply publication metadata and engagement
   counts. Search results do not constitute a complete census and the API does
   not assert that a YouTube Short derives from a Twitch moment.
3. **Owner analytics are informative but not public.** Watch time, retention,
   traffic, and richer performance require an authorized channel/content owner.
4. **TikTok public-data access is not a general anonymous baseline.** Display
   access is user-authorized. Research API access is eligibility- and
   purpose-gated. Neither surface supplies universal Twitch lineage.
5. **Web pages, undocumented GraphQL, scraping, third-party aggregators, and
   inferred downloader URLs are excluded.** They do not meet the
   official/legitimate, stable-contract, provenance-preserving requirement for
   this pilot.

Authentication and quota values change. A real acquisition must capture the
then-current official documentation, response headers, granted scopes, project
identity (pseudonymized where necessary), and terms version alongside data.

## 3. Minimal observation schema

The normative research schema is
[`observation.schema.json`](observation.schema.json). It deliberately represents
the chain without declaring a final domain model:

| Node/link | Minimal fields | Reason |
|---|---|---|
| Observation | immutable local ID, UTC observation time | distinguishes repeated mutable metric snapshots |
| Creator | platform, platform creator ID, URL if available | joins streams/clips; audience covariates are separate observations |
| Livestream/VOD | platform, video/stream ID, URL | preserves a nullable source identity rather than manufacturing one |
| Moment | start/end offset, derivation method | distinguishes platform VOD offsets from alignment or attestation |
| Clip | platform, clip ID, URL | identifies the actual short segment |
| Downstream publication | nullable platform/ID, linkage method/confidence | absence stays unknown; candidates do not become facts |
| Outcome | metric, value or NULL, measured-at, fixed window | makes mutable counts comparable only at defined ages |
| Provenance | source, canonical request, retrieval UTC, raw SHA-256 | permits integrity checks and qualified replay |
| Uncertainty | explicit, repeatable labels | prevents missingness and inference from silently collapsing |

The schema permits a null downstream object and null measures, but requires the
observer to say how a moment and any cross-platform link were derived.

## 4. Inclusion, exclusion, and sampling protocol

### Pre-registered pilot frame

1. Choose **one UTC collection week** before querying.
2. Draw **five Twitch broadcasters** from one predeclared game/category and
   language using a reproducible seeded sample of broadcaster IDs observed live
   at a fixed UTC snapshot. This is a feasibility sample, not population
   inference.
3. Include every official Twitch clip for those broadcasters whose `created_at`
   falls inside that week. Save all pages, headers, request parameters, and raw
   responses. De-duplicate on clip ID.
4. Include a livestream/VOD link only when Helix supplies the video ID and
   offset, or label another allowed derivation. Do not infer a deleted VOD.
5. Freeze clip-view snapshots at collection and, prospectively, at fixed
   7-day and 30-day clip ages. If an age was missed, store NULL rather than the
   nearest convenient count.
6. Search downstream platforms only after freezing a deterministic query set
   derived from creator-declared accounts and clip title/time. Store search
   candidates separately. Promote a link only by platform reference, creator
   attestation, exact media hash, or a documented perceptual match; retain the
   schema confidence category.
7. For each creator, record audience-size proxies at the same declared snapshot
   where officially obtainable. Analyze within-creator ranks or stratified
   summaries; never treat raw cross-creator views as clip quality.

### Include

- records returned by documented official APIs under valid credentials;
- public clips with a stable platform ID and creation timestamp in the window;
- repeated outcome observations with explicit metric, timestamp, and age;
- downstream candidates with their uncertainty intact;
- failures, deletions, inaccessible records, and missing fields in the
  acquisition log.

### Exclude

- scraped/undocumented endpoints or terms-circumventing acquisition;
- third-party popularity lists as ground truth;
- compilations where the source moment cannot be bounded;
- private/deleted content represented from hearsay;
- comparisons with mismatched observation ages;
- “unsuccessful” moments selected after seeing outcomes;
- causal, quality, revenue, conversion, or operational-efficiency labels not
  directly observed under a predeclared definition.

### A valid later comparison

The smallest defensible descriptive comparison would be clip outcomes at equal
ages **within creator**, reporting count, median, interquartile range, and
missingness. Moment duration, creation delay, category, language, and source
link availability may be described. A genuine operation-level comparison
requires creator/editor consent or another direct operation identifier; public
clip records alone cannot distinguish organized operations from casual clipping.

## 5. Provenance and uncertainty rules

- Store raw response bytes unchanged; hash with SHA-256; store a normalized
  derivative separately. A normalized row never replaces raw evidence.
- Record UTC retrieval time, endpoint/version, canonical parameters, pagination
  cursor, status, response rate headers, authentication class/scopes (not
  secrets), and collector version.
- A later response is a new observation. Mutable counts and deleted resources
  mean replay equivalence is not assumed.
- Missing downstream publication means **not observed by this method**, never
  proof of non-publication.
- A title/account/time similarity is a candidate, not confirmed provenance.
  Uncertain cross-platform provenance remains uncertain.
- Popularity is an outcome measure, not causal clipping quality. Correlation is
  not causation.
- Creator audience size, category, stream reach, publication timing, paid
  promotion, and platform recommendation are confounders; public fields do not
  fully control them.
- Observation is not evidence until its provenance and fitness for a particular
  claim are evaluated. Evidence does not establish theory. Neither reasoning
  nor a candidate grants permission or action. Execution does not establish a
  successful outcome.
- Do not retain access tokens, unnecessary personal data, or media copies unless
  terms, consent, and the declared research need permit it. Respect deletion and
  platform-policy obligations; hashes are integrity metadata, not ownership.

## 6. Pilot result

The pilot artifacts are an intentionally empty
[`observations.csv`](pilot/observations.csv) and a four-row
[`acquisition-log.csv`](pilot/acquisition-log.csv). This is the smallest honest
pilot under the available environment:

- Twitch acquisition stopped before request because `TWITCH_CLIENT_ID` and
  `TWITCH_ACCESS_TOKEN` are absent.
- YouTube acquisition stopped before request because `YOUTUBE_API_KEY` and a
  predeclared creator/sample frame are absent.
- No official general-purpose API establishes downstream cross-platform
  lineage.
- The repository's own Issue #1 cannot be provenance-captured from the current
  checkout.

No record was invented, scraped, or selected opportunistically to create the
appearance of a dataset. The offline validator proves that all four attempts are
recorded as blocked and that the observation table has zero rows.

## 7. Descriptive baseline supported by evidence

There are **0 acquired observations**, **4 blocked acquisition attempts**, and
**7 inventoried official data surfaces**. Therefore no distribution of clip
views, duration, timing, source-link rate, downstream-link rate, or creator
audience can be reported. There is no empirical basis in this run for claiming
observable characteristics that distinguish successful from ordinary outcomes.

The source-contract analysis supports only a narrower statement: official APIs
can represent parts of the chain and timestamp mutable outcomes, while operation
identity and cross-platform lineage are not generally public fields. Whether a
usable partial baseline can actually be acquired remains untested until a
credentialed, pre-registered run succeeds.

## 8. Blockers and unresolved questions

1. What is the canonical repository URL and exact Issue #1 body?
2. Can a registered research client receive Twitch credentials and preserve the
   applicable terms/version and rate headers?
3. Which fixed game, language, week, and deterministic broadcaster frame should
   be pre-registered without outcome-based selection?
4. Will creators/editors consent to identify operation membership, editor
   actions, unselected candidate moments, and downstream account ownership?
5. What media-linkage method and threshold can be validated against an
   attested ground-truth set without treating candidates as facts?
6. Which success metric and age window are meaningful before outcomes are seen?
7. How will deletions, hidden counts, retention expiry, API policy changes, and
   consent withdrawal be versioned?
8. Can audience, exposure, category, publication time, and promotion confounding
   be measured well enough for claims beyond description?

## 9. Next capability justified

**B. Further empirical/methodological research.** The immediate justified work
is a credentialed, pre-registered acquisition and an attested linkage validation
set. Recurring observations have not yet been acquired, so abstraction,
application modeling, structural analysis, deterministic structural tooling,
and mutation-capable workflow authority are premature. No downstream repository
is selected.

## Feasibility determination

BLOCKED_BY_ACCESS_OR_PROVENANCE
