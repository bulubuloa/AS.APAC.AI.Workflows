# CMS-only provider audit → Confluence

Source: `issues/cms-only-provider-audit/*.md` (34 documents, 73 Mermaid diagrams). Published 21 Sep 2026 under
**Roadside use vendor from CMS** (page 6838452246): README = parent body, 00a + 01–10 as children,
F01–F23 under "Per-feature documents". Page ids and attachment media ids: `state.json`.

To republish after editing a Markdown file: `python3 convert.py` (regenerates HTML), render the diagrams with
the Playwright recipe in `../data-processors/README.md` into `pngs.json` + `png/`, then `python3 publish.py pass2`
(idempotent: re-uses attachments already in `state.json`, updates only pages still at v1 — drop the version
guard for a full refresh).
