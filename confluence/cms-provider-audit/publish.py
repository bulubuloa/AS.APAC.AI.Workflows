"""Pass 1: create pages with diagram placeholders. Pass 2: upload PNGs, embed, resolve links, update."""
import json, os, re, subprocess, sys, html
from convert import load_docs, extract_mermaid, to_html, link_rewriter, figure, PARENT, OUT

SPACE = "64782337"; SITE = "https://internationalsos.atlassian.net"
STATE = f"{OUT}/state.json"
state = json.load(open(STATE)) if os.path.exists(STATE) else {"pages": {}, "media": {}}
def save(): json.dump(state, open(STATE, "w"), indent=1)

def twg(*args):
    r = subprocess.run(["twg", *args], capture_output=True, text=True); return r

def create(title, body, parent):
    p = f"{OUT}/_body.html"; open(p, "w", encoding="utf-8").write(body)
    r = twg("confluence", "content", "create", "--space-id", SPACE, "--parent-id", parent, "--content-type", "page", "--title", title, "--body-file", p, "--format", "html", "--ack-body-formats", "--content-width", "wide", "-y", "-o", "json")
    m = re.search(r'stdout: "([^"]+)"', r.stdout)
    d = json.load(open(m.group(1))) if m else json.loads(r.stdout)
    if not d.get("data", {}).get("ok", True) and "content" not in d.get("data", {}): raise SystemExit(f"create failed {title}: {r.stdout[-600:]}")
    return d["data"]["content"]["id"]

def update(pid, body, version, msg):
    p = f"{OUT}/_body.html"; open(p, "w", encoding="utf-8").write(body)
    r = twg("confluence", "content", "update", pid, "--snapshot-token", f"v:{version}", "--body-file", p, "--format", "html", "--ack-body-formats", "--version-message", msg, "-y")
    if '"ok": false' in r.stdout or r.returncode != 0: raise SystemExit(f"update failed {pid}: {(r.stdout+r.stderr)[-600:]}")

def version(pid):
    r = twg("confluence", "content", "get", pid); m = re.search(r"Version: v(\d+)", r.stdout); return int(m.group(1))

def upload(pid, path):
    tok = open(os.path.expanduser("~/.config/atlassian/token")).read().strip()
    r = subprocess.run(["curl", "-s", "-u", f"hoang.quach@aspirelifestyles.com:{tok}", "-X", "POST", "-H", "X-Atlassian-Token: nocheck",
                        f"{SITE}/wiki/rest/api/content/{pid}/child/attachment", "-F", f"file=@{path}", "-F", "minorEdit=true"], capture_output=True, text=True)
    try: d = json.loads(r.stdout); a = d["results"][0]
    except Exception:
        import time; time.sleep(5)
        r = subprocess.run(["curl", "-s", "-u", f"hoang.quach@aspirelifestyles.com:{tok}", "-X", "POST", "-H", "X-Atlassian-Token: nocheck",
                            f"{SITE}/wiki/rest/api/content/{pid}/child/attachment", "-F", f"file=@{path}", "-F", "minorEdit=true"], capture_output=True, text=True)
        d = json.loads(r.stdout or "{}")
        if "results" not in d:  # already uploaded by the first attempt: look it up by name
            name = os.path.basename(path)
            g = subprocess.run(["curl", "-s", "-u", f"hoang.quach@aspirelifestyles.com:{tok}", f"{SITE}/wiki/rest/api/content/{pid}/child/attachment?filename={name}&expand=extensions"], capture_output=True, text=True)
            d = json.loads(g.stdout)
        a = d["results"][0]
    return {"fileId": a["extensions"]["fileId"], "collection": f"contentId-{pid}", "title": a["title"]}

docs = load_docs()
for rel, d in docs.items():
    md, codes = extract_mermaid(d["md"]); d["html"] = to_html(md); d["codes"] = codes

INDEX_TITLE = "Per-feature documents (F01–F23)"
ORDER_TOP = ["00a-manager-summary.md"] + [f for f in sorted(docs) if re.match(r"\d\d-", f) and not f.startswith("00-")]

if sys.argv[1] == "pass1":
    # placeholders for diagrams; links left as-is for now
    for rel in ORDER_TOP:
        if rel in state["pages"]: continue
        body = re.sub(r"<p>MERMAIDPLACEHOLDER(\d+)</p>", r"<p><em>[diagram \1 — added in the next version]</em></p>", docs[rel]["html"])
        state["pages"][rel] = create(docs[rel]["title"], body, PARENT); save(); print("created", rel, state["pages"][rel])
    if "features/" not in state["pages"]:
        idx = "<p>One page per feature: how it works today, what CMS-only would mean, what CMS-master means, with diagrams, load arithmetic and pros/cons.</p>" \
              '<p><span data-type="inline-extension" data-extension-key="children" data-extension-type="com.atlassian.confluence.macro.core" data-parameters=\'{"macroParams":{"all":{"value":"true"},"depth":{"value":"1"}},"macroMetadata":{"schemaVersion":{"value":"2"},"title":"Child pages"}}\'>Child pages</span></p>'
        state["pages"]["features/"] = create(INDEX_TITLE, idx, PARENT); save(); print("created index", state["pages"]["features/"])
    for rel in sorted(f for f in docs if f.startswith("features/")):
        if rel in state["pages"]: continue
        body = re.sub(r"<p>MERMAIDPLACEHOLDER(\d+)</p>", r"<p><em>[diagram \1 — added in the next version]</em></p>", docs[rel]["html"])
        state["pages"][rel] = create(docs[rel]["title"], body, state["pages"]["features/"]); save(); print("created", rel, state["pages"][rel])
    state["pages"]["00-README.md"] = PARENT; save()

elif sys.argv[1] == "pass2":
    urls = {rel: f"{SITE}/wiki/spaces/AD/pages/{pid}" for rel, pid in state["pages"].items()}
    pngs = json.load(open(f"{OUT}/pngs.json"))
    for rel, d in docs.items():
        pid = state["pages"][rel]
        body = d["html"]
        for i, code in enumerate(d["codes"]):
            key = f"{rel}#{i}"
            if key not in state["media"]:
                state["media"][key] = upload(pid, f"{OUT}/png/{key.replace('/', '__').replace('#', '_')}.png"); save()
            body = body.replace(f"<p>MERMAIDPLACEHOLDER{i}</p>", figure(state["media"][key], code))
        body = link_rewriter(body, rel, urls)
        if rel == "00-README.md":
            body = ('<div data-type="panel-note"><p><strong>Status (21 Sep 2026):</strong> ticket <a href="https://internationalsos.atlassian.net/browse/ABE-5439">ABE-5439</a> — Awaiting Review. These pages replace the Markdown reader Lambda <code>cms-only-provider-audit-docs</code>; the source files live in the <code>ai-workspace</code> repo under <code>issues/cms-only-provider-audit/</code>.</p></div>'
                    + body.replace('<p><span data-type', '<p><span data-type'))
            body += '<h2>Pages</h2><p><span data-type="inline-extension" data-extension-key="children" data-extension-type="com.atlassian.confluence.macro.core" data-parameters=\'{"macroParams":{"all":{"value":"true"},"depth":{"value":"2"}},"macroMetadata":{"schemaVersion":{"value":"2"},"title":"Child pages"}}\'>Child pages</span></p>'
        v = version(pid)
        if v >= 2 and rel != "00-README.md": print("skip (done)", rel); continue
        update(pid, body, v, "Diagrams as images; links to sibling pages"); print("updated", rel, f"v{v}->v{v+1}")
    save()
