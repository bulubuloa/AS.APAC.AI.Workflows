#!/usr/bin/env bash
# Clones the product repos side by side into the workspace (the kit's parent folder by default), each on the
# branch that feeds the first test environment. Idempotent: existing folders are left alone. Signs you in to
# Bitbucket once via OAuth (Git Credential Manager, browser) and keeps the token in the OS keychain.
# Called by bootstrap.sh; standalone: ./clone.sh [workspace]
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
WS="${1:-$(dirname "$KIT")}"
BB=https://bitbucket.org/internationalsos
say() { printf '\033[36m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33mwarn\033[0m %s\n' "$*"; }
# folder | repo | branch   (folder names matter — the agent knows the repos by these names)
REPOS="
ABMB        apac-booking-modernization-backend  roadside-release-uat
ABVB        apac-benefit-vendor-backend         develop
ABF         apac-benefits-frontend              develop
ABCB        apac-benefit-client-backend         data-processer-pre-production
ABCB.Clone  apac-benefit-client-backend         develop
"

# Bitbucket OAuth through Git Credential Manager, scoped to bitbucket.org so other hosts keep their helper.
# App passwords are retired; without GCM git falls back to prompting for a Bitbucket API token.
bb_oauth() {
  local gcm; gcm="$(command -v git-credential-manager || true)"
  [ -z "$gcm" ] && [ -x "/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe" ] && gcm="/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"  # WSL: borrow the Windows one
  if [ -z "$gcm" ]; then warn "git-credential-manager not found - git will prompt for a Bitbucket API token instead"; return; fi
  git config --global --unset-all credential.https://bitbucket.org.helper || true
  git config --global --add credential.https://bitbucket.org.helper ""     # empty entry drops inherited helpers (osxkeychain)
  git config --global --add credential.https://bitbucket.org.helper "${gcm// /\\ }"   # git runs the helper through sh; escape the space in "Program Files"
  git config --global credential.https://bitbucket.org.bitbucketAuthModes oauth
  # one probe so the browser opens once, not per repo; later runs reuse the stored token
  say "bitbucket: signing in (a browser opens the first time)"
  git ls-remote "$BB/apac-benefit-vendor-backend.git" HEAD >/dev/null || { echo "bitbucket sign-in failed - check you have access to $BB"; exit 1; }
  say "bitbucket: signed in"
}

mkdir -p "$WS"; say "workspace: $WS"
need=0; for d in ABMB ABVB ABF ABCB ABCB.Clone; do [ -d "$WS/$d/.git" ] || need=1; done
[ "$need" = 1 ] && bb_oauth
echo "$REPOS" | while read -r dir repo branch; do
  [ -z "$dir" ] && continue
  if [ -d "$WS/$dir/.git" ]; then say "$dir already cloned ($(git -C "$WS/$dir" branch --show-current))"; continue; fi
  say "cloning $repo -> $dir ($branch)"; git clone -b "$branch" "$BB/$repo.git" "$WS/$dir"
done
say "repos ready in $WS"

