# 04 — The provider mobile app (Partner app) and provider website

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F15, F16, F17** in `features/`.


The technician side. Everything here is keyed on the provider's Roadside ID and login; almost none of it reads provider *details* at all.

---

## 4.1 Provider login

**What it is.** Technicians sign in to the mobile app (and providers to the provider website) with a username and password.

**How it works today.** The username is looked up in the Roadside provider record; the password hash and salt are compared; a token is issued carrying the Roadside ID. Three separate login endpoints (Roadside web, Partner app API, Provider website) all do this against the same record.

### If CMS-only
Not possible. The CMS is a content system with no credential store, and the roadside module's "RSA username" field is a label, not a login. Even if the CMS held usernames, it must never hold password hashes.

**Verdict:** *Must stay on Roadside.* Every provider keeps a Roadside record for as long as anyone from that provider can sign in.

---

## 4.2 Locking out a deactivated provider

**What it is.** When a provider is deactivated, its technicians should stop receiving and accepting jobs immediately.

**How it works today.** Every API request from the app passes through an authentication filter that re-reads the provider record and requires `active = 1`. Deactivating the record in Roadside blocks the app on the very next request. Vehicles are also filtered on the provider's Active flag in the dispatch query, so an inactive provider's trucks stop being offered.

### If CMS-only
- If "active" lives only in the CMS, the per-request filter would have to ask the CMS on every app request: thousands of calls per hour, 0.2–1.5 s each, on the hot path of GPS updates and job acceptance. Not viable.
- Through a cache: viable but makes lock-out latency = cache age, and makes the auth filter depend on the cache being warm.
- Mirror: the sync copies CMS status into the Roadside Active flag; lock-out latency = webhook latency (seconds); the filter is unchanged.

**Verdict:** *Must stay on Roadside* (the flag), fed by the mirror. Without this, deactivating a vendor in the CMS does **not** stop its technicians.

**Decision needed:** what CMS state means "deactivated" — status = inactive, unpublished, or archived (see `08`, complication 3). Today the code treats CMS status `active` as the only "active" value and, on the detail page, overlays it onto the Roadside flag.

---

## 4.3 Vehicles, GPS position, accepting and updating jobs, photos, directions

**What it is.** Everything the technician does after login: register a vehicle, send position, see assigned jobs, accept, mark reached / complete, upload photos, get directions.

**How it works today.** All keyed on the Roadside provider ID from the token and the vehicle ID. The app never displays the provider's own CMS details; it shows job and customer data.

### If CMS-only
No provider detail is read, so nothing changes — provided the Roadside record (and therefore the ID) exists.

**Verdict:** *Unaffected.*

---

## Summary for this area

| Feature | Verdict | Note |
|---|---|---|
| Login | Must stay | Credentials only exist in Roadside |
| Lock-out | Must stay | Per-request Active check; mirror must copy CMS status |
| Vehicles / GPS / job updates | Unaffected | Keyed on Roadside ID, no provider details read |
