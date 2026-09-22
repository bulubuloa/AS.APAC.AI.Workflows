# Clones the product repos side by side into the workspace (the kit's parent folder by default), each on the
# branch that feeds the first test environment. Idempotent: existing folders are left alone. Uses your own
# Bitbucket credential (Git Credential Manager prompts). Called by bootstrap.ps1; standalone: .\clone.ps1 [-Workspace path]
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
  @{ Dir = 'ABCB.Clone';  Repo = 'apac-benefit-client-backend';        Branch = 'develop' }
)
New-Item -ItemType Directory -Force $WS | Out-Null; $WS = (Resolve-Path $WS).Path; Say "workspace: $WS"
foreach ($r in $Repos) {
  $dir = Join-Path $WS $r.Dir
  if (Test-Path (Join-Path $dir '.git')) { Say "$($r.Dir) already cloned ($(git -C $dir branch --show-current))"; continue }
  Say "cloning $($r.Repo) -> $($r.Dir) ($($r.Branch))"
  git clone -b $r.Branch "$BB/$($r.Repo).git" $dir
  if ($LASTEXITCODE -ne 0) { throw "git clone failed for $($r.Repo)" }
}
Say "repos ready in $WS"
