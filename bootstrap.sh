#!/usr/bin/env bash
# Installs the ai-workspace kit into this machine's Claude Code setup. Idempotent; backs up what it replaces.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${WORKSPACE:-$(dirname "$KIT")}"          # the folder that holds the Omnicasa.Mobile.* repos
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
STAMP="$(date +%Y%m%d%H%M%S)"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarn\033[0m %s\n' "$*"; }
backup() { [ -e "$1" ] && [ ! -L "$1" ] && cp -a "$1" "$1.bak-$STAMP" && warn "backed up $1 → $1.bak-$STAMP" || true; }

# Claude Code keys project memory by the absolute path of the folder, with '/' replaced by '-'.
slug() { printf '%s' "$1" | sed 's#/#-#g'; }

say "workspace: $WS"
[ -d "$WS" ] || { echo "workspace folder not found: $WS (set WORKSPACE=…)"; exit 1; }

# 1. Global preferences
mkdir -p "$CLAUDE_HOME"
backup "$CLAUDE_HOME/CLAUDE.md"; cp "$KIT/claude/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"; say "installed ~/.claude/CLAUDE.md"

# 2. Workspace-level instructions, commands and permissions
mkdir -p "$WS/.claude/commands" "$WS/issues"
backup "$WS/CLAUDE.md"; cp "$KIT/workspace/CLAUDE.md" "$WS/CLAUDE.md"
for c in "$KIT"/claude/commands/*.md; do cp "$c" "$WS/.claude/commands/"; done
backup "$WS/.claude/settings.json"; cp "$KIT/claude/settings.json" "$WS/.claude/settings.json"
say "installed workspace CLAUDE.md, $(ls "$KIT"/claude/commands | wc -l | tr -d ' ') commands, settings.json"

# 3. Per-repo instructions (only for repos that are checked out)
for r in "$KIT"/workspace/repos/*/; do
  name="$(basename "$r")"
  for dir in "$WS/Omnicasa.Mobile.$name" "$WS/Omnicasa.Mobile.$name.Clone"; do
    if [ -d "$dir" ]; then backup "$dir/CLAUDE.md"; cp "$r/CLAUDE.md" "$dir/CLAUDE.md"; say "installed $dir/CLAUDE.md"; fi
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
link_memory "$WS" OmnicasaAS
[ -d "$WS/Omnicasa.Mobile.ABCB" ]       && link_memory "$WS/Omnicasa.Mobile.ABCB" ABCB
[ -d "$WS/Omnicasa.Mobile.ABCB.Clone" ] && link_memory "$WS/Omnicasa.Mobile.ABCB.Clone" ABCB
[ -d "$WS/Omnicasa.Mobile.ABMB" ]       && link_memory "$WS/Omnicasa.Mobile.ABMB" ABMB

# 5. MCP servers (user scope; harmless if already present)
if command -v claude >/dev/null; then bash "$KIT/claude/mcp.sh"; else warn "claude CLI not found — install Claude Code, then run claude/mcp.sh"; fi

# 6. Secret guard for this repo
if [ -d "$KIT/.git" ]; then
  cat > "$KIT/.git/hooks/pre-commit" <<'EOF'
#!/usr/bin/env bash
# refuse commits that look like they contain credentials
if git diff --cached -U0 | grep -E '^\+' | grep -vE '^\+\+\+' | grep -qE 'ATATT3|AKIA[0-9A-Z]{12}|eyJ[A-Za-z0-9_-]{30,}|(-p|pwd=|password[=: ]+)[A-Za-z0-9@#$%^&*_+=/.!-]{8,}'; then
  echo "pre-commit: something in the staged diff looks like a credential. Point at the secret's name instead."; exit 1; fi
EOF
  chmod +x "$KIT/.git/hooks/pre-commit"; say "installed secret guard (pre-commit)"
fi

say "done. Next: claude → /mcp (authenticate atlassian-isos); twg (OAuth); aws sso login; open tunnels (access/ACCESS.md); then ./doctor.sh"
