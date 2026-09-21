# Confluence pages for the Benefit Data Processors

Source of the pages under Confluence folder **APAC Aspire Benefit Data Processors** (AD space, folder id 6837698656).
Overview page 6837534805; one child page per client (ids in `page_ids.json`).

- `clients.py` — the facts per client (pipeline per env, input format, program mapping, gotchas, open items). Edit this.
- `gen.py` — renders `pages/00-overview.html` + `pages/<CODE>.html` in the Confluence HTML format.
- Publish/update with the twg CLI (the Atlassian MCP cannot write on our tenant):

```bash
python3 gen.py
# update an existing page (snapshot token = "v:<current version>")
twg confluence content update <page-id> --snapshot-token "v:N" --body-file pages/KPI.html --format html --ack-body-formats -y
# new client: create under the overview
twg confluence content create --space-id 64782337 --parent-id 6837534805 --content-type page --title "XYZ — Client name" --body-file pages/XYZ.html --format html --ack-body-formats --content-width wide -y
```

Re-verify the AWS facts (job-definition revisions, rule states, image tags) before republishing — they drift with every deploy.

## Diagrams

Diagrams are **PNG attachments** rendered from Mermaid source (the Mermaid Chart / draw.io / PlantUML apps only render
macros created in their own editor, so API-written macros stay empty). Each page shows the image plus the Mermaid source
in an expand. To change a diagram:

1. Edit the Mermaid code in `gen.py` (`FLOW[...]` or the overview diagram).
2. Regenerate `mrender.html` from the codes and render: `python3 -m http.server 8765`, open `http://127.0.0.1:8765/mrender.html`
   (Playwright is fine), wait for title `done`, save `JSON.stringify(window.__result)` as `pngs.json`.
3. Upload the PNGs as attachments with the Confluence REST API (`POST /wiki/rest/api/content/<pageId>/child/attachment`,
   header `X-Atlassian-Token: nocheck`, basic auth email + API token from `~/.config/atlassian/token`), and put the
   returned `extensions.fileId` into `media_ids.json` (collection = `contentId-<pageId>`).
4. `python3 gen.py`, then `twg confluence content update …` per page.
