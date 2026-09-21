---
name: reference-fwd-concurrent-run-duplicates
description: FWD/FWW duplicate customers come from concurrent prod runs — the dedup dictionary is an in-memory snapshot loaded at transaction start, and no DB unique constraint exists. Use when investigating duplicate customer records.
metadata:
  type: reference
---

`FWDBatchProcessor` dedups against `existingCustomerDictionary1/2/3`, built **once** from
`_context.Customers.Where(ClientCode in FWU/FWS/FWW/FWT).ToListAsync()` at the top of the
transaction (FWDBatchProcessor.cs:139) and matched at :384. `processedKeys` / `lastOccurrenceIndex`
only dedup **within one file**. So two overlapping runs each load a snapshot before either commits,
neither sees the other's inserts, and every shared member is inserted twice.

**No DB safety net**: every index on `customers` is non-unique (checked 2026-09-03). Nothing
catches a duplicate UUID.

**2026-08-18 FWW incident** (found via ABE ticket on customers 10348908 / 10351026):
CS sent V1 and V0 of the same "MyWell Eligible members Q326" xlsx ~10 min apart; each triggered its
own Batch job, and they overlapped by ~52 min:
- run A `48dad76cc120` 02:37:09 → 03:39:24 (V1)
- run B `0a138ffba0dd` 02:47:10 → 03:47:55 (V0)

Result: 4,239 FWW rows created that day; as of 2026-09-03, **2,117 FWW customers have 2+ live rows**
(2,118 surplus) plus 27 FWS groups. Duplicate rows are byte-identical including `CustomerAttributes`
— comparing field values proves nothing, so diagnose by `CreatedOn` + run overlap, not by data diff.

**Triage recipe**: hash the UUID components to group duplicates without exposing PII —
`SHA2(CONCAT_WS('|',FirstNameEN,LastNameEN,CardType, JSON_UNQUOTE(JSON_EXTRACT(CustomerAttributes,'$.InsuredID')),
 ...'$.EffectiveDate'), ...'$.ExpirationDate')),256)`. FWW UUID = those 6 fields (see
`BuildUUIDForFWUFWW`); FWT drops InsuredID/dates; FWS adds ProductName.

Cleanup notes: the Aug-18 rows have **0 bookings** but all have `customerprograms` rows, which must
be removed with them. Only one row (10348908) was ever manually soft-deleted (2026-08-24) — there
has been no bulk cleanup.

Fix directions: serialize FWD runs (claim lock, cf. [[reference-handback-run-races]]), and/or
re-check existence immediately before insert instead of trusting the start-of-run snapshot.
Related: [[reference-kpi-s3-upload-triggers-duplicate-job]].

**Status 2026-09-08:** the fix exists as `ABE-5325 Prevent duplicate FWD customers` — a MySQL
advisory lock `GET_LOCK('abcb_fwd_data_processor')` around the snapshot+transaction, plus
`FWDCustomerUuid` normalisation. Originally on local-only branch `codex/abe-5325-fww-customer-dedup`
(never pushed); re-cut onto `jira/ABE-5325-fwd-duplicate-prevention` from `data-processer-production`.
**Deployed to UAT only** (`benefit-fwd-import-uat-job-definitions:6`, image
`apac-benefit-data-processer-pre-production:uat-abe5325-fwd-20260908-01`); prod still runs
`fwd-abe5142-20260813`. Lock verified live: holding it externally made a UAT job take 140.9s vs
the normal ~35s.

**Still open:** the 600s lock timeout *rejects* the second file instead of queueing it (Aug-18 runs
took ~62 min), and that path throws before any `PublishFailedHandback…` so a contended file never
appears in the Data Processor Report. No unique index yet, and the 2,117 duplicates are uncleaned.
