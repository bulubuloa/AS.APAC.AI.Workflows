# Clones the product repos side by side into the workspace (the kit's parent folder by default), each on the
# branch that feeds the first test environment. Idempotent: existing folders are left alone. Signs you in to
# Bitbucket once via OAuth (Git Credential Manager, bundled with Git for Windows) and keeps the token in Windows
# Credential Manager. Called by bootstrap.ps1; standalone: .\clone.ps1 [-Workspace path]
[CmdletBinding()] param([string]$Workspace)
$ErrorActionPreference = 'Stop'
$Kit = $PSScriptRoot
$WS  = if ($Workspace) { $Workspace } else { Split-Path $Kit -Parent }
$BB  = 'https://bitbucket.org/internationalsos'
function Say($m) { Write-Host "==> $m" -ForegroundColor Cyan }
# folder names matter — the agent knows the repos by these names
$Repos = @(
  @{ Dir = 'ABMB';        Repo = 'apac-booking-modernization-backend'; Branch = 'roadside-release-uat' },
  @{ Dir = 'ABVB';        Repo = 'apac-benefit-vendor-backend';        Branch = 'develop' },
  @{ Dir = 'ABF';         Repo = 'apac-benefits-frontend';             Branch = 'develop' },
  @{ Dir = 'ABCB';        Repo = 'apac-benefit-client-backend';        Branch = 'data-processer-pre-production' },
  @{ Dir = 'ABCB.Clone';  Repo = 'apac-benefit-client-backend';        Branch = 'develop' },
  @{ Dir = 'ABMR';        Repo = 'apac_mobile_roadside';               Branch = 'main' }
)
New-Item -ItemType Directory -Force $WS | Out-Null; $WS = (Resolve-Path $WS).Path; Say "workspace: $WS"

# Bitbucket OAuth via GCM, scoped to bitbucket.org; one probe so the browser opens once, not per repo
if ($Repos | Where-Object { -not (Test-Path (Join-Path (Join-Path $WS $_.Dir) '.git')) }) {
  git config --global credential.https://bitbucket.org.helper manager
  git config --global credential.https://bitbucket.org.bitbucketAuthModes oauth
  Say 'bitbucket: signing in (a browser opens the first time)'
  git ls-remote "$BB/apac-benefit-vendor-backend.git" HEAD | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "bitbucket sign-in failed - check you have access to $BB" }
  Say 'bitbucket: signed in'
}
foreach ($r in $Repos) {
  $dir = Join-Path $WS $r.Dir
  if (Test-Path (Join-Path $dir '.git')) { Say "$($r.Dir) already cloned ($(git -C $dir branch --show-current))"; continue }
  Say "cloning $($r.Repo) -> $($r.Dir) ($($r.Branch))"
  git clone -b $r.Branch "$BB/$($r.Repo).git" $dir
  if ($LASTEXITCODE -ne 0) { throw "git clone failed for $($r.Repo)" }
}
Say "repos ready in $WS"
