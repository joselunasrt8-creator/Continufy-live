# Issue 12: one-customer paid-pilot acquisition instrument

**Depends on:** frozen Issue #11 protocol `continufy-ai-content-paid-pilot-v1.0.0`  
**Scope:** preparation and manual evidence recording only  
**Current terminal determination:** `MANUAL_ACQUISITION_REQUIRED`

This instrument makes the acquisition decision reproducible; it does not contact
anyone, obtain consent, accept payment, create customer evidence, perform pilot
work, or authorize Issue #13. A human must perform every real-world interaction.

## Evidence threshold

`PAID_PILOT_CUSTOMER_ELIGIBLE` is valid for exactly one non-synthetic customer
only when all of the following are supported by references to evidence retained
outside Git in controlled storage:

1. the Issue #11 offer was actually presented, including a proposed USD price
   in the frozen $250–$400 range, and the customer explicitly accepted a
   positive price and signed service agreement;
2. settled payment evidence exists—interest, a promise, an invoice, or payment
   authorization does not count;
3. one complete and retrievable eligible source was selected before outcomes,
   with customer ownership or legitimate licence evidence;
4. the accepted scope freezes one source, 1–8 assets in at least two permitted
   forms, no more than three named destinations, two revision rounds, baseline
   method, readiness date, approver, and publication controller;
5. transformation/creation, minimized-evidence retention, measurement, and
   required data access are separately granted;
6. every destination has an explicit mode. `NOT_AUTHORIZED` is valid when the
   pilot will not publish there; either publishing mode requires its own
   permission reference. Payment and service acceptance never grant publication;
7. no privacy, credential, platform-policy, authority, provenance, access,
   scope, or payment dependency remains unresolved; and
8. there is no withdrawal, cancellation, or revoked permission.

The public record contains pseudonymous IDs and opaque evidence references only.
Names, contact details, private messages, raw customer content, credentials,
tokens, payment instruments, and consent documents stay out of the repository.
Evidence references are pointers, not evidence invented by the recorder.

## Manual acquisition checklist

Perform these steps manually and stop immediately on decline or withdrawal:

- [ ] Assign a new pseudonymous candidate ID and record the legitimate channel
      and first-identification timestamp. Do not copy contact details into Git.
- [ ] Confirm an apparently eligible source and the person/entity's authority
      to discuss it. Contactability is not consent.
- [ ] Present the unchanged Issue #11 offer and record only an opaque controlled-
      storage reference plus proposed price. Interest is not willingness to pay.
- [ ] If accepted, obtain a signed service agreement and separately record the
      accepted price and accepted scope. Do not treat acceptance as payment.
- [ ] Verify source ownership/licence, complete source access, creation authority,
      evidence-retention consent, approver, and publication controller.
- [ ] Record a mode for each destination and secure separate publication
      authority only where publishing is authorized.
- [ ] Secure measurement consent and actual outcome-data access separately.
      Payment is not measurement permission.
- [ ] Confirm funds have settled and retain an opaque settlement reference.
- [ ] List every unresolved dependency; never clear one without actual evidence.
- [ ] Run the validator. Proceed to Issue #13 only if it returns
      `PAID_PILOT_CUSTOMER_ELIGIBLE` for one real record.

For corrections, preserve the prior committed record and add a corrected record
or commit; do not rewrite external evidence. On withdrawal or cancellation,
record its timestamp and controlled-storage reference, revoke the transition,
and do not start or continue execution.

## Determination rules

The validator applies one terminal state per record:

1. decline, no response, ineligibility, withdrawal, or cancellation →
   `NO_ELIGIBLE_PAID_PILOT_CUSTOMER_ACQUIRED`;
2. an accepted or paid candidate with unresolved authority/access dependencies →
   `BLOCKED_BY_AUTHORITY_OR_ACCESS`;
3. every evidence threshold above, for a real record →
   `PAID_PILOT_CUSTOMER_ELIGIBLE`;
4. otherwise → `MANUAL_ACQUISITION_REQUIRED`.

Validation of multiple records rejects more than one eligible customer. One
paying customer is a bounded pilot input, not market validation. Until genuine
evidence meets the eligibility rule, Issue #13 is not execution-eligible.

## Use

Copy the synthetic template to a private working branch or other appropriately
controlled workflow, replace placeholders only with pseudonymous metadata and
opaque evidence references, then run:

```text
python3 research/issue-12/validate_acquisition.py path/to/record.json
```

The checked-in synthetic record deliberately contains no customer interaction
and therefore returns `MANUAL_ACQUISITION_REQUIRED`.
