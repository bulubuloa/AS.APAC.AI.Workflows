#!/usr/bin/env bash
# Clones the product repos side by side into the workspace (the kit's parent folder by default), each on the
# branch that feeds the first test environment. Idempotent: existing folders are left alone. Uses your own
# Bitbucket credential (git prompts). Usage: ./clone.sh [workspace] ; add --bootstrap to run bootstrap.sh after.
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
WS="$(dirname "$KIT")"; RUN_BOOTSTRAP=
for a in "$@"; do case "$a" in --bootstrap) RUN_BOOTSTRAP=1 ;; *) WS="$a" ;; esac; done
BB=https://bitbucket.org/internationalsos
say() { printf '\033[36m==> %s\033[0m\n' "$*"; }
# folder | repo | branch   (folder names matter — the agent knows the repos by these names)
REPOS="
ABMB        apac-booking-modernization-backend  roadside-release-uat
ABVB        apac-benefit-vendor-backend         develop
ABF         apac-benefits-frontend              develop
ABCB        apac-benefit-client-backend         data-processer-pre-production
ABCB.Clone  apac-benefit-client-backend         develop
"
mkdir -p "$WS"; say "workspace: $WS"
echo "$REPOS" | while read -r dir repo branch; do
  [ -z "$dir" ] && continue
  if [ -d "$WS/$dir/.git" ]; then say "$dir already cloned ($(git -C "$WS/$dir" branch --show-current))"; continue; fi
  say "cloning $repo -> $dir ($branch)"; git clone -b "$branch" "$BB/$repo.git" "$WS/$dir"
done
say "done. Next: $KIT/bootstrap.sh"
[ -n "$RUN_BOOTSTRAP" ] && exec bash "$KIT/bootstrap.sh"; true
