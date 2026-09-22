#!/usr/bin/env bash
# DB tunnels through the bastion. Targets come from tunnels.env (committed, hosts only); the PEM key is yours:
# ABE_SSH_KEY or ~/.ssh/ABE.pem. Usage: access/tunnel.sh up|down|status [3375 3382 3383]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/tunnels.env"
[ -f "$HERE/tunnels.local.env" ] && . "$HERE/tunnels.local.env"
KEY="${ABE_SSH_KEY:-$HOME/.ssh/ABE.pem}"
# older setups kept the key in the workspace folder — works, but move it to ~/.ssh (one `git add .` away from a leak)
[ -r "$KEY" ] || { alt="$(dirname "$(dirname "$HERE")")/ABE.pem"; [ -r "$alt" ] && { KEY="$alt"; echo "warn: using $alt — move it to ~/.ssh/ABE.pem (chmod 400)"; }; }

cmd="${1:-status}"; shift || true
ports=("$@"); [ ${#ports[@]} -gt 0 ] || ports=(3375 3382 3383)
listening() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }

for p in "${ports[@]}"; do
  var="TUNNEL_$p"; target="${!var:-}"
  [ -n "$target" ] || { echo "no $var in tunnels.env"; exit 1; }
  case "$cmd" in
    up)
      if listening "$p"; then echo "  up   $p → $target (already)"; continue; fi
      [ -r "$KEY" ] || { echo "PEM key not found: $KEY — set ABE_SSH_KEY or copy the key to ~/.ssh/ABE.pem (chmod 400)"; exit 1; }
      if ssh -i "$KEY" -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ConnectTimeout=10 \
             -L "$p:$target" "$BASTION_USER@$BASTION_HOST" -N -f; then echo "  up   $p → $target"
      else echo "  FAIL $p — the bastion security group must allow your public IP ($(curl -s --max-time 5 ifconfig.me || echo '?')) on port 22"; exit 1; fi ;;
    down)   pkill -f -- "-L $p:$target" 2>/dev/null && echo "  down $p" || echo "  $p was not running" ;;
    status) listening "$p" && echo "  up   $p → $target" || echo "  down $p → $target" ;;
    *) echo "usage: $0 up|down|status [ports…]"; exit 2 ;;
  esac
done
