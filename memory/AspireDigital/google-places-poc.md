---
name: google-places-poc
description: "Google Places POC (Sep 2026) — React app in GooglePlaceAPI.POC comparing Kontent PROD restaurants to Places API (New); keys, IP restriction, CMS data-quality facts"
metadata:
  node_type: memory
  type: project
  originSessionId: b812a07d-8c08-44da-a18a-f193e8e3059e
  modified: 2026-09-29T04:20:04.652Z
---

POC for Sanchit (due 30 Sep 2026): `GooglePlaceAPI.POC/` (Vite+React, `npm run dev` → :5188). Reads Kontent PROD via public Delivery API; Google key held server-side by the Vite proxy (`.env.local`, git-ignored). Findings in `docs/FINDINGS.md`, rows in `docs/batch-2026-09-29.md`.

- Benefit prod Google key (`GoogleMapConfiguration`, legacy `maps/api/place/`) is IP-restricted — works only from ABE NAT `abe-natgateway` 52.74.89.90 (vpc-0918f1ce2c573925d). Not in SSM/Secrets (scanned 166 APPSETTINGS params, ap-southeast-1). POC ran on a separate user-supplied test key.
- CMS data facts (PROD, 29 Sep 2026): 399 restaurant vendors / 411 locations; 4% coords (3 junk), 3% hours, 2% website; all 8 AU locations are test data; Anan Saigon tagged TH.
- Accuracy: TH 30/40 high+medium, HIGH always correct; hotel outlets need restaurant-only retry (`includedType`).

- App now defaults to Kontent UAT (`225b0999-fce9-02b4-c44b-ed6990faeeaa`, public Delivery API) with a UAT/PROD switch. UAT restaurant data is mostly test records ("Steven test…", "Daigo N", "Test Vendor N" at Oxford St) — use PROD for accuracy numbers.
- Hosted: Lambda `apac-google-places-poc` + Function URL (cookie login page; basic-auth prompt doesn't work because Function URLs remap WWW-Authenticate). Code-only updates via `aws lambda update-function-code` are allowed; creating it with the key needed the user.

- 30 Sep 2026 decision (user, after Sanchit review): **live** — CMS stores google_place_id + our own filterable values (city, country, cuisine, price, name); address/hours/phone/website/rating/photos read live from Google on the website. Minimum PD input measured: name+country 92% top-1, +postal code 100% (docs/PD-ONBOARDING.md).

**Why:** Google terms only allow storing Place ID → recommended design is store `google_place_id` on `location`, fetch the rest live.
**How to apply:** Reuse the app/findings if the ticket comes; don't propose copying Google fields into CMS. Related: [[abe-repo-aliases-and-cms-modules]].
