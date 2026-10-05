# Builds GooglePlaceAPI.POC/docs/CMS-VS-GOOGLE-FLOW.md from the diagram sources and the captured example responses.
import json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.join(HERE, '..', '..', '..', 'GooglePlaceAPI.POC')
E = '994226e6-d1a5-023e-0fc9-21571d884f47'
j = lambda o: json.dumps(o, indent=2, ensure_ascii=False)
rd = lambda f: json.load(open(os.path.join(HERE, f), encoding='utf-8'))

os.makedirs(os.path.join(POC, 'docs', 'img'), exist_ok=True)
shutil.copy(os.path.join(HERE, 'overview.png'), os.path.join(POC, 'docs', 'img', 'flow-overview.png'))
shutil.copy(os.path.join(HERE, 'sequence.png'), os.path.join(POC, 'docs', 'img', 'flow-sequence.png'))

js = open(os.path.join(HERE, 'diagrams.mmd.js'), encoding='utf-8').read()
src = dict(re.findall(r'(\w+): `(.*?)`', js, flags=re.S))

a1 = rd('ex-a1.json')['items'][0]
a1s = {'system': {'codename': a1['system']['codename'], 'type': a1['system']['type']},
       'elements': {k: {'value': v['value']} for k, v in a1['elements'].items()}}
a2 = rd('ex-a2.json')['item']
keep = ['location_name', 'address_line_1', 'city', 'province', 'country', 'postal_code', 'lattitude', 'longitude', 'monday_hours']
a2s = {'system': {'codename': a2['system']['codename'], 'type': a2['system']['type']},
       'elements': {k: {'value': a2['elements'][k]['value']} for k in keep if k in a2['elements']}}
b1req, b1 = rd('ex-b1-body.json'), rd('ex-b1.json')
b2req, b2 = rd('ex-b2-body.json'), rd('ex-b2.json')
b4 = rd('ex-b4.json')
b4s = dict(b4)
b4s['addressComponents'] = [{'longText': c['longText'], 'types': c['types']} for c in b4['addressComponents']
                            if set(c['types']) & {'street_number', 'route', 'sublocality_level_1', 'locality', 'postal_code', 'country'}]
b4s['photos'] = [{'name': b4['photos'][0]['name'][:60] + '…', 'widthPx': b4['photos'][0].get('widthPx'),
                  'heightPx': b4['photos'][0].get('heightPx')}, '… (10 photos)']
photo = b4['photos'][0]['name']
loc = [l for l in open(os.path.join(HERE, 'ex-b5.txt')) if l.lower().startswith('location')][0].split(': ', 1)[1].strip()

FENCE = '```'
doc = f"""# CMS vs Google — request flow

Every call the **CMS vs Google** tab makes, in order, with URL, parameters and a real example.
Same content as Confluence: [POC - Kontent CMS vs Google Place APIs](https://internationalsos.atlassian.net/wiki/spaces/AD/pages/6868598827/POC+-+Kontent+CMS+vs+Google+Place+APIs) §6.

- `{{app}}` = POC host: `https://yed3iooo7fgdusqvbyiruxwjwu0gowbs.lambda-url.ap-southeast-1.on.aws` (or `http://localhost:5188` locally). It adds the Google key — the browser never sees it.
- `{{env}}` = Kontent environment: UAT `225b0999-fce9-02b4-c44b-ed6990faeeaa` · PROD `{E}`.
- Nothing is written to Kontent; results live in the browser until reload.

## Diagrams

### Overview

![Overview](img/flow-overview.png)

{FENCE}mermaid
{src['overview']}
{FENCE}

### Sequence

![Sequence](img/flow-sequence.png)

{FENCE}mermaid
{src['sequence']}
{FENCE}

Diagram source: `ai-workspace/confluence/google-places-poc/diagrams.mmd.js` (PNGs rendered with `render.html`).

## Steps, URLs and parameters

| # | Step | Request | Parameters |
|---|---|---|---|
| A1 | Load vendors | `GET https://deliver.kontent.ai/{{env}}/items` | `system.type=template_generic`, `limit=1000`, `skip=0,1000,…`, `depth=0`, `elements=vendor_name,vendor_status,category_text,sub_category_text,website,phone_code,phone_number,office_address,short_description,description,image,logo,location,vendor_country,module_dynamic_category` |
| A2 | Load locations | `GET https://deliver.kontent.ai/{{env}}/items` | `system.type=location`, `limit=1000`, `skip=0,…`, `depth=0` |
| A3 | Build the list (browser) | — | keep vendors whose `sub_category_text` contains "restaurant" or `category_text` contains "food and wine"; one row per linked `location` |
| B1 | Text Search | `POST {{app}}/gplaces/v1/places:searchText` → `POST https://places.googleapis.com/v1/places:searchText` | Header `X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.location,places.types,places.primaryType,places.businessStatus`. Body: `textQuery` = vendor_name + address_line_1 (or city / province) + country name; `regionCode` = location.country (e.g. `TH`); `languageCode=en`; `maxResultCount=5`; `locationBias` = 5 km circle around CMS lat/lng (only if valid) |
| B2 | Retry (sometimes) | same as B1 | + `includedType=restaurant`; only if no result or the best is a hotel / not food / closed / weak; results merged |
| B3 | Compare (browser) | — | name, CMS address words in Google address, distance to CMS pin, food type → sort, label HIGH / MEDIUM / AMBIGUOUS / LOW / NONE |
| B4 | Place Details | `GET {{app}}/gplaces/v1/places/{{placeId}}?languageCode=en` → `GET https://places.googleapis.com/v1/places/{{placeId}}` | Header `X-Goog-FieldMask: id,displayName,formattedAddress,addressComponents,location,types,primaryType,businessStatus,googleMapsUri,nationalPhoneNumber,internationalPhoneNumber,websiteUri,regularOpeningHours,currentOpeningHours,rating,userRatingCount,priceLevel,editorialSummary,photos,…` |
| B5 | Photos (×4) | `GET {{app}}/gplaces/v1/places/{{placeId}}/photos/{{ref}}/media?maxWidthPx=320` | Google answers 302 → `lh3.googleusercontent.com`; the browser loads the image |
| B6 | Show result (browser) | — | candidates, Google card, field table; kept in memory only |
| C | Pick another candidate | B4 + B5 for that `placeId` | table redrawn, "manually corrected" — not saved |

**Per restaurant:** 1 Text Search + 1 Place Details (+1 Text Search on retry) + up to 4 photos. Only name, address/city, country and optionally coordinates are sent to Google — no customer data.

## Worked example — Savelberg (Kontent PROD), captured 30 Sep 2026

### A1. Vendor

{FENCE}
GET https://deliver.kontent.ai/{E}/items?system.type=template_generic&limit=1000&skip=0&depth=0&elements=vendor_name,category_text,sub_category_text,location,…
{FENCE}

Response (the Savelberg item, trimmed):

{FENCE}json
{j(a1s)}
{FENCE}

### A2. Location

The codename in `location` is looked up in the location list. Item (trimmed):

{FENCE}json
{j(a2s)}
{FENCE}

### B1. Text Search

{FENCE}
POST {{app}}/gplaces/v1/places:searchText
Content-Type: application/json
X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.location,places.types,places.primaryType,places.businessStatus
{FENCE}

{FENCE}json
{j(b1req)}
{FENCE}

Response — Google returns only the **hotel** (the CMS address is the old one; the restaurant moved), so the match is
flagged "matched a hotel" and the retry runs:

{FENCE}json
{j(b1)}
{FENCE}

### B2. Retry with `includedType`

{FENCE}json
{j(b2req)}
{FENCE}

Response — the restaurant itself, at its new address:

{FENCE}json
{j(b2)}
{FENCE}

### B4. Place Details

{FENCE}
GET {{app}}/gplaces/v1/places/{b4['id']}?languageCode=en
X-Goog-FieldMask: id,displayName,formattedAddress,addressComponents,location,primaryType,businessStatus,googleMapsUri,internationalPhoneNumber,websiteUri,regularOpeningHours.weekdayDescriptions,currentOpeningHours.openNow,rating,userRatingCount,priceLevel,photos
{FENCE}

Response (address components and photos trimmed):

{FENCE}json
{j(b4s)}
{FENCE}

### B5. Photo

{FENCE}
GET {{app}}/gplaces/v1/{photo}/media?maxWidthPx=320

HTTP/1.1 302 Found
location: {loc[:90]}…
{FENCE}

### Result

**MEDIUM** — the name matches, the CMS address does not (the restaurant moved). The comparison shows Address = *differs*;
District, Postal code, Coordinates, Hours, Phone, Website = *CMS empty → Google has it*.

### PD onboarding equivalent

PD types Name = "Savelberg", Postal code = "10120", Country = Thailand →
`textQuery` = `"Savelberg, 10120, Thailand"`, `regionCode` = `"TH"` → exactly **1 result**: Savelberg, 136/1 Soi Yen Akat 2, Yan Nawa.
"""
open(os.path.join(POC, 'docs', 'CMS-VS-GOOGLE-FLOW.md'), 'w', encoding='utf-8').write(doc)
print('written', len(doc), 'chars')
