#!/usr/bin/env bash
# Registers the MCP servers the workflow uses, at user scope. Safe to re-run.
set -e
add() { local name="$1"; shift; if claude mcp get "$name" >/dev/null 2>&1; then echo "mcp: $name already registered"; else claude mcp add "$@" && echo "mcp: registered $name"; fi; }
# Jira + Confluence (ISOS tenant). Named after the site so other Atlassian tenants can coexist as separate servers.
add atlassian-isos --transport http -s user atlassian-isos https://mcp.atlassian.com/v1/mcp
# Real browser for verification / reproduction on SIT/UAT
add playwright -s user playwright -- npx -y @playwright/mcp@latest
echo "now: claude -> /mcp -> atlassian-isos -> Authenticate (approve for the internationalsos site)"
