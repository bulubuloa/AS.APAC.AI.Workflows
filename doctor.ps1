# Verifies the setup the agent depends on, on Windows. Read-only. One line per check.
[CmdletBinding()] param([string]$Workspace)
$Kit = $PSScriptRoot; $WS = if ($Workspace) { (Resolve-Path $Workspace).Path } else { Split-Path $Kit -Parent }
$ClaudeHome = Join-Path $env:USERPROFILE '.claude'
function OK($m)  { Write-Host "  OK   $m" -ForegroundColor Green }
function Bad($m) { Write-Host "  MISS $m" -ForegroundColor Red }
function Have($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Slug($p) { return ($p -replace '[^A-Za-z0-9]', '-') }

Write-Host 'tools'
foreach ($t in 'claude','twg','aws','git','dotnet','node','python','sqlcmd') { if (Have $t) { OK $t } else { Bad "$t not on PATH" } }
if ((Have 'mysql') -or (Have 'mysqlsh')) { OK 'mysql client' } else { Bad 'mysql client (winget install Oracle.MySQL or MySQL Shell)' }
if (Have 'python') { if (python -c "import pymysql" 2>$null; $LASTEXITCODE -eq 0) { OK 'python pymysql' } else { Bad 'python pymysql (pip install pymysql)' } }

Write-Host 'repos'
foreach ($r in 'ABMB','ABVB','ABF','ABCB','ABCB.Clone') { $d = Join-Path $WS "Omnicasa.Mobile.$r"; if (Test-Path (Join-Path $d '.git')) { OK "$r ($(git -C $d branch --show-current))" } else { Bad "$r missing at $d" } }

Write-Host 'claude config'
if (Test-Path (Join-Path $ClaudeHome 'CLAUDE.md')) { OK '~\.claude\CLAUDE.md' } else { Bad '~\.claude\CLAUDE.md' }
if (Test-Path (Join-Path $WS 'CLAUDE.md')) { OK 'workspace CLAUDE.md' } else { Bad 'workspace CLAUDE.md' }
foreach ($c in 'task-fetch','task-analyse','task-implement','task-verify','task-deliver','task-run') { if (Test-Path (Join-Path $WS ".claude\commands\$c.md")) { OK "/$c" } else { Bad "/$c command" } }
foreach ($p in @($WS, (Join-Path $WS 'Omnicasa.Mobile.ABCB'), (Join-Path $WS 'Omnicasa.Mobile.ABMB'))) {
  $mem = Join-Path $ClaudeHome ("projects\" + (Slug $p) + "\memory")
  if ((Test-Path $mem) -and (Get-Item $mem).LinkType) { OK "memory linked: $(Split-Path $p -Leaf) -> $((Get-Item $mem).Target)" } else { Bad "memory not linked for $p (expected $mem)" }
}
if (Have 'claude') { $l = claude mcp list 2>$null; if ($l -match 'atlassian-isos') { OK 'MCP atlassian-isos registered (authenticate with /mcp inside claude)' } else { Bad 'MCP atlassian-isos' }; if ($l -match 'playwright') { OK 'MCP playwright' } else { Bad 'MCP playwright' } }

Write-Host 'codex (optional)'
$CodexHome = Join-Path $env:USERPROFILE '.codex'
if (Test-Path $CodexHome) {
  if (Test-Path (Join-Path $CodexHome 'AGENTS.md')) { OK '~\.codex\AGENTS.md' } else { Bad '~\.codex\AGENTS.md' }
  if (Test-Path (Join-Path $WS 'AGENTS.md')) { OK 'workspace AGENTS.md' } else { Bad 'workspace AGENTS.md' }
  if (Test-Path (Join-Path $CodexHome 'prompts\task-fetch.md')) { OK '/prompts:task-fetch' } else { Bad 'codex prompt task-fetch' }
  if ((Test-Path (Join-Path $CodexHome 'config.toml')) -and ((Get-Content (Join-Path $CodexHome 'config.toml') -Raw) -match 'mcp_servers\.atlassian-isos')) { OK 'codex MCP atlassian-isos in config.toml (login: codex mcp login atlassian-isos)' } else { Bad 'codex MCP atlassian-isos' }
} else { OK 'codex not installed - skipped' }

Write-Host 'access'
$acct = aws sts get-caller-identity --query Account --output text 2>$null
if ($acct -eq '739075353953') { OK 'AWS account 739075353953' } else { Bad 'AWS credentials (aws sso login / profile) - expected account 739075353953' }
aws secretsmanager describe-secret --secret-id benefit-connection-string-preprod *> $null; if ($LASTEXITCODE -eq 0) { OK 'can read secret benefit-connection-string-preprod' } else { Bad 'secret benefit-connection-string-preprod not readable' }
foreach ($t in @(@(3375,'Benefit SIT/UAT MySQL (benefit-sit cluster)'), @(3382,'Benefit PROD MySQL (read-only use)'), @(3383,'RSA PROD MSSQL'))) {
  if (Get-NetTCPConnection -State Listen -LocalPort $t[0] -ErrorAction SilentlyContinue) { OK "tunnel $($t[0]) $($t[1])" } else { Bad "tunnel $($t[0]) $($t[1]) not listening" }
}
if (Have 'twg') { twg confluence space get AD *> $null; if ($LASTEXITCODE -eq 0) { OK 'twg Confluence (AD space)' } else { Bad 'twg not authenticated (run: twg confluence space get AD)' } }
Write-Host 'done'
