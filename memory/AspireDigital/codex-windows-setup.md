---
name: codex-windows-setup
description: Codex on Windows - codex.exe not on PATH, [projects] trust must use C:\ paths, repo .codex/config.toml only loads when trusted, prompts became skills
metadata:
  type: reference
---

Codex desktop app (0.160, Oct 2026) on Windows, as handled by ai-workspace bootstrap:
- `codex.exe` lives in `%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\` (hash changes per update) — bootstrap adds a `~/.local/bin/codex(.cmd)` launcher.
- `[projects.'C:\Projects\AspireDigital\ABMB'] trust_level="trusted"` must use the Windows path; a Git-Bash `/c/...` key never matches (bug fixed 6 Oct 2026, commit 5439dbb).
- A repo's `.codex/config.toml` (Codex's `.mcp.json`) is loaded only for a trusted repo; `codex mcp list` does not show it — check with `codex doctor` ("MCP servers N").
- `type = "stdio"` in `[mcp_servers.*]` is ignored with a warning; `command` implies stdio, `url` implies HTTP.
- Custom prompts → skills: `~/.agents/skills/<name>/SKILL.md` (frontmatter name + description), invoked `$task-fetch`.

**How to apply:** when Codex "doesn't see" MCP or commands, run `doctor.sh`/`codex doctor` before editing config. Related: [[isos-confluence-write-via-twg]].
