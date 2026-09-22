#!/usr/bin/env bash
# Installs the ai-workspace kit into this machine's Claude Code setup. Idempotent; backs up what it replaces.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${WORKSPACE:-$(dirname "$KIT")}"          # the folder that holds the ABMB/ABVB/ABF/ABCB repos
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
STAMP="$(date +%Y%m%d%H%M%S)"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarn\033[0m %s\n' "$*"; }
backup() { [ -e "$1" ] && [ ! -L "$1" ] && ! cmp -s "$1" "${2:-/dev/null}" && cp -a "$1" "$1.bak-$STAMP" && warn "backed up $1 → $1.bak-$STAMP" || true; }  # $2 = incoming file: no backup when identical

# Claude Code keys project memory by the absolute path of the folder, with '/' replaced by '-'.
slug() { printf '%s' "$1" | sed 's/[^A-Za-z0-9]/-/g'; }  # Claude Code turns every non-alphanumeric character of the path into '-'

say "workspace: $WS"
[ -d "$WS" ] || { echo "workspace folder not found: $WS (set WORKSPACE=…)"; exit 1; }

# 1. Global preferences
mkdir -p "$CLAUDE_HOME"
backup "$CLAUDE_HOME/CLAUDE.md" "$KIT/claude/CLAUDE.md"; cp "$KIT/claude/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"; say "installed ~/.claude/CLAUDE.md"

# 2. Workspace-level instructions, commands and permissions
mkdir -p "$WS/.claude/commands"
# task files live in the kit (issues/) so work in progress can be picked up by anyone; the workspace gets a symlink
if [ -d "$WS/issues" ] && [ ! -L "$WS/issues" ]; then for f in "$WS/issues"/*; do [ -e "$KIT/issues/$(basename "$f")" ] || cp -R "$f" "$KIT/issues/"; done; mv "$WS/issues" "$WS/issues.bak-$STAMP"; warn "moved existing issues/ into the kit"; fi
[ -L "$WS/issues" ] || ln -s "$KIT/issues" "$WS/issues"
backup "$WS/CLAUDE.md" "$KIT/workspace/CLAUDE.md"; cp "$KIT/workspace/CLAUDE.md" "$WS/CLAUDE.md"
for c in "$KIT"/claude/commands/*.md; do cp "$c" "$WS/.claude/commands/"; done
backup "$WS/.claude/settings.json" "$KIT/claude/settings.json"; cp "$KIT/claude/settings.json" "$WS/.claude/settings.json"
backup "$WS/.mcp.json" "$KIT/claude/mcp.json"; cp "$KIT/claude/mcp.json" "$WS/.mcp.json"
say "installed workspace CLAUDE.md, $(ls "$KIT"/claude/commands | wc -l | tr -d ' ') commands, settings.json, .mcp.json"

# 3. Per-repo instructions (only for repos that are checked out)
for r in "$KIT"/workspace/repos/*/; do
  name="$(basename "$r")"
  for dir in "$WS/$name" "$WS/$name.Clone"; do
    if [ -d "$dir" ]; then
      backup "$dir/CLAUDE.md" "$r/CLAUDE.md"; cp "$r/CLAUDE.md" "$dir/CLAUDE.md"; say "installed $dir/CLAUDE.md"
      backup "$dir/.mcp.json" "$KIT/claude/mcp.json"; cp "$KIT/claude/mcp.json" "$dir/.mcp.json"
      # keep the instruction files out of the product repos' commits without touching their .gitignore
      if [ -d "$dir/.git" ]; then mkdir -p "$dir/.git/info"; for f in CLAUDE.md AGENTS.md .mcp.json "*.bak-*"; do grep -qx "$f" "$dir/.git/info/exclude" 2>/dev/null || echo "$f" >> "$dir/.git/info/exclude"; done; fi
    fi
  done
done

# 4. Memory: link each project's memory dir to the kit so notes are versioned and shared
link_memory() { # $1 = folder the agent runs in, $2 = kit memory name
  local proj="$CLAUDE_HOME/projects/$(slug "$1")" target="$KIT/memory/$2"
  mkdir -p "$proj"
  if [ -d "$proj/memory" ] && [ ! -L "$proj/memory" ]; then
    # merge any local-only notes into the kit before replacing the dir
    for f in "$proj/memory"/*.md; do [ -e "$f" ] || continue; [ -e "$target/$(basename "$f")" ] || { cp "$f" "$target/"; warn "kept local note $(basename "$f") in kit memory/$2"; }; done
    mv "$proj/memory" "$proj/memory.bak-$STAMP"
  fi
  [ -L "$proj/memory" ] && rm "$proj/memory"
  ln -s "$target" "$proj/memory"; say "memory: $1 → memory/$2"
}
link_memory "$WS" AspireDigital
[ -d "$WS/ABCB" ]       && link_memory "$WS/ABCB" ABCB
[ -d "$WS/ABCB.Clone" ] && link_memory "$WS/ABCB.Clone" ABCB
[ -d "$WS/ABMB" ]       && link_memory "$WS/ABMB" ABMB

# 5. MCP servers (user scope; harmless if already present)
if command -v claude >/dev/null; then bash "$KIT/claude/mcp.sh"; else warn "claude CLI not found — install Claude Code, then run claude/mcp.sh"; fi

# 5b. Codex CLI (OpenAI) — same content, its file names: AGENTS.md, ~/.codex/prompts, config.toml
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
if [ -d "$CODEX_HOME" ] || [ "${WITH_CODEX:-0}" = "1" ]; then
  # the ChatGPT desktop app bundles the codex CLI but does not put it on PATH; a short name keeps commands on one line
  if ! command -v codex >/dev/null && [ -x "/Applications/ChatGPT.app/Contents/Resources/codex" ]; then mkdir -p "$HOME/.local/bin"; ln -sf /Applications/ChatGPT.app/Contents/Resources/codex "$HOME/.local/bin/codex"; say "codex: linked ~/.local/bin/codex"; fi
  mkdir -p "$CODEX_HOME/prompts"
  backup "$CODEX_HOME/AGENTS.md"; sed 's/Co-Authored-By: Claude/Co-Authored-By: Codex/' "$KIT/claude/CLAUDE.md" > "$CODEX_HOME/AGENTS.md"
  for c in "$KIT"/codex/prompts/*.md; do cp "$c" "$CODEX_HOME/prompts/"; done
  # Codex reads AGENTS.md from the git root down to cwd; the workspace folder is not a repo, so each repo's
  # AGENTS.md carries the workspace map + the Codex memory preamble + the repo's own instructions.
  backup "$WS/AGENTS.md"; cat "$KIT/codex/AGENTS.preamble.md" "$KIT/workspace/CLAUDE.md" > "$WS/AGENTS.md"
  for r in "$KIT"/workspace/repos/*/; do
    name="$(basename "$r")"
    for dir in "$WS/$name" "$WS/$name.Clone"; do
      [ -d "$dir" ] || continue
      backup "$dir/AGENTS.md"; { cat "$KIT/codex/AGENTS.preamble.md"; echo "# Workspace map (from ai-workspace/workspace/CLAUDE.md)"; echo; cat "$KIT/workspace/CLAUDE.md"; echo; echo "---"; echo; cat "$r/CLAUDE.md"; } > "$dir/AGENTS.md"
    done
  done
  # config.toml: append the snippet sections that are not there yet; trust the workspace project
  cfg="$CODEX_HOME/config.toml"; touch "$cfg"; backup "$cfg"
  grep -q '\[mcp_servers.atlassian-isos\]' "$cfg" || printf '\n[mcp_servers.atlassian-isos]\nurl = "https://mcp.atlassian.com/v1/mcp"\n' >> "$cfg"
  grep -q '\[mcp_servers.playwright\]' "$cfg" || printf '\n[mcp_servers.playwright]\ntype = "stdio"\ncommand = "npx"\nargs = ["-y", "@playwright/mcp@latest"]\n' >> "$cfg"
  grep -q "\[projects.\"$WS\"\]" "$cfg" || printf '\n[projects."%s"]\ntrust_level = "trusted"\n' "$WS" >> "$cfg"
  say "codex: AGENTS.md (global, workspace, repos), 2 prompts, MCP servers in config.toml — run: codex mcp login atlassian-isos"
fi

# 6. Secret guard for this repo
if [ -d "$KIT/.git" ]; then
  printf '#!/usr/bin/env bash\ngit diff --cached -U0 -- . ":(exclude)claude/secret-guard.pl" | perl "$(git rev-parse --show-toplevel)/claude/secret-guard.pl" || { echo "pre-commit: staged diff looks like it contains a credential — point at the secret name instead"; exit 1; }\n' > "$KIT/.git/hooks/pre-commit"
  chmod +x "$KIT/.git/hooks/pre-commit"; say "installed secret guard (pre-commit)"
fi

say "done. Next: claude → /mcp (authenticate atlassian-isos); twg (OAuth); aws login --region ap-southeast-1; open tunnels (access/ACCESS.md); then ./doctor.sh"
