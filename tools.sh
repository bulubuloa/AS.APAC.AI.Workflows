#!/usr/bin/env bash
# Installs the CLIs the workflow needs on macOS (Homebrew) / Linux+WSL (apt + brew-for-Linux if present). Idempotent;
# called by bootstrap.sh (skip with NO_TOOLS=1).
set -uo pipefail
say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarn\033[0m %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

# 1. Package manager: command to test | brew formula | apt package
if have brew; then
  for spec in git:git node:node aws:awscli python3:python@3.12 mysql:mysql-client sqlcmd:sqlcmd dotnet:dotnet-sdk; do
    cmd="${spec%%:*}"; pkg="${spec#*:}"
    if have "$cmd"; then say "$cmd present"; continue; fi
    say "brew install $pkg"; brew install "$pkg" >/dev/null 2>&1 || warn "brew install $pkg failed - install it by hand"
  done
  have mysql || { [ -x /opt/homebrew/opt/mysql-client/bin/mysql ] && warn 'mysql is keg-only: add /opt/homebrew/opt/mysql-client/bin to PATH'; }
elif have apt-get; then
  say 'apt install git nodejs npm awscli python3 python3-pip mysql-client'
  sudo apt-get install -y -qq git nodejs npm awscli python3 python3-pip mysql-client >/dev/null || warn 'apt install failed - install the tools by hand'
  have dotnet || warn '.NET SDK 8: https://learn.microsoft.com/dotnet/core/install/linux'
  have sqlcmd || warn 'sqlcmd: https://learn.microsoft.com/sql/tools/sqlcmd/sqlcmd-utility#download-and-install-sqlcmd'
else
  warn 'no brew/apt found - install git, node, awscli, python3, mysql-client, sqlcmd, dotnet by hand'
fi

# 2. Claude Code
have claude || { say 'npm install -g @anthropic-ai/claude-code'; npm install -g @anthropic-ai/claude-code >/dev/null 2>&1 || warn 'Claude Code install failed: npm install -g @anthropic-ai/claude-code'; }

# 3. twg (Atlassian Teamwork Graph CLI) - official installer, ~/.local/bin/twg; opens the OAuth login itself
if have twg || [ -x "$HOME/.local/bin/twg" ]; then say 'twg present'; else
  say 'installing twg'; curl -fsSL --retry 2 https://teamwork-graph.atlassian.com/cli/install | bash || warn 'twg install failed - https://developer.atlassian.com/cloud/twg-cli/getting-started/installation/'
fi

# 4. Python helpers the agent uses for DB / PGP work
pipi() { python3 -m pip install --quiet --disable-pip-version-check --user "$@" 2>/dev/null || python3 -m pip install --quiet --disable-pip-version-check --break-system-packages "$@" 2>/dev/null; }
if have python3; then
  pipi pymysql boto3 && say 'python: pymysql boto3' || warn 'pip install pymysql boto3 failed'
  pipi pgpy && say 'python: pgpy' || warn 'python: pgpy not installed - only needed for the PGP test-drop tool'   # source-only on PyPI; corporate proxies may block it
fi

# 5. AWS region default
have aws && aws configure set region ap-southeast-1
exit 0
