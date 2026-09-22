# Installs the CLIs the workflow needs on Windows and fixes corporate TLS (Zscaler) for them. Idempotent; called by
# bootstrap.ps1 (skip with -NoTools). winget may raise UAC prompts for machine-scope installers - click Yes.
[CmdletBinding()] param()
$ErrorActionPreference = 'Continue'
function Say($m)  { Write-Host "==> $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "warn $m" -ForegroundColor Yellow }
function Refresh-Path { $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') }
# the Microsoft Store ships python/python3 stubs that only open the Store - not a real install
function Have($c) { $cmd = Get-Command $c -ErrorAction SilentlyContinue; if (-not $cmd) { return $false }; return ($cmd.Source -notmatch '\\WindowsApps\\') }

Refresh-Path   # the calling window may predate earlier installs
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { Warn 'winget not found (install "App Installer" from the Microsoft Store) - skipping tool installs'; return }

# 1. CLIs via winget: command to test | winget id | extra args
$tools = @(
  @('git',     'Git.Git',                 @()),
  @('node',    'OpenJS.NodeJS.LTS',       @()),
  @('claude',  'Anthropic.ClaudeCode',    @()),
  @('aws',     'Amazon.AWSCLI',           @()),
  @('python',  'Python.Python.3.12',      @('--scope','user')),
  @('dotnet',  'Microsoft.DotNet.SDK.8',  @()),
  @('sqlcmd',  'Microsoft.Sqlcmd',        @()),
  @('mysqlsh', 'Oracle.MySQLShell',       @())
)
foreach ($t in $tools) {
  $cmd, $id, $extra = $t
  if (Have $cmd) { Say "$cmd present"; continue }
  Say "installing $id"
  winget install --id $id -e --accept-package-agreements --accept-source-agreements --disable-interactivity @extra | Select-String 'Successfully|already installed|error|failed' | ForEach-Object { "     $_" }
  Refresh-Path
}

# 2. twg (Atlassian Teamwork Graph CLI) - official installer, user scope, login done later by the developer
if (Have 'twg') { Say 'twg present' } else {
  Say 'installing twg'
  $inst = Join-Path $env:TEMP 'twg-install.ps1'
  curl.exe -fsSL https://teamwork-graph.atlassian.com/cli/install.ps1 -o $inst
  if (Test-Path $inst) { powershell -ExecutionPolicy Bypass -File $inst -SkipLogin -SkipSkills -Yes | Select-String 'Installed|error' | ForEach-Object { "     $_" }; Refresh-Path } else { Warn 'twg installer download failed - see https://developer.atlassian.com/cloud/twg-cli/getting-started/installation/' }
}

# 3. Corporate TLS inspection (Zscaler): python/node-based CLIs ship their own CA list and reject the proxy's
#    certificate. Build one bundle = AWS CLI's public CAs + the Zscaler roots from the Windows store, point the CLIs at it.
$zs = Get-ChildItem Cert:\LocalMachine\Root, Cert:\CurrentUser\Root, Cert:\LocalMachine\CA, Cert:\CurrentUser\CA -ErrorAction SilentlyContinue | Where-Object { $_.Subject -match 'Zscaler' } | Sort-Object Thumbprint -Unique
if ($zs) {
  $bundle = Join-Path $env:USERPROFILE '.aws\ca-bundle.pem'
  $base = Get-ChildItem 'C:\Program Files\Amazon\AWSCLIV2' -Recurse -Filter cacert.pem -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($base) {
    New-Item -ItemType Directory -Force (Split-Path $bundle) | Out-Null
    $sb = New-Object Text.StringBuilder; $null = $sb.Append((Get-Content $base.FullName -Raw))
    foreach ($c in $zs) {
      $b64 = [Convert]::ToBase64String($c.Export('Cert')); $null = $sb.Append("`n# $($c.Subject)`n-----BEGIN CERTIFICATE-----`n")
      for ($i = 0; $i -lt $b64.Length; $i += 64) { $null = $sb.Append($b64.Substring($i, [Math]::Min(64, $b64.Length - $i)) + "`n") }
      $null = $sb.Append("-----END CERTIFICATE-----`n")
    }
    [IO.File]::WriteAllText($bundle, $sb.ToString())
    foreach ($v in 'AWS_CA_BUNDLE','REQUESTS_CA_BUNDLE','SSL_CERT_FILE','NODE_EXTRA_CA_CERTS') { [Environment]::SetEnvironmentVariable($v, $bundle, 'User'); Set-Item "env:$v" $bundle }
    if (Have 'aws') { aws configure set ca_bundle $bundle }
    Say "zscaler detected: CA bundle $bundle (AWS_CA_BUNDLE, REQUESTS_CA_BUNDLE, SSL_CERT_FILE, NODE_EXTRA_CA_CERTS)"
  } else { Warn 'zscaler detected but AWS CLI not installed yet - re-run to build the CA bundle' }
}
if (Have 'aws') { aws configure set region ap-southeast-1 }

# 4. Python helpers the agent uses for DB / PGP work
if (Have 'python') { python -m pip install --quiet --disable-pip-version-check pymysql pgpy boto3 2>&1 | Select-String 'error' | ForEach-Object { "     $_" }; Say 'python: pymysql pgpy boto3' } else { Warn 'python not on PATH yet - open a new window and run: pip install pymysql pgpy boto3' }
