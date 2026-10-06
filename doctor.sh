#!/usr/bin/env bash
# Verifies the setup the agent depends on. Read-only. Prints one line per check.
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; WS="${WORKSPACE:-$(dirname "$KIT")}"
ok(){ printf '  \033[32mOK  \033[0m %s\n' "$*"; } ; bad(){ printf '  \033[31mMISS\033[0m %s\n' "$*"; }
have(){ command -v "$1" >/dev/null 2>&1; }

echo "tools"
for t in claude twg aws git dotnet node python3 sqlcmd; do have "$t" && ok "$t ($($t --version 2>/dev/null | head -1 | cut -c1-40))" || bad "$t not on PATH"; done
have mysql || [ -x /opt/homebrew/opt/mysql-client/bin/mysql ] && ok "mysql client" || bad "mysql client (brew install mysql-client)"
python3 -c "import pymysql" 2>/dev/null && ok "python pymysql" || bad "python pymysql (pip3 install pymysql)"

echo "repos"
for r in ABMB ABVB ABF ABCB ABCB.Clone ABMR; do d="$WS/$r"; [ -d "$d/.git" ] && ok "$r ($(git -C "$d" branch --show-current))" || bad "$r missing at $d"; done

echo "claude config"
[ -f "$HOME/.claude/CLAUDE.md" ] && ok "~/.claude/CLAUDE.md" || bad "~/.claude/CLAUDE.md"
[ -f "$WS/CLAUDE.md" ] && ok "workspace CLAUDE.md" || bad "workspace CLAUDE.md"
[ -f "$WS/.claude/commands/task-fetch.md" ] && ok "/task-fetch" || bad "/task-fetch command"
[ -f "$WS/.claude/commands/task-analyse.md" ] && ok "/task-analyse" || bad "/task-analyse command"
for p in "$WS" "$WS/ABCB" "$WS/ABMB" "$WS/ABMR"; do s="$HOME/.claude/projects/$(printf '%s' "$p" | sed 's/[^A-Za-z0-9]/-/g')/memory"; [ -L "$s" ] && ok "memory linked: $(basename "$p") → $(readlink "$s" | sed "s#$KIT/##")" || bad "memory not linked for $p"; done
have claude && { claude mcp list 2>/dev/null | grep -q "atlassian-isos" && ok "MCP atlassian-isos registered (authenticate with /mcp inside claude)" || bad "MCP atlassian-isos (run claude/mcp.sh)"; claude mcp list 2>/dev/null | grep -q playwright && ok "MCP playwright" || bad "MCP playwright"; }

echo "codex (optional)"
CODEX_WIN_BIN="${LOCALAPPDATA:+$(cygpath -u "$LOCALAPPDATA" 2>/dev/null)/OpenAI/Codex/bin}"
if [ -d "$HOME/.codex" ] || command -v codex >/dev/null || { [ -n "$CODEX_WIN_BIN" ] && [ -d "$CODEX_WIN_BIN" ]; }; then
  command -v codex >/dev/null && ok "codex on PATH" || bad "codex not on PATH (Codex app installed?) - re-run bootstrap.sh to add the ~/.local/bin launcher"
  if command -v codex >/dev/null; then codex mcp list 2>/dev/null | grep -q atlassian-isos && ok "codex sees MCP atlassian-isos (login: codex mcp login atlassian-isos)" || bad "codex mcp list has no atlassian-isos - re-run bootstrap.sh"; fi
  for r in ABMB ABVB ABF ABCB ABCB.Clone ABMR; do [ -d "$WS/$r" ] || continue; p="$( { command -v cygpath >/dev/null && cygpath -w "$WS/$r"; } || echo "$WS/$r")"
    [ -f "$WS/$r/.codex/config.toml" ] && grep -qF "$p'" "$HOME/.codex/config.toml" 2>/dev/null && ok "codex repo MCP: $r/.codex/config.toml (trusted)" || bad "codex repo MCP: $r/.codex/config.toml or its trust entry missing - re-run bootstrap.sh"; done
  [ -f "$HOME/.codex/AGENTS.md" ] && ok "~/.codex/AGENTS.md" || bad "~/.codex/AGENTS.md"
  [ -f "$WS/AGENTS.md" ] && ok "workspace AGENTS.md" || bad "workspace AGENTS.md"
  [ -f "$HOME/.codex/prompts/task-fetch.md" ] && ok "/prompts:task-fetch" || bad "codex prompt task-fetch"
  [ -f "$HOME/.agents/skills/task-fetch/SKILL.md" ] && ok "skill \$task-fetch" || bad "codex skill task-fetch (~/.agents/skills) - re-run bootstrap.sh"
  grep -q 'mcp_servers.atlassian-isos' "$HOME/.codex/config.toml" 2>/dev/null && ok "codex MCP atlassian-isos in config.toml (login: codex mcp login atlassian-isos)" || bad "codex MCP atlassian-isos"
else ok "codex not installed — skipped"; fi
echo "access"
aws sts get-caller-identity --query Account --output text 2>/dev/null | grep -q 739075353953 && ok "AWS account 739075353953" || bad "AWS credentials (aws login --region ap-southeast-1, or aws configure with an access key) — expected account 739075353953"
aws secretsmanager describe-secret --secret-id benefit-connection-string-preprod >/dev/null 2>&1 && ok "can read secret benefit-connection-string-preprod" || bad "secret benefit-connection-string-preprod not readable"
key="${ABE_SSH_KEY:-$HOME/.ssh/ABE.pem}"; [ -r "$key" ] && ok "bastion key $key" || { [ -r "$WS/ABE.pem" ] && ok "bastion key $WS/ABE.pem (move it to ~/.ssh/ABE.pem)" || bad "bastion key: ~/.ssh/ABE.pem or ABE_SSH_KEY (ask the team for ABE.pem — never via git/chat)"; }
for port in 3375:"Benefit SIT/UAT MySQL (benefit-sit cluster)" 3382:"Benefit PROD MySQL (read-only use)" 3383:"RSA PROD MSSQL"; do p="${port%%:*}"; (lsof -nP -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1) && ok "tunnel $p ${port#*:}" || bad "tunnel $p ${port#*:} not listening (access/tunnel.sh up $p)"; done
have twg && { twg confluence space get AD >/dev/null 2>&1 && ok "twg Confluence (AD space)" || bad "twg not authenticated (run: twg confluence space get AD)"; }
echo "done"
