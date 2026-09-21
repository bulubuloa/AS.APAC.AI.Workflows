# 01 — Dispatching a job

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F01, F02, F03, F04** in `features/`.


Four features are involved between an agent opening a new job and a technician being assigned. Two of them can read the CMS; two cannot.

---

## 1.1 The Provider search box (Auto and Manual mode)

**What it is.** On the job form the agent types part of a provider name and picks one from the drop-down. In Auto mode the list is limited to "mobile" providers (those with technician vehicles on the app); in Manual mode any active provider is offered.

**How it works today.**
1. The browser sends every keystroke to Roadside (`/api/autofill/providername`). The box is set to `minLength: 0`, so simply clicking into it sends an empty search.
2. Roadside runs two searches in parallel:
   - its own database: providers whose name or login contains the text, Active, not deleted, and — in Auto mode — whose *Roadside* Mobile flag is on;
   - the CMS: the full vendor list is downloaded (~2.2 MB, 2.4–4.3 s), filtered in memory by name and, in Auto mode, by the *CMS* mobile flag; any matches are looked up back in the Roadside database by CMS link — and that lookup applies the *same* Roadside Mobile filter.
3. Results are merged, de-duplicated, sorted, and the first 10 returned. The Roadside provider ID is what gets saved on the job.
4. If the Roadside query throws, a legacy SQL query is used instead. If the CMS call throws, the Roadside results are used alone.

**Why it is broken today.** Step 2 filters on the Roadside Mobile flag in both branches. The sync that creates provider records never copies that flag, so 317 active providers whose CMS record says "mobile vendor: yes" have Mobile = no in Roadside and are never offered in Auto mode. The provider *page* reads the CMS live and shows Mobile ticked, which is why the screen and the search disagree.

**Volume.** Every keystroke by every agent. 8,338 Auto-mode jobs in 90 days ≈ 90 per day; with 3–8 keystrokes per search that is several hundred CMS list downloads per day today.

### If CMS-only

**Option A — call the CMS on every keystroke, nothing else (literal reading of the premise).**
- Each keystroke: 1 full-list download (2.4–4.3 s). Agents wait seconds per character; typing fast queues several downloads.
- No Roadside filter, so the 317 hidden providers appear. But 24 active providers filed outside "Roadside Assistance" in the CMS and 7 with no CMS record disappear from search entirely.
- Login-name matches stop working (the CMS list can only be searched by vendor name). Names with suffixes (`… CO., LTD._10697`) or Thai aliases stored only in Roadside no longer match.
- If the CMS is slow or down: empty drop-down, no dispatch possible.
- Pros: exactly what the CMS editor sees; fixes the mobile-flag drift by construction.
- Cons: unusably slow without a cache; loses 31 providers; loses login-name search; single point of failure for dispatch.

**Option B — CMS through an in-memory cache inside Roadside.**
- Roadside keeps the CMS vendor list in memory, refreshed every 60 s or when the CMS webhook fires. A keystroke searches memory: milliseconds.
- Same 31-provider and login-name losses as A unless the roadside-vendor definition in the CMS is fixed (see `07`, change 8).
- CMS outage: the cache keeps serving the last good list; dispatch continues on stale-by-minutes data.
- Pros: fast; CMS-fresh within a minute; survives short CMS outages.
- Cons: still needs the CMS data clean-up first; a new component to build and monitor; the "no fallback" premise is technically violated by the cache itself.

**Option C — search the Roadside mirror (recommended).**
- The mirror carries the CMS name and mobile flag (once the sync is complete). The search stays a database query — the same query that already works — and can match on CMS name *and* Roadside login.
- Zero CMS calls per keystroke. No new component. Works during CMS outages.
- Freshness = webhook latency (seconds) rather than zero.
- Pros: fastest, cheapest, keeps every current match, fixes the drift the moment the sync copies the flag.
- Cons: depends on the mirror being complete and the webhook being reliable; a vendor changed in the CMS is visible only after the webhook lands.

**Verdict:** *Can move, with conditions.* Recommended: C, with B as the "must be live to the second" upgrade if the business asks for it. A is not viable.

**Decisions needed:** confirm the CMS mobile flag (687 of 752 vendors are flagged mobile, including call centres); re-file the 24 misfiled vendors; decide the 7 unlinked ones.

**Effort:** C = small (once the sync is fixed). B = medium. A = small to code, unacceptable to run.

---

## 1.2 Finding the nearest technicians (Auto mode)

**What it is.** After the agent saves an Auto-mode job with the customer's location and service type, the system finds technician vehicles that are ready, within range (10 km, or the job's own radius), offer that service, and belong to an active provider; it computes distance and price for each; the agent picks one and the app pushes the job to that vehicle.

**How it works today.** One database query does all of it: vehicles joined to their provider record (`ua.active = 1`), joined to the provider's grade, filtered by GPS distance (`fn_LinearKm`), by service type, and excluding vehicles already on a job. The result carries the provider's display name, group and phone for the map pins. The same query shape is reused for the "previous result" view, the single-vehicle direction, and the map markers.

**Volume.** Every Auto-mode job save and every "find again" click; 82 providers / 8,338 jobs in 90 days. Each run scans ~1,000 vehicles.

### If CMS-only

There is no option that removes the Roadside record from this query:
- The CMS does not know vehicles, GPS positions, ready / on-job state, service lists, grades or distance.
- The "active" gate is inside the SQL join. To take it from the CMS, Roadside would have to fetch the CMS list (2–4 s) on every dispatch, then post-filter the SQL result in memory. That is slower and duplicates logic that already exists.
- Display name / group / phone on the pins can come from the mirror (they already do) or from the CMS overlay that the map markers already apply.

**Verdict:** *Must stay on Roadside.* The provider's Active flag, ID and grade must be in the Roadside database. Only the *display* fields could come from the CMS, and they already can.

**What CMS-master changes here:** nothing in the query; only that the Active flag it reads is now guaranteed to equal the CMS status because the mirror copies it.

---

## 1.3 Saving the job with the chosen provider

**What it is.** When the job is saved with a provider (picked from the box, or attached via the chosen vehicle), Roadside stamps the provider's name on the job record. That stamped name is what the customer link, the monitor board and the reports show.

**How it works today.**
1. Roadside looks the provider up by ID in its database (name + CMS link). If there is no record, the provider ID is cleared from the job.
2. If the record has a CMS link, Roadside calls the CMS for that one vendor (1.0–1.6 s) and uses the CMS name; on any CMS error it keeps the Roadside name.
3. On Honda / Mercedes benefit jobs, an agent may also *type* a provider name without picking one. Roadside then looks for exactly one active provider with that exact Roadside display name; if none or several, the save is rejected ("The provider X is invalid for the privilege benefit").

**Volume.** Every job save ≈ 150 per day. One CMS call per save today.

### If CMS-only

- Step 1 (the existence check) needs the Roadside record; without it the job cannot carry a provider ID, and the ID is what everything downstream keys on.
- Step 2 already prefers the CMS. Removing the fallback means: CMS error → blank provider name on a saved job. The job still saves; the name is missing on the monitor board, the customer link and every report until someone re-saves.
- Step 3 must match the typed name against the CMS spelling. Agents who type the Roadside spelling from memory get the rejection message.

**Options.** (a) Keep step 2 as is and read the name from the mirror instead of calling the CMS per save (0 calls, same name once the mirror is complete). (b) Keep the per-save CMS call but through the cache. (c) Literal CMS-only: per-save CMS call, blank on failure.

**Verdict:** *Can move, with conditions.* Recommended (a). The name stamped on the job should always be written — it is the historical record that reports rely on — so a blank-on-failure design is a regression.

**Decision needed:** whether hand-typed provider names remain allowed on benefit jobs at all, now that the search box can offer every CMS vendor.

---

## 1.4 Honda / Mercedes benefit check when saving a job

**What it is.** For Honda (client 380) and Mercedes (client 338) jobs, Roadside asks the Benefit system whether the chosen provider is allowed for the customer's privilege before the job can be saved or redeemed.

**How it works today.** Roadside sends the customer, privilege, service and provider to the Benefit system. Since an earlier fix, the provider is identified by a **Benefit vendor ID** stored on the Roadside provider record (copied by the sync), instead of by name — name matching failed whenever the two systems spelled a vendor differently. The provider name is still sent alongside for display.

**Volume.** Every Honda / Mercedes job save and redemption.

### If CMS-only

The Benefit vendor ID is not a CMS field; it comes from the Benefit portal's own database via the sync. If the Roadside record stops being written by the sync, the ID disappears and the check falls back to matching by name — the exact failure the earlier fix removed. There is no CMS-side substitute unless the Benefit portal publishes its vendor ID into the CMS (possible, but a change on the Benefit side).

**Verdict:** *Must stay on Roadside* (or the CMS must start carrying the Benefit vendor ID, which is a change to the CMS content model, see `07` change 4).

---

## Summary for this area

| Feature | Verdict | Recommended route | CMS calls per action (today → recommended) |
|---|---|---|---|
| Provider search box | Can move, with conditions | Search the mirror; cache if live-to-the-second is required | 1 full list per keystroke → 0 |
| Nearest technicians | Must stay | Keep the SQL; mirror guarantees Active is correct | 0 → 0 |
| Saving the job | Can move, with conditions | Name from the mirror | 1 per save → 0 |
| Benefit check | Must stay | Keep Benefit vendor ID on the Roadside record | 0 → 0 |
