# 05 — Reports

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F18, F19 (and F12 for grades)** in `features/`.


Reports are where "call the CMS" arithmetic bites hardest, because one report can carry tens of thousands of rows. The good news: only **one** column in any report is provider-derived — the provider name — and it can be produced without a single per-row CMS call. The bad news: done naively, it would be the slowest thing in the system.

---

## The arithmetic first

Facts from production:

| Measure | Value |
|---|---|
| Jobs per year | 51,764 (≈ 4,300 / month, ≈ 1,000 / week) |
| Distinct providers used in 90 days | 356 |
| Distinct providers with any job in 365 days | ≈ 420 |
| CMS call for one vendor by ID | 1.0 – 1.6 s with the "fresh content" header the code uses today; 0.2 – 0.45 s without |
| CMS batch lookup, up to 50 IDs per call | ≈ 0.9 s |
| CMS full roadside vendor list | 1 call, ≈ 2.2 MB, 2.4 – 4.3 s |

Three ways to get a provider name onto a report row, costed for a **3-month Job Report (≈ 13,000 rows, ≈ 360 distinct providers)**:

| Approach | CMS calls | Wall-clock CMS time | Data downloaded | Verdict |
|---|---|---|---|---|
| **Per row** — call the CMS for each job's provider | 13,000 | 13,000 × 1.0–1.6 s ≈ **3.5 – 6 hours** sequential; even 20 in parallel ≈ 10–18 min | 13,000 × 20 KB ≈ 260 MB | Not viable. Would also hit the CMS provider's request limits and get throttled (HTTP 429) part-way through, leaving some rows blank. |
| **Per distinct provider, batched** — collect the 360 provider IDs on the report, ask the CMS 50 at a time | 8 | ≈ 7 s | ≈ 8 × 50 × 3 KB ≈ 1.2 MB | Viable. Scales with providers, not rows. |
| **One list per report run** — download the whole roadside vendor list once, map names in memory (what the Job Report does today) | 1 | 2.4 – 4.3 s | 2.2 MB | Viable. Cost is flat whatever the date range. |
| **Mirror** — the name is already in the Roadside record the report query joins | 0 | 0 | 0 | Cheapest. Freshness = webhook. |

For a **12-month report (≈ 52,000 rows)** the per-row approach becomes 14–23 hours; the other three do not change.

**Rule that follows:** a report may make at most a handful of CMS calls per *run*, never per *row*. Any design that violates this is wrong regardless of the CMS-only decision.

---

## 5.1 Job Report (CSV / HTML)

**What it is.** The main operational export: every job in a date range for a client, 55 columns, one row per job. Downloaded by client services and used for Honda / Mercedes / Porsche billing and SLA reviews.

**How it works today.**
1. One database query builds all rows. The provider name column is `ISNULL(ua.dispName, jb.provName)`: the provider's *current* Roadside name if the record exists, else the name stamped on the job when it was saved.
2. One CMS list download per run (all vendors, active and inactive). For every row whose provider has a CMS link and appears in the list, the CMS name replaces the Roadside name.
3. If the CMS call fails: log it, keep the Roadside names, still produce the report.

So today: **1 CMS call per run**, 2.4–4.3 s added, and the report never fails because of the CMS.

### If CMS-only
- Keep step 2, drop step 3: CMS failure → the report either fails or ships with a blank provider column for all 13,000 rows. Client-facing exports going out with blank vendor names is a visible regression.
- Unpublished / archived vendors are not in the list → blank name on every historical job they served, unless the stamped `jb.provName` is kept as the last fallback. Over a year, 51,761 of 51,764 jobs resolve today; that number only goes down as vendors churn.
- Renames: both the Roadside join and the CMS overlay show the *current* name on old jobs. CMS-only does not change this. If the business wants "name as it was at the time", that is the stamped `jb.provName` — a separate decision.

**Options.** (a) Mirror name inside the SQL (0 calls; the join already exists). (b) One list call per run via cache (0 calls on cache hit). (c) Literal CMS-only: one list call, fail or blank on error. (d) Per-row: never.

**Verdict:** *Can move.* Recommended (a) with `jb.provName` kept as the last fallback for vendors that no longer exist anywhere. (c) is acceptable only if the business accepts occasional blank exports.

---

## 5.2 Complete Report (CSV)

**What it is.** Completed jobs in a date range, same 55 columns, used for month-end reconciliation.

**How it works today.** Same query model as the Job Report, but **without** the CMS overlay: it prints the Roadside name. So today a vendor renamed in the CMS shows the new name on the Job Report and the old Roadside name on the Complete Report — the two do not agree.

### If CMS-only
Same arithmetic as 5.1. Moving it to the same source as the Job Report is an improvement: the three main exports (Job, Complete, Compass) finally print one spelling.

**Verdict:** *Can move.* Recommended: mirror; add the same overlay/cache as the Job Report only if the mirror is not adopted.

---

## 5.3 Compass Report

**What it is.** The export in the Compass (insurance partner) column layout.

**How it works today.** Own query model, provider name `ISNULL(ua.dispName, jb.provName)`, no CMS overlay.

### If CMS-only
Identical to 5.2.

**Verdict:** *Can move.* Same recommendation.

---

## 5.4 Job Detail export

**What it is.** One job's full detail, including the technician vehicle and the vehicle's provider name.

**How it works today.** One database query joining vehicle → provider record. No CMS.

### If CMS-only
One job → one CMS call is affordable per export (1–1.5 s). But this export is also used in bulk by some teams (loop over a list of jobs), where it becomes the per-row case above.

**Verdict:** *Can move, with conditions.* Recommended: mirror name in the query (0 calls). If a CMS call is added, it must be one per export, cached.

---

## 5.5 Porsche XLSX job report (planned)

**What it is.** The new Excel report for Porsche (in progress) built on the same job-report query model.

### If CMS-only
Inherits whatever 5.1 does. The performance seeding done for that ticket (1,500 test jobs) can be used to prove the per-run vs per-row difference on SIT before any decision.

**Verdict:** as 5.1.

---

## 5.6 Provider Review list and summary

**What it is.** Providers by grade (see `03`, 3.3). Included here because supervisors treat it as a report.

**How it works today.** Roadside query; the list is limited to providers the CMS list returns when a name is searched; the summary is a `GROUP BY grade` in Roadside.

### If CMS-only
Grades are Roadside-only. The name search can use the cache or mirror; the summary cannot leave Roadside.

**Verdict:** *Must stay* for grades; name search can move.

---

## Where the reports stand

| Report | Provider columns | Today | CMS calls per run today → recommended | Verdict |
|---|---|---|---|---|
| Job Report | 1 (name) | Roadside name, CMS overlay, Roadside fallback | 1 → 0 | Can move (mirror) |
| Complete Report | 1 (name) | Roadside name only | 0 → 0 | Can move (mirror) — becomes consistent with Job Report |
| Compass Report | 1 (name) | Roadside name only | 0 → 0 | Can move (mirror) |
| Job Detail export | 1 (vehicle's provider name) | Roadside | 0 → 0 | Can move (mirror) |
| Porsche XLSX | 1 (name) | as Job Report | 1 → 0 | as Job Report |
| Provider Review | name + grade | Roadside + CMS gate | 0–1 → 0 | Must stay (grades) |

## Pros and cons of each way to source the report name

| | Per-row CMS | Per-run CMS list | Batched by provider | Mirror |
|---|---|---|---|---|
| Speed on 13,000 rows | hours | +3 s | +7 s | +0 |
| Speed on 52,000 rows | half a day | +3 s | +7 s | +0 |
| CMS request limits | will be throttled | safe | safe | n/a |
| Works during CMS outage | no | only with fallback | only with fallback | yes |
| Unpublished vendor on old job | blank | blank unless stamped name kept | blank unless stamped name kept | name kept |
| Freshness | live | live | live | seconds behind |
| New code needed | yes | none (Job Report has it) | some | none once the mirror exists |
