# 02 — Job screens

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F05, F06, F07, F08, F09** in `features/`.


Five places show provider information on an existing job. They differ mainly in *how often* they refresh, which decides whether a CMS call per refresh is realistic.

---

## 2.1 Job detail page (the job form)

**What it is.** The page an agent opens for one job: customer, vehicle, service, and the assigned provider's name.

**How it works today.** One database query loads the job, the assigned vehicle and the provider record (name, CMS link). If the provider has a CMS link, Roadside calls the CMS for that one vendor (1.0–1.6 s) and shows the CMS name instead; on CMS failure the Roadside name is shown. The same overlay runs when the form is re-loaded after a save.

**Volume.** Every job open ≈ several thousand a day across agents (each job is opened many times over its life). One CMS call per open today.

### If CMS-only
- Per-open CMS call stays; the fallback goes. A vendor that is **unpublished** in the CMS returns nothing → the open job shows a blank provider name, even though a technician is on the way.
- A CMS outage → every open job shows a blank provider.
- Page load gains ~1–1.5 s per open compared with reading the mirror.

**Options.** (a) Read the name from the mirror: 0 CMS calls, no blanks, freshness = webhook. (b) CMS via cache: milliseconds, blanks only for unpublished vendors. (c) Literal CMS-only per open.

**Verdict:** *Can move, with conditions.* Recommended (a). The rule for unpublished vendors (`08`, complication 3) must exist before (b) or (c).

---

## 2.2 Live job monitor board

**What it is.** A wall-board style page listing open jobs with status, vehicle and provider name, pushed to every open browser in real time (SignalR) whenever a job changes.

**How it works today.** Each push re-runs one database query over all open jobs, joined to vehicle and provider record for the display name, renders the HTML once and broadcasts it. No CMS involvement.

**Volume.** One re-render per job event (save, accept, reach, complete, cancel, message) — hundreds per hour in the day shift. Each render lists every open job, typically dozens to low hundreds.

### If CMS-only
- Per render, the board would need the current CMS name for every provider on the board. Per-row CMS calls: 50–150 calls × 1 s = the board falls a minute behind after every event. Per-render full-list download: 2–4 s per event, and the download is 2.2 MB each time; at hundreds of events per hour that is gigabytes per day for a name column.
- Through a cache: feasible, but the board is rendered server-side inside an event handler, so the cache becomes a hard dependency of the real-time path.
- The only design that keeps the board instant is reading the name from the mirror inside the existing query.

**Verdict:** *Must stay on Roadside* for the name column. The mirror must carry the CMS name.

---

## 2.3 Job action list and message monitor

**What it is.** The paged list of job events / actions agents scroll through, and the list of customer messages per job.

**How it works today.** Database queries joined to the provider record for `provDispName`. No CMS.

**Volume.** Per page view; each page lists up to a few hundred rows.

### If CMS-only
Same arithmetic as the monitor board but without the real-time constraint: one cached list lookup per page render is fine; per-row CMS calls are not. Reading from the mirror is free.

**Verdict:** *Can move, with conditions* (cache or mirror). Recommended: mirror.

---

## 2.4 Customer tracking link

**What it is.** The public page a customer opens from the SMS to watch the technician approach. Shows the technician vehicle and the provider's name.

**How it works today.** One database query, provider name from the Roadside record. No CMS.

**Volume.** Every customer click on the link, often repeatedly while waiting. This page is public-facing and hit from mobile networks.

### If CMS-only
- A CMS call per customer refresh adds 1–1.5 s to a page customers reload while stressed at the roadside, and makes a public page depend on a third-party API.
- If the provider is unpublished mid-job: the customer sees a blank company name for the truck that is coming.

**Options.** (a) Mirror name — instant, no dependency. (b) Cache — fine. (c) Literal CMS-only — poor.

**Verdict:** *Can move, with conditions.* Recommended (a).

---

## 2.5 Map markers (all technician vehicles)

**What it is.** The dispatch map showing every ready technician vehicle with provider name, group icon (Honda / Porsche pins), phone and licence plate.

**How it works today.** Database query over vehicles + provider records (no CMS gate, because most operational providers were not in the CMS when this was written). Then one full CMS list download to overlay name / group / phone on CMS-linked providers, and one CMS call per vehicle with a CMS link for vehicle details. Failures per row keep the Roadside values.

**Volume.** Every map load and refresh; ~1,000 vehicles; today ≈ 1 list download + up to hundreds of vehicle calls per load. This is already the heaviest CMS consumer in the system.

### If CMS-only
- Removing the fallback means a single failed vehicle call blanks that pin; a failed list download blanks every name on the map.
- The vehicle-level CMS calls (one per vehicle) are the real cost: at 0.2–1.5 s each, a map with 300 ready vehicles spends 1–7 minutes of CMS time per load, mitigated today only by running them in parallel.
- A cache fixes the list; vehicle details would need the same treatment (vehicle mirror or batched ID lookups, 50 per call ≈ 0.9 s).

**Verdict:** *Can move, with conditions.* Prerequisites: cache for the vendor list, batched or mirrored vehicle lookups, and the group-name spelling rule (the pin icon code already handles both "Honda" and "Honda RSA").

---

## Summary for this area

| Feature | Refresh rate | Verdict | CMS calls per refresh (today → recommended) |
|---|---|---|---|
| Job detail page | per open | Can move, with conditions | 1 → 0 (mirror) |
| Live monitor board | per job event, real time | Must stay | 0 → 0 |
| Job action / message lists | per page | Can move, with conditions | 0 → 0 (mirror) |
| Customer tracking link | per customer refresh | Can move, with conditions | 0 → 0 (mirror) |
| Map markers | per map load | Can move, with conditions | 1 list + up to hundreds → 0 list (cache) + batched vehicles |
