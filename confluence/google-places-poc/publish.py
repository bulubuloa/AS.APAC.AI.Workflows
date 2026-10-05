# Appends the request-flow section + 2 diagram PNGs to Confluence page 6868598827 (keeps existing content).
# Usage: python publish.py   (API token in ~/.config/atlassian/token, or ATLASSIAN_TOKEN env)
import base64, json, os, re, sys, urllib.request, uuid

SITE = 'https://internationalsos.atlassian.net/wiki'
PAGE = '6868598827'
HERE = os.path.dirname(os.path.abspath(__file__))
# Token from ATLASSIAN_TOKEN or ~/.config/atlassian/token (same file the other Confluence publishers use)
EMAIL = os.environ.get('ATLASSIAN_EMAIL', 'hoang.quach@aspirelifestyles.com')
TOKEN = os.environ.get('ATLASSIAN_TOKEN') or open(os.path.expanduser('~/.config/atlassian/token')).read().strip()
AUTH = 'Basic ' + base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
MARK_START, MARK_END = '<!-- gp-flow:start -->', '<!-- gp-flow:end -->'

def call(method, url, body=None, headers=None):
    req = urllib.request.Request(url, data=body, method=method, headers={'Authorization': AUTH, 'Accept': 'application/json', **(headers or {})})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b'{}')

def upload(path, name):
    # create-or-update attachment by filename
    boundary = uuid.uuid4().hex
    data = open(path, 'rb').read()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: image/png\r\n\r\n').encode() + data + \
           f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="minorEdit"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode()
    call('PUT', f'{SITE}/rest/api/content/{PAGE}/child/attachment', body,
         {'X-Atlassian-Token': 'nocheck', 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    print('uploaded', name)

page = call('GET', f'{SITE}/api/v2/pages/{PAGE}?body-format=storage')
body, ver, title = page['body']['storage']['value'], page['version']['number'], page['title']
open(os.path.join(HERE, f'page-v{ver}-backup.html'), 'w', encoding='utf-8').write(body)
print(f'read "{title}" v{ver} ({len(body)} chars) — backup saved')

upload(os.path.join(HERE, 'overview.png'), 'gp-flow-overview.png')
upload(os.path.join(HERE, 'sequence.png'), 'gp-flow-sequence.png')

section = MARK_START + open(os.path.join(HERE, 'section.html'), encoding='utf-8').read() + MARK_END
# Re-running replaces the previous copy of the section instead of appending twice.
if MARK_START in body:
    body = re.sub(re.escape(MARK_START) + '.*?' + re.escape(MARK_END), lambda m: section, body, flags=re.S)
else:
    body = body + section

payload = {'id': PAGE, 'status': 'current', 'title': title, 'body': {'representation': 'storage', 'value': body},
           'version': {'number': ver + 1, 'message': 'Add CMS vs Google request flow + diagrams'}}
res = call('PUT', f'{SITE}/api/v2/pages/{PAGE}', json.dumps(payload).encode(), {'Content-Type': 'application/json'})
print('updated to v', res['version']['number'], '→', SITE + res['_links']['webui'])
