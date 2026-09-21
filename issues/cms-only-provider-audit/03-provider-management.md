# 03 — Managing providers in GAN

> Summary of this area. Full per-feature analysis with architecture and workflow diagrams, load arithmetic and pros/cons: **F10, F11, F12, F13, F14** in `features/`.


The screens the operations team uses to see and maintain providers. Two of them already read the CMS; they are a useful preview of the CMS-only experience, including its gaps.

---

## 3.1 Provider list

**What it is.** The searchable list of all providers (ID, login, name, group, status), used to find a provider and open its detail.

**How it works today.** Roadside lists its own provider records. If the user typed a search, the CMS list is downloaded (2.4–4.3 s) and used as an *additional* way to match (by CMS name), then CMS values are overlaid on matched rows. An earlier version gated the list on the CMS — "show only providers the CMS returned" — and the screen went blank for every provider the CMS did not know, so it was changed to the current "add, never remove" rule.

**Volume.** Per page view; 719 active + inactive rows.

### If CMS-only
- The list *is* the CMS vendor list: 752 roadside vendors. Compared with Roadside's 719 active: 31 active Roadside providers are not in it (24 filed outside "Roadside Assistance" — five towing companies among them — and 7 with no CMS record), and the CMS list includes vendors with no Roadside record yet (never synced), which the operations team cannot act on because they have no ID, login or vehicles.
- Search by login name, by Roadside ID and by the Roadside spelling of a name stops working.
- Sorting / paging over a 2.2 MB JSON download per view instead of a database page: 2–4 s per view, or a cache.

**Options.** (a) Mirror as the list source, CMS name and status included: instant, complete, searchable by every field. (b) CMS via cache: complete from the CMS's point of view, missing the 31 until re-filed, no ID / login search unless the cache is joined to Roadside anyway. (c) Literal CMS-only.

**Verdict:** *Can move, with conditions.* Recommended (a). This screen exists to manage *Roadside* providers; a list that cannot show the Roadside ID or login does not do its job.

---

## 3.2 Provider detail page

**What it is.** One provider's name, login, contact, group, country, note, Active and Mobile Provider flags, plus its vehicles.

**How it works today.** Loads the Roadside record, then calls the CMS for that vendor (1.0–1.6 s) and replaces every field the CMS has a value for — including Active and Mobile. All fields are read-only on screen. On CMS failure the Roadside values show.

### If CMS-only
Already CMS-first. Removing the fallback means: CMS failure → empty form; unpublished vendor → empty form. The vehicle sub-list stays on Roadside regardless (vehicles are not in the CMS).

**Verdict:** *Already on the CMS.* No user-visible change on a good day. This page is also the reason the current drift went unnoticed: it shows the CMS truth while the search box uses the Roadside copy.

---

## 3.3 Provider review and grades

**What it is.** Supervisors grade providers (A/B/C…) and review the list by grade; the summary counts providers per grade.

**How it works today.** Grades live in a Roadside table keyed by provider ID. The list joins provider records to grades; when a name search is typed, the CMS list is downloaded and the results are limited to providers the CMS returned. The summary is a `GROUP BY grade` over the Roadside table.

### If CMS-only
- Grades are not CMS data and never will be; the join needs the Roadside ID.
- The name search can read the CMS (cache) or the mirror.
- The summary cannot be computed from the CMS at all.

**Verdict:** *Must stay on Roadside.* Only the name search could move; on the mirror it already would.

---

## 3.4 Vehicle health / vehicle summary screens

**What it is.** Lists of technician vehicles per provider with health (token, GPS age) and service coverage.

**How it works today.** The CMS list is downloaded first, and the vehicle query is limited to providers whose CMS link is in that list. Vehicle data is Roadside.

### If CMS-only
Already CMS-gated. The 31 providers not in the CMS list are already missing here — the operations team simply has not noticed because those providers have few vehicles. A cache removes the 2–4 s per view.

**Verdict:** *Already on the CMS.* Add the cache; fix the 31 in the CMS.

---

## 3.5 Editing a provider directly in Roadside

**What it is.** Historically, admins could edit a provider (name, contact, group, Active, note) in Roadside. The screen is now read-only, but the underlying save API (`AccInfo` POST) still accepts those fields for provider accounts, and the password-reset API is separate and still needed.

### If CMS-only / CMS-master
This path must be closed for provider accounts (kept for staff accounts). As long as it exists, a well-meaning admin fix "just in Roadside" recreates the drift, and with no fallback the drift now has nowhere to hide: the CMS wins on the next sync and the admin's change vanishes, or the sync never runs and the two disagree forever.

**Pros of closing it:** one writer, one truth. **Cons:** urgent operational fixes (wrong phone number at 2 a.m.) must go through the Benefit portal / CMS and wait for publish + webhook. Decide whether an emergency override is needed and, if so, make it write to the CMS, not to Roadside.

**Verdict:** *Must be closed.*

---

## Summary for this area

| Feature | Verdict | Recommended route | CMS calls per view (today → recommended) |
|---|---|---|---|
| Provider list | Can move, with conditions | Mirror | 0–1 list → 0 |
| Provider detail | Already on the CMS | Keep; via cache | 1 → 0 (cache hit) |
| Provider review / grades | Must stay | Grades in Roadside; search on mirror | 0–1 list → 0 |
| Vehicle health / summary | Already on the CMS | Cache | 1 list → 0 (cache hit) |
| Direct edit | Must be closed | Remove for provider accounts; emergency path writes to CMS | — |
