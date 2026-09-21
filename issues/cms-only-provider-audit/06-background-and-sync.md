# 06 — Background jobs, the sync, deletion and environments

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F20, F21, F22, F23** in `features/`.


The parts nobody sees on a screen, which is exactly why they drift.

---

## 6.1 Lost-signal alerts to technicians

**What it is.** A timer inside the Roadside application checks every few minutes for technician vehicles that are on shift, have a push token, belong to an **active** provider, and have not reported a GPS position for 10 minutes; it sends them a push warning and records that it did.

**How it works today.** One database query (`VW_Vehicle` joined to provider records with `ua.active = 1`), then one push per vehicle. Runs on a fixed schedule from application start.

### If CMS-only
- The Active gate is inside the SQL. To take it from the CMS the timer would download the vendor list every tick (2–4 s, 2.2 MB, every few minutes, forever) or read a cache.
- Timers run outside any web request; a cache built for web requests must also be reachable from here, and a CMS outage would silently stop or mis-target alerts.

**Verdict:** *Must stay on Roadside* (Active flag in the record, fed by the mirror).

---

## 6.2 The Benefit → Roadside sync (v1 and v2)

**What it is.** When a vendor is created or edited in the Benefit portal, the portal calls a Roadside endpoint that creates or updates the provider record (and, separately, its vehicles).

**How it works today.**
- **v1** (`ProviderSyncData`) copies: login, display name, phone, group, email, **active**, **mobile provider**, note, **country**, Benefit vendor ID, CMS link.
- **v2** (`ProviderSyncDataVer2`, the live path) copies: display name, login (only if sent), phone, **active**, Benefit vendor ID, group, note (fetched from the CMS if not sent), CMS link, vehicles. It does **not** copy mobile provider, country or email — on create the mobile flag is left empty, on update it is left as it was.
- New providers get a Roadside ID minted here (`2-` + next number). A record is never deleted by the sync; a separate delete endpoint marks it deleted.
- The Benefit portal calls the sync only when *it* saves. A change made in the CMS editor directly, or a publish that happens later than the save, never reaches Roadside.

**The drift, measured:** 317 active providers whose CMS module says "mobile vendor: yes" and whose Roadside record says no. 274 of them are migration-era rows (`StatusSysnData = 'Success'`), 40 were updated through v2, 3 were created through v2. The oldest-known example was last updated by the sync on 11 Nov 2025 and has been invisible to Auto mode since.

### If CMS-only
The sync is not optional under any design: the Roadside record must exist for login, IDs, vehicles, grades and the Benefit vendor ID. What changes is its *role*: from "the portal pushes a subset" to "the CMS drives a complete mirror".

**Changes needed (details in `07`):**
1. Complete the field mapping in v2 (mobile, country, email) — small, ships now, ends the drift.
2. Trigger from the CMS (webhook on publish / unpublish / archive), not only from the portal save.
3. Nightly reconciliation to repair anything a webhook missed.
4. Retire v1 or make it call the same code as v2.

**Verdict:** *Must keep running, and be fixed first.*

---

## 6.3 Deletion and "unpublish"

**What it is.** What Roadside does when a vendor is deleted or taken down on the Benefit / CMS side.

**How it works today.** The portal calls a delete endpoint that marks the Roadside record `isDelete = 1` (soft delete); vehicles are deleted by a separate endpoint. An **unpublished** CMS item, on the other hand, triggers nothing — Roadside simply stops finding it in CMS reads, while the Roadside record stays active.

### If CMS-only
- With no fallback, "unpublished" becomes "gone" everywhere the CMS is read (search, detail, lists, job pages), while the record — and its vehicles and logins — keep working. Technicians of an unpublished vendor still receive jobs; agents cannot see who they are.
- A physical delete in the CMS of a vendor with history leaves thousands of jobs pointing at a name nobody can resolve; only the stamped name on each job survives.

**Rule to adopt:** unpublish / archive → mirror sets Active = 0 (never deletes); delete in CMS → mirror sets Active = 0 and flags for manual review; the stamped job name is never overwritten.

**Verdict:** *Decision needed before any switch* (see `08`, complications 3 and 5).

---

## 6.4 Environments (SIT, UAT, pre-prod, production)

**How it works today.** Each Roadside site reads its CMS environment ID from its configuration; SIT and pre-prod have no value set, so the code's built-in default — the **production** CMS — is used. UAT was pointed at a shared SIT/UAT CMS environment in August 2026. Pre-prod points at production on purpose. The Benefit portal environments have their own mapping.

### If CMS-only
- SIT and pre-prod screens would show production vendors against SIT / pre-prod Roadside records: no CMS links match, every provider screen is empty, and testers cannot reproduce anything.
- Worse, with the CMS as master, a webhook from the production CMS to a test Roadside — or from a test CMS to production — would rewrite provider records across environments.

**Verdict:** *Fix first.* One CMS environment per Roadside environment, configured explicitly, and webhooks locked to their own pair.

---

## Summary for this area

| Item | Verdict | Why |
|---|---|---|
| Lost-signal alerts | Must stay | Active flag inside a scheduled SQL query |
| Sync v1 / v2 | Must keep and fix | The mirror *is* the sync; v2 drops three fields today |
| Deletion / unpublish | Decision needed | "Not published" and "not active" are different things; history must survive |
| Environments | Fix first | Test sites silently read production CMS |
