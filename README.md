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
| `issues/` | Task files, one per ticket (`ABE-xxxx.md`: brief → analysis → implementation → verification → release) plus runbooks. Work in progress lives here so anyone can pick it up | symlinked as `<workspace>/issues` |
| `confluence/` | Generators for the Confluence pages (Data Processors client pages, AI workflow series) | run when the pages change |
| `clone.sh` / `clone.ps1` | Clone the five product checkouts side by side on their working branches (`--bootstrap` / `-Bootstrap` chains the install) | — |
| `bootstrap.sh` / `doctor.sh` | Install into a fresh machine / verify the setup | — |

## Take over in 15 minutes

macOS / Linux / WSL. On native Windows, same steps in PowerShell — see [Windows](#windows) below.

```bash
# 1. Clone the kit, then let it clone the product repos side by side (folder names and branches matter)
mkdir -p ~/Projects/OmnicasaAS && cd ~/Projects/OmnicasaAS
git clone https://github.com/bulubuloa/AS.APAC.AI.Workflows.git ai-workspace
./ai-workspace/clone.sh   # ABMB, ABVB, ABF, ABCB (data-processer-pre-production), ABCB.Clone (develop); skips what exists
                          # (or `./ai-workspace/clone.sh --bootstrap` to do steps 1 and 2 in one go)

# 2. Install the kit (idempotent; backs up anything it replaces)
./ai-workspace/bootstrap.sh

# 3. Authenticate the things only you can authenticate
claude            # then /mcp → atlassian-isos → Authenticate (Jira/Confluence, your ISOS account)
twg               # first run opens the Atlassian OAuth login for the twg CLI
aws sso login     # or configure the ap-southeast-1 profile you were given
# open the DB tunnels you were given (ports in access/ACCESS.md)

# 4. Check
./ai-workspace/doctor.sh
```

Then, in any repo: `claude` → `/task-run ABE-xxxx` (pauses after fetch and after analysis), or step by step `/task-fetch` → `/task-analyse` → `/task-implement` → `/task-verify` → `/task-deliver`. Codex: `codex` → `/prompts:task-run ABE-xxxx`.

## Windows

Two ways, both supported:

- **WSL2 (recommended)** — install Ubuntu from the Store, clone the repos *inside* the WSL filesystem (`~/Projects/OmnicasaAS`, not `/mnt/c/...` — git and builds are far faster), install the tools with `apt`/`brew`-for-Linux, and run `./ai-workspace/bootstrap.sh` unchanged. Claude Code, Codex, twg, aws, dotnet, mysql-client, sqlcmd, Playwright and the SSH tunnels all work in WSL. Windows-only work (RoadSide `.NET Framework 4.8` builds in Visual Studio) stays on the Windows side.
- **Native PowerShell** — `clone.ps1` / `bootstrap.ps1` / `doctor.ps1` do the same as the shell scripts. Same four steps, in a PowerShell window (Windows PowerShell 5.1 or 7):

```powershell
# 0. Tools (once). sqlcmd: Microsoft installer; twg: its Windows installer (%LOCALAPPDATA%\Programs\twg\bin — add to PATH)
winget install Anthropic.ClaudeCode Amazon.AWSCLI Git.Git OpenJS.NodeJS Python.Python.3.12 Microsoft.DotNet.SDK.8 Oracle.MySQL

# 1. Clone the kit, then let it clone the product repos side by side (folder names and branches matter)
mkdir C:\Projects\OmnicasaAS; cd C:\Projects\OmnicasaAS
git clone https://github.com/bulubuloa/AS.APAC.AI.Workflows.git ai-workspace
powershell -ExecutionPolicy Bypass -File .\ai-workspace\clone.ps1      # add -Bootstrap to do steps 1 and 2 in one go

# 2. Install the kit (idempotent; backs up anything it replaces)
powershell -ExecutionPolicy Bypass -File .\ai-workspace\bootstrap.ps1

# 3. Authenticate the things only you can authenticate
claude            # then /mcp → atlassian-isos → Authenticate (Jira/Confluence, your ISOS account)
twg               # first run opens the Atlassian OAuth login; token from clipboard if asked:
                  #   Get-Clipboard | Set-Content -NoNewline $env:USERPROFILE\.config\atlassian\token
aws sso login     # or configure the ap-southeast-1 profile you were given
# DB tunnels: ssh -N -L 3375:... user@bastion in its own PowerShell window (ports in access\ACCESS.md)

# 4. Check
powershell -ExecutionPolicy Bypass -File .\ai-workspace\doctor.ps1
```

  Notes: `-ExecutionPolicy Bypass` only matters if scripts are blocked on your machine (`.\bootstrap.ps1` works otherwise). Memory and `issues/` become directory **junctions** (no admin rights needed); the project slug follows Claude Code's Windows rule (`C:\Projects\OmnicasaAS` → `C--Projects-OmnicasaAS`); the pre-commit guard runs under Git for Windows' bash + perl. Inside a `claude` session, run scripts with `! powershell -File ./bootstrap.ps1` — the `!` prefix is Git Bash, so `.\` backslashes don't work there.

Codex CLI on Windows is best run inside WSL; the PowerShell bootstrap still writes the `AGENTS.md`/prompts/config if `~\.codex` exists.

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
