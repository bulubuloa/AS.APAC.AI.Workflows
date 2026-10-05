# Runs the "what if a field is missing" search scenarios through the hosted POC and saves results.
import json, subprocess, os
U = 'https://yed3iooo7fgdusqvbyiruxwjwu0gowbs.lambda-url.ap-southeast-1.on.aws'
AUTH = os.environ['POC_AUTH']
MASK = 'places.id,places.displayName,places.formattedAddress,places.primaryType,places.businessStatus'
PHILIPPE = 'ChIJ'  # filled from scenario 1

def search(body):
    r = subprocess.run(['curl', '-s', '-u', AUTH, '-X', 'POST', f'{U}/gplaces/v1/places:searchText',
                        '-H', 'Content-Type: application/json', '-H', f'X-Goog-FieldMask: {MASK}', '--data', json.dumps(body)],
                       capture_output=True, text=True, encoding='utf-8')
    d = json.loads(r.stdout)
    if 'error' in d: return {'error': d['error']['message'][:160]}
    return {'places': [{'id': p['id'], 'name': p['displayName']['text'], 'address': p['formattedAddress'], 'type': p.get('primaryType', '')} for p in d.get('places', [])]}

base = {'languageCode': 'en', 'maxResultCount': 5}
S = [
  ('full', 'All fields: name + address_line_1 + country', {'textQuery': 'Philippe, 20/15-17 Sukhumvit Soi 39, Bangkok 10110, Thailand', 'regionCode': 'TH'}),
  ('no_address', 'address_line_1 missing → name + city + country', {'textQuery': 'Philippe, Bangkok, Thailand', 'regionCode': 'TH'}),
  ('name_country', 'address and city missing → name + country', {'textQuery': 'Philippe, Thailand', 'regionCode': 'TH'}),
  ('postal', 'address missing, postal code present → name + postal code + country', {'textQuery': 'Philippe, 10110, Thailand', 'regionCode': 'TH'}),
  ('no_name', 'vendor_name missing → address + country', {'textQuery': '20/15-17 Sukhumvit Soi 39, Bangkok 10110, Thailand', 'regionCode': 'TH'}),
  ('no_country', 'country missing → name + address, no regionCode', {'textQuery': 'Philippe, 20/15-17 Sukhumvit Soi 39, Bangkok 10110'}),
  ('no_country_name_only', 'country and address missing → name only', {'textQuery': 'Philippe'}),
  ('bad_coords', 'junk CMS coordinates sent as locationBias (1232142141, 412412412)', {'textQuery': 'Philippe, 20/15-17 Sukhumvit Soi 39, Bangkok 10110, Thailand', 'regionCode': 'TH',
      'locationBias': {'circle': {'center': {'latitude': 1232142141, 'longitude': 412412412}, 'radius': 5000}}}),
  ('chain_name_country', 'chain, name + country (Hong Bao)', {'textQuery': 'Hong Bao, Thailand', 'regionCode': 'TH'}),
  ('chain_postal', 'chain, name + postal code + country (Hong Bao, 10330)', {'textQuery': 'Hong Bao, 10330, Thailand', 'regionCode': 'TH'}),
]
out = []
for key, label, body in S:
    res = search({**base, **body})
    out.append({'key': key, 'label': label, 'request': {**base, **body}, 'result': res})
json.dump(out, open('missing-fields.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for o in out:
    r = o['result']
    print('==', o['key'], '|', r.get('error') or '; '.join(f"{p['name']} ({p['address'][:45]})" for p in r['places'][:3]) or 'NO RESULTS')
