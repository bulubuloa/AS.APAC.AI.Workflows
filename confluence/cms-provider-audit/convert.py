"""Markdown (audit docs) -> Confluence HTML. Two passes: pass1 creates pages (diagram placeholders), pass2 embeds PNGs + resolves links."""
import re, os, json, html, glob, markdown

SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "issues", "cms-only-provider-audit"))
OUT = os.path.dirname(os.path.abspath(__file__))
PARENT = "6838452246"

def load_docs():
    docs = {}
    for f in sorted(glob.glob(f"{SRC}/*.md") + glob.glob(f"{SRC}/features/*.md")):
        rel = os.path.relpath(f, SRC)
        text = open(f, encoding="utf-8").read()
        m = re.match(r"\s*#\s+(.+)", text)
        title = m.group(1).strip() if m else rel
        body = text[m.end():] if m else text
        docs[rel] = {"title": title, "md": body}
    return docs

def extract_mermaid(md):
    codes = []
    def rep(m):
        codes.append(m.group(1).strip()); return f"\n\nMERMAIDPLACEHOLDER{len(codes)-1}\n\n"
    md = re.sub(r"```mermaid\n(.*?)```", rep, md, flags=re.S)
    return md, codes

def to_html(md):
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    # blockquote "Quick view for managers" -> info panel (Confluence blockquotes cannot hold headings)
    h = h.replace("<blockquote>", '<div data-type="panel-info">').replace("</blockquote>", "</div>")
    # fenced code: <pre><code class="language-sql"> stays; plain <pre><code> fine. Strip markdown's 'codehilite' none.
    h = re.sub(r'<pre><code class="language-(\w+)">', lambda m: f'<pre><code class="language-{m.group(1)}">', h)
    # hr
    h = h.replace("<hr />", "<hr>").replace("<br />", "<br>")
    # headings: drop id attrs none; ensure <h4+> -> h3 (Confluence fine with h4 but keep hierarchy)
    return h

def link_rewriter(h, rel, urls):
    base = os.path.dirname(rel)
    def rep(m):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:")): return m.group(0)
        path, _, anchor = href.partition("#")
        if not path: return m.group(0).replace(f'href="{href}"', f'href="#{anchor}"')
        target = os.path.normpath(os.path.join(base, path))
        if target in urls: return m.group(0).replace(f'href="{href}"', f'href="{urls[target]}"')
        return m.group(0)
    return re.sub(r'<a href="([^"]+)"', rep, h)

def figure(media, code):
    fig = ('<figure data-type="media-single" data-layout="center" data-width="100" data-width-type="percentage">'
           f'<div data-type="media" data-media-type="file" data-id="{media["fileId"]}" data-collection="{media["collection"]}" data-alt="{media["title"]}"></div></figure>')
    return fig + '<details><summary>Diagram source (Mermaid)</summary><pre><code class="language-text">' + html.escape(code) + "</code></pre></details>"

if __name__ == "__main__":
    docs = load_docs()
    allcodes = {}
    for rel, d in docs.items():
        md, codes = extract_mermaid(d["md"])
        d["html"] = to_html(md); d["codes"] = codes
        for i, c in enumerate(codes): allcodes[f"{rel}#{i}"] = c
    json.dump({rel: {"title": d["title"]} for rel, d in docs.items()}, open(f"{OUT}/docs.json", "w"), indent=1)
    json.dump(allcodes, open(f"{OUT}/mermaid.json", "w"))
    os.makedirs(f"{OUT}/html", exist_ok=True)
    for rel, d in docs.items():
        open(f"{OUT}/html/{rel.replace('/', '__')}.html", "w", encoding="utf-8").write(d["html"])
    print(len(docs), "docs,", len(allcodes), "diagrams")
