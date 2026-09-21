# 09 — Rollout plan

Four phases. Each is useful on its own and can be the stopping point if the analysis in `08` changes the decision. Numbers in brackets refer to the changes in `07`.

---

## Phase 0 — Stop the bleeding (ship now)

**Goal.** End the mobile-flag drift without touching the architecture.

| Step | Detail |
|---|---|
| Complete the v2 field mapping [4] | Mirror writes mobile vendor, country, email on create and update, read from the CMS by CMS ID (the same call the note already uses). |
| Search box trusts the CMS mobile flag for CMS-matched rows | Providers found through the CMS list no longer need the Roadside flag to be set. |
| Confirm the mobile flag with the business [9-i] | List of 687 CMS "mobile" vendors reviewed; call centres corrected in the CMS. |
| Backfill the 317 | One run of the (new) reconcile logic limited to the mobile flag, after the review. |

**Success criteria.** Every provider whose CMS module says mobile = yes and status = active is offered in Auto-mode search on SIT and UAT; drift query returns 0 for the mobile flag on production after backfill.
**Rollback.** The mapping is additive; the backfill is a reversible column update (before/after values kept).
**Effort.** Days. **Dependencies.** Business review of the mobile list.

---

## Phase 1 — Analyse and decide

**Goal.** Answer the ten complications; sign off field ownership.

| Step | Output |
|---|---|
| Decision register in `08` completed | Owner and answer per line |
| Field-ownership table in `07` signed by Benefit and Roadside owners | One page |
| Publish / active mapping written down | Table, plus editor guidance |
| Delay tolerance and outage policy decided | Two numbers: max delay, max CMS outage before dispatch is affected |
| CMS clean-up rules agreed and the roadside flag added to the content model [8] | Flag exists in all CMS environments |

**Success criteria.** No open line in the decision register.
**Effort.** Calendar time, little engineering. **Dependencies.** People.

---

## Phase 2 — Build the plumbing

**Goal.** A complete, self-healing mirror and fast CMS reads, still with today's fallbacks in place.

| Step | Detail |
|---|---|
| CMS → Roadside webhook [3] | Per environment; signed; idempotent upsert; unpublish / archive / delete mapped per Phase 1 [5] |
| Nightly reconcile [6] | Also used for the initial full backfill |
| Drift report + alerts [7] | Daily e-mail / dashboard; alert on webhook or reconcile failure |
| Provider cache [10] | TTL 60 s, webhook invalidation, shared with background timers |
| Outage behaviour [11] | Implemented per Phase 1 decision; silent nulls replaced by surfaced errors |
| One CMS environment per Roadside environment [13] | Config set on SIT, UAT, pre-prod, prod; content types replicated |
| CMS data clean-up [9-ii..v] | 24 re-filed or flagged, 7 unlinked resolved, duplicates removed |

**Success criteria.** Drift report = 0 on SIT/UAT for 7 consecutive days with editors working normally; a vendor edit in the CMS is visible in Roadside within the agreed delay; a simulated CMS outage on UAT leaves dispatch working.
**Rollback.** Webhook can be disabled; fallbacks are still present.
**Effort.** 3–6 weeks engineering + CMS admin. **Dependencies.** Phase 1 decisions; Kontent environments.

---

## Phase 3 — Switch over

**Goal.** CMS becomes the only writer; screens move to the mirror / cache; overlays retired.

| Step | Order |
|---|---|
| Full production backfill via reconcile; compare; sign off [14] | first |
| Close the direct provider edit [1]; retire v1 push [2] | second |
| Move read paths one screen at a time [12, 14]: provider detail and vehicle screens (already on CMS) → provider list → search box → job save / job detail → customer link → reports | one per release, watch the drift report |
| Remove per-request CMS overlays once the mirror has been clean for the agreed period | last |
| Remove fallbacks — only if the Phase 1 outage decision says so | optional |

**Success criteria.** Drift report = 0 on production for the agreed period; no provider-related incident during the switch; agents cannot tell which screen reads which store.
**Rollback.** Each screen move is a flag; the overlay code stays until the end.
**Effort.** Spread over several releases. **Dependencies.** Phase 2 green on UAT.

---

## What each phase delivers to users

| After phase | Agents see |
|---|---|
| 0 | Every mobile provider in Auto-mode search; nothing else changes |
| 1 | Nothing yet; decisions are made |
| 2 | Faster provider screens (cache); CMS edits appear within a minute; ops get a daily drift report |
| 3 | One spelling of every vendor everywhere; vendors are edited in one place; Roadside cannot drift |

## What is explicitly *not* in this plan

- Deleting or bypassing the Roadside provider record. Seven features and every job, vehicle and payment depend on it.
- Calling the CMS per row in any list or report.
- Moving the dispatch engine, the monitor board, the auth filter or the lost-signal timer off SQL.
