# ai-workspace — the AI setup for the APAC Aspire Digital projects

Everything an AI coding agent (Claude Code) needs to work on the Benefit / RSA repositories
the way we work on them, in one versioned place, so that any developer can take over any of
the projects and the agent starts with the same knowledge, commands, permissions and access
recipes — not with an empty memory.

Nothing in this repository is a secret, but `issues/` and `memory/` contain internal business detail (client codes, counts, incident notes) — keep the repository private to the team. Credentials live in AWS Secrets Manager / SSM and in
each developer's own OAuth logins; this repo only says *where* they are.

## What is in here

| Path | What | Where it ends up on your machine |
|---|---|---|
| `claude/CLAUDE.md` | Global working preferences (comment style, commit format, no AI trailers) | `~/.claude/CLAUDE.md` |
| `claude/commands/*.md` | Slash commands for the whole loop: `/task-fetch` (Jira → task file), `/task-analyse` (read-only analysis), `/task-implement` (branch from the right base, code, build, tests, commits), `/task-verify` (evidence: browser, DB, logs), `/task-deliver` (PR text, QA comment, release notes, memory), `/task-run` (all of them, with pauses / `--cowork` / `--auto`) | `<workspace>/.claude/commands/` |
| `codex/` | The same for OpenAI Codex CLI: `config.snippet.toml` (MCP servers, sandbox), `prompts/` (`/prompts:task-*`), `AGENTS.preamble.md` (how Codex reads/writes the shared memory) | `~/.codex/`, `AGENTS.md` next to each `CLAUDE.md` |
| `claude/settings.json` | Permission allow/deny rules: reads silent, writes prompted | `<workspace>/.claude/settings.json` |
| `claude/mcp.json` | MCP servers as a project config file (`atlassian-isos` HTTP, `playwright` stdio) | `<workspace>/.mcp.json` and `<repo>/.mcp.json` (git-excluded) |
| `claude/mcp.sh` | The MCP servers to register (Atlassian, Playwright) | `claude mcp add …` (user scope) |
| `workspace/CLAUDE.md` | Workspace instructions: repo map, branch → environment, environments, access, conventions, where the docs are | `<workspace>/CLAUDE.md` |
| `workspace/repos/<REPO>/CLAUDE.md` | Per-repo instructions (ABCB, ABMB, ABF, ABVB) | `<workspace>/<repo dir>/CLAUDE.md` |
| `memory/<name>/*.md` | The agent's project memory — every non-obvious fact learned on these projects (env ids, drifted SPs, pipeline quirks, incidents) | symlinked into `~/.claude/projects/<slug>/memory` |
| `access/ACCESS.md` | Access recipes: which tunnel port is which database, which secret holds which connection string, AWS account, CMS environments, mail rules | read by the agent via `workspace/CLAUDE.md` |
| `access/tunnels.env`, `tunnel.sh` / `tunnel.ps1` | Bastion + RDS targets per local port (no secrets) and the `up`/`down`/`status` script; the PEM key is yours (`~/.ssh/ABE.pem` or `ABE_SSH_KEY`) | run when you need a database |
| `issues/` | Task files, one per ticket (`ABE-xxxx.md`: brief → analysis → implementation → verification → release) plus runbooks. Work in progress lives here so anyone can pick it up | symlinked as `<workspace>/issues` |
| `confluence/` | Generators for the Confluence pages (Data Processors client pages, AI workflow series) | run when the pages change |
| `tools.sh` / `tools.ps1` | Install the CLIs (brew/apt / winget, Claude Code, twg, python helpers; Windows: Zscaler CA bundle) | called by bootstrap |
| `clone.sh` / `clone.ps1` | Clone the five product checkouts side by side on their working branches | called by bootstrap |
| `bootstrap.sh` / `bootstrap.ps1` | One-shot setup: tools -> repos -> kit (global + workspace + per-repo instructions, commands, permissions, MCP, memory links) | — |
| `doctor.sh` / `doctor.ps1` | Verify the setup, one line per check | — |

## Take over in 15 minutes

Three steps on every platform: clone the kit, run its bootstrap, do the three logins only you can do.

**macOS / Linux / WSL**

```bash
# 1. Clone the kit into a fresh workspace folder (the product repos land next to it)
mkdir -p ~/Projects/AspireDigital && cd ~/Projects/AspireDigital
git clone https://github.com/bulubuloa/AS.APAC.AI.Workflows.git ai-workspace

# 2. Bootstrap: tools (brew/apt, Claude Code, twg), the five product repos on their working branches, the kit itself
./ai-workspace/bootstrap.sh        # idempotent - re-run any time; NO_TOOLS=1 / NO_CLONE=1 skip those parts

# 3. Log in (browser opens each time), then check
claude                             # /mcp -> atlassian-isos -> Authenticate  (Jira/Confluence, your ISOS account)
twg login                          # only if the twg installer did not already log you in
aws login --region ap-southeast-1  # console sign-in; session expires, re-run when needed (no browser: aws configure + access key)
./ai-workspace/doctor.sh
```

**Windows (native PowerShell 5.1 / 7)** — same three steps. Say *Yes* to the UAC prompts winget raises for machine-wide installers.

```powershell
mkdir C:\Projects\AspireDigital; cd C:\Projects\AspireDigital
git clone https://github.com/bulubuloa/AS.APAC.AI.Workflows.git ai-workspace     # no git yet? winget install Git.Git, open a new window

powershell -ExecutionPolicy Bypass -File .\ai-workspace\bootstrap.ps1   # tools via winget + twg installer, Zscaler CA bundle, repos, kit; -NoTools / -NoClone

# NEW PowerShell window (PATH), then:
claude                             # /mcp -> atlassian-isos -> Authenticate
twg login
aws login --region ap-southeast-1
powershell -ExecutionPolicy Bypass -File .\ai-workspace\doctor.ps1
```

DB tunnels: `./ai-workspace/access/tunnel.sh up` (Windows: `access\tunnel.ps1 up`) opens 3375/3382/3383 through the bastion. Hosts and ports are committed in `access/tunnels.env`; the only secret is the bastion key `ABE.pem` — get it from the team out of band, put it at `~/.ssh/ABE.pem` (`chmod 400`) or point `ABE_SSH_KEY` at it. `*.pem` is git-ignored here and the pre-commit guard rejects private keys.

Then, in any repo: `claude` → `/task-run ABE-xxxx` (pauses after fetch and after analysis), or step by step `/task-fetch` → `/task-analyse` → `/task-implement` → `/task-verify` → `/task-deliver`. Codex: `codex` → `/prompts:task-run ABE-xxxx`.

## New device (yours or a teammate's)

1. Clone the kit and run the bootstrap (above) — `access/tunnels.env` and `access/tunnel.sh` come with it.
2. Put the bastion key at `~/.ssh/ABE.pem` (`chmod 400`). It is the only thing git does not carry: copy it from your
   other machine (AirDrop / `scp` / password-manager attachment) — never through chat, email or a ticket attachment.
   Key kept elsewhere? `ABE_SSH_KEY=/path` in your shell profile or in `access/tunnels.local.env` (git-ignored).
3. The bastion security group (`sg-006ea52049f6aee44`) allows port 22 only from known IPs; on a new network
   `tunnel.sh up` fails and prints your public IP — send it to whoever manages the SG.
4. `./ai-workspace/access/tunnel.sh up` then `./ai-workspace/doctor.sh`.

## Windows notes

- **WSL2 is also fine** — install Ubuntu from the Store, keep the workspace *inside* the WSL filesystem (`~/Projects/AspireDigital`, not `/mnt/c/...` — git and builds are far faster) and use the macOS/Linux steps unchanged. Windows-only work (RoadSide `.NET Framework 4.8` builds in Visual Studio) stays on the Windows side.
- **Corporate TLS (Zscaler)** — python/node-based CLIs (aws, pip, npx) reject the proxy's certificate out of the box (`CERTIFICATE_VERIFY_FAILED`). `tools.ps1` detects the Zscaler root in the Windows store, writes `~\.aws\ca-bundle.pem` (public CAs + Zscaler) and sets `AWS_CA_BUNDLE`, `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS` for your user. Open a new window afterwards.
- `-ExecutionPolicy Bypass` only matters if scripts are blocked on your machine (`.\bootstrap.ps1` works otherwise). Memory and `issues/` become directory **junctions** (no admin rights needed); the project slug follows Claude Code's Windows rule (`C:\Projects\AspireDigital` → `C--Projects-AspireDigital`); the pre-commit guard runs under Git for Windows' bash + perl. Inside a `claude` session, run scripts with `! powershell -File ./bootstrap.ps1` — the `!` prefix is Git Bash, so `.\` backslashes don't work there.
- Codex CLI on Windows is best run inside WSL; the PowerShell bootstrap still writes the `AGENTS.md`/prompts/config if `~\.codex` exists.

## Codex CLI instead of Claude Code

`bootstrap.sh` installs the Codex equivalents when `~/.codex` exists (or `WITH_CODEX=1`): `~/.codex/AGENTS.md` (global preferences), an `AGENTS.md` in the workspace and in each repo (workspace map + the Codex memory preamble + the repo instructions, because Codex reads `AGENTS.md` from the git root, not from parent folders), the six prompts in `~/.codex/prompts/`, and the MCP servers + trusted project in `~/.codex/config.toml`. Then `codex mcp login atlassian-isos`. Codex has no automatic project memory, so its `AGENTS.md` tells it to read `ai-workspace/memory/*/MEMORY.md` at the start of a session and to write notes at the end — the notes are the same files either agent uses. Permissions are coarser than Claude's allow-list: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`, network on.

## Keeping it current — the one rule

**When a session learns something non-obvious, it goes into `memory/` and gets committed.**
The agent does this itself at the end of a ticket (the workspace `CLAUDE.md` tells it to); the
human reviews the diff like any other. Facts that turn out wrong get corrected or deleted, never
left to mislead the next person. Secrets never go in — the pre-commit check refuses them.

Layout of a memory note (the agent's own format):

```markdown
---
name: kebab-case-slug
description: one line used for recall
metadata: { type: reference | project | feedback }
---
The fact. **Why:** … **How to apply:** … Links: [[other-note]]
```

## Related documentation

- Confluence → Aspire Digital → *AI in the Development Workflow* (how we work with the agent, two worked examples)
- Confluence → Aspire Digital → *Benefit Data Processors* (one page per client, generated from `confluence/data-processors/`)
