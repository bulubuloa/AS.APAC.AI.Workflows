# Installs the ai-workspace kit on Windows (native PowerShell 5.1+ / 7). Idempotent; backs up what it replaces.
# WSL2 users: run ./bootstrap.sh inside WSL instead — it works unchanged there.
[CmdletBinding()] param([string]$Workspace, [switch]$WithCodex)
$ErrorActionPreference = 'Stop'
$Kit = $PSScriptRoot
$WS  = if ($Workspace) { (Resolve-Path $Workspace).Path } else { Split-Path $Kit -Parent }
$ClaudeHome = Join-Path $env:USERPROFILE '.claude'
$CodexHome  = Join-Path $env:USERPROFILE '.codex'
$Stamp = Get-Date -Format 'yyyyMMddHHmmss'

function Say($m)  { Write-Host "==> $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "warn $m" -ForegroundColor Yellow }
function Backup($path, $incoming) {  # copy aside unless identical
  if ((Test-Path $path) -and -not (Get-Item $path).LinkType) {
    if ($incoming -and (Test-Path $incoming) -and ((Get-FileHash $path).Hash -eq (Get-FileHash $incoming).Hash)) { return }
    Copy-Item $path "$path.bak-$Stamp"; Warn "backed up $path"
  }
}
# Claude Code keys project memory by the absolute path with every non-alphanumeric character turned into '-'
# e.g. C:\Users\me\Projects\OmnicasaAS -> C--Users-me-Projects-OmnicasaAS
function Slug($p) { return ($p -replace '[^A-Za-z0-9]', '-') }

Say "workspace: $WS"
if (-not (Test-Path $WS)) { throw "workspace folder not found: $WS (pass -Workspace)" }

# 1. Global preferences
New-Item -ItemType Directory -Force $ClaudeHome | Out-Null
Backup (Join-Path $ClaudeHome 'CLAUDE.md') (Join-Path $Kit 'claude\CLAUDE.md'); Copy-Item (Join-Path $Kit 'claude\CLAUDE.md') (Join-Path $ClaudeHome 'CLAUDE.md'); Say 'installed ~\.claude\CLAUDE.md'

# 2. Workspace instructions, commands, permissions, task files
New-Item -ItemType Directory -Force (Join-Path $WS '.claude\commands') | Out-Null
$issues = Join-Path $WS 'issues'
if ((Test-Path $issues) -and -not (Get-Item $issues).LinkType) {
  Get-ChildItem $issues | ForEach-Object { if (-not (Test-Path (Join-Path $Kit "issues\$($_.Name)"))) { Copy-Item $_.FullName (Join-Path $Kit 'issues') -Recurse } }
  Rename-Item $issues "issues.bak-$Stamp"; Warn 'moved existing issues\ into the kit'
}
if (-not (Test-Path $issues)) { New-Item -ItemType Junction -Path $issues -Target (Join-Path $Kit 'issues') | Out-Null }
Backup (Join-Path $WS 'CLAUDE.md') (Join-Path $Kit 'workspace\CLAUDE.md'); Copy-Item (Join-Path $Kit 'workspace\CLAUDE.md') (Join-Path $WS 'CLAUDE.md')
Get-ChildItem (Join-Path $Kit 'claude\commands\*.md') | Copy-Item -Destination (Join-Path $WS '.claude\commands')
Backup (Join-Path $WS '.claude\settings.json') (Join-Path $Kit 'claude\settings.json'); Copy-Item (Join-Path $Kit 'claude\settings.json') (Join-Path $WS '.claude\settings.json')
Backup (Join-Path $WS '.mcp.json') (Join-Path $Kit 'claude\mcp.json'); Copy-Item (Join-Path $Kit 'claude\mcp.json') (Join-Path $WS '.mcp.json')
Say "installed workspace CLAUDE.md, $((Get-ChildItem (Join-Path $Kit 'claude\commands\*.md')).Count) commands, settings.json, .mcp.json"

# 3. Per-repo instructions
Get-ChildItem (Join-Path $Kit 'workspace\repos') -Directory | ForEach-Object {
  $name = $_.Name
  foreach ($dir in @((Join-Path $WS "Omnicasa.Mobile.$name"), (Join-Path $WS "Omnicasa.Mobile.$name.Clone"))) {
    if (Test-Path $dir) {
      Backup (Join-Path $dir 'CLAUDE.md') (Join-Path $_.FullName 'CLAUDE.md'); Copy-Item (Join-Path $_.FullName 'CLAUDE.md') (Join-Path $dir 'CLAUDE.md'); Say "installed $dir\CLAUDE.md"
      Backup (Join-Path $dir '.mcp.json') (Join-Path $Kit 'claude\mcp.json'); Copy-Item (Join-Path $Kit 'claude\mcp.json') (Join-Path $dir '.mcp.json')
      $ex = Join-Path $dir '.git\info\exclude'
      if (Test-Path (Join-Path $dir '.git')) { New-Item -ItemType Directory -Force (Split-Path $ex) | Out-Null; foreach ($f in 'CLAUDE.md','AGENTS.md','.mcp.json','*.bak-*') { if (-not (Test-Path $ex) -or -not (Select-String -Path $ex -Pattern "^$([regex]::Escape($f))$" -Quiet)) { Add-Content $ex $f } } }
    }
  }
}

# 4. Memory: junction each project's memory folder to the kit (junctions need no admin rights)
function Link-Memory($folder, $kitName) {
  $proj = Join-Path $ClaudeHome ("projects\" + (Slug $folder)); $target = Join-Path $Kit "memory\$kitName"; $mem = Join-Path $proj 'memory'
  New-Item -ItemType Directory -Force $proj | Out-Null
  if ((Test-Path $mem) -and -not (Get-Item $mem).LinkType) {
    Get-ChildItem $mem -Filter *.md | ForEach-Object { if (-not (Test-Path (Join-Path $target $_.Name))) { Copy-Item $_.FullName $target; Warn "kept local note $($_.Name) in kit memory\$kitName" } }
    Rename-Item $mem "memory.bak-$Stamp"
  }
  if ((Test-Path $mem) -and (Get-Item $mem).LinkType) { (Get-Item $mem).Delete() }
  New-Item -ItemType Junction -Path $mem -Target $target | Out-Null; Say "memory: $folder -> memory\$kitName"
}
Link-Memory $WS 'OmnicasaAS'
foreach ($p in @('Omnicasa.Mobile.ABCB','Omnicasa.Mobile.ABCB.Clone')) { if (Test-Path (Join-Path $WS $p)) { Link-Memory (Join-Path $WS $p) 'ABCB' } }
if (Test-Path (Join-Path $WS 'Omnicasa.Mobile.ABMB')) { Link-Memory (Join-Path $WS 'Omnicasa.Mobile.ABMB') 'ABMB' }

# 5. MCP servers (user scope). PS 5.1 turns a native command's stderr into a terminating error under 'Stop',
# so probe registration through cmd instead of 2>$null.
function Has-Mcp($name) { $o = cmd /c "claude mcp get $name 2>nul"; return ($LASTEXITCODE -eq 0 -and $o) }
if (Get-Command claude -ErrorAction SilentlyContinue) {
  if (-not (Has-Mcp atlassian-isos)) { claude mcp add --transport http -s user atlassian-isos https://mcp.atlassian.com/v1/mcp; Say 'mcp: registered atlassian-isos' } else { Say 'mcp: atlassian-isos already registered' }
  if (-not (Has-Mcp playwright))     { claude mcp add -s user playwright -- npx -y "@playwright/mcp@latest"; Say 'mcp: registered playwright' } else { Say 'mcp: playwright already registered' }
} else { Warn 'claude CLI not found - install Claude Code, then run: claude mcp add --transport http -s user atlassian-isos https://mcp.atlassian.com/v1/mcp' }

# 5b. Codex CLI
if ((Test-Path $CodexHome) -or $WithCodex) {
  New-Item -ItemType Directory -Force (Join-Path $CodexHome 'prompts') | Out-Null
  (Get-Content (Join-Path $Kit 'claude\CLAUDE.md') -Raw) -replace 'Co-Authored-By: Claude', 'Co-Authored-By: Codex' | Set-Content (Join-Path $CodexHome 'AGENTS.md')
  Get-ChildItem (Join-Path $Kit 'codex\prompts\*.md') | Copy-Item -Destination (Join-Path $CodexHome 'prompts')
  $pre = Get-Content (Join-Path $Kit 'codex\AGENTS.preamble.md') -Raw; $wsmap = Get-Content (Join-Path $Kit 'workspace\CLAUDE.md') -Raw
  Set-Content (Join-Path $WS 'AGENTS.md') ($pre + $wsmap)
  Get-ChildItem (Join-Path $Kit 'workspace\repos') -Directory | ForEach-Object {
    foreach ($dir in @((Join-Path $WS "Omnicasa.Mobile.$($_.Name)"), (Join-Path $WS "Omnicasa.Mobile.$($_.Name).Clone"))) {
      if (Test-Path $dir) { Set-Content (Join-Path $dir 'AGENTS.md') ($pre + "# Workspace map (from ai-workspace/workspace/CLAUDE.md)`n`n" + $wsmap + "`n---`n`n" + (Get-Content (Join-Path $_.FullName 'CLAUDE.md') -Raw)) }
    }
  }
  $cfg = Join-Path $CodexHome 'config.toml'; if (-not (Test-Path $cfg)) { New-Item $cfg -ItemType File | Out-Null }
  $c = Get-Content $cfg -Raw
  if ($c -notmatch '\[mcp_servers\.atlassian-isos\]') { Add-Content $cfg "`n[mcp_servers.atlassian-isos]`nurl = `"https://mcp.atlassian.com/v1/mcp`"" }
  if ($c -notmatch '\[mcp_servers\.playwright\]')     { Add-Content $cfg "`n[mcp_servers.playwright]`ntype = `"stdio`"`ncommand = `"npx`"`nargs = [`"-y`", `"@playwright/mcp@latest`"]" }
  $wsToml = $WS -replace '\\', '\\\\'
  if ($c -notmatch [regex]::Escape("[projects.`"$wsToml`"]")) { Add-Content $cfg "`n[projects.`"$wsToml`"]`ntrust_level = `"trusted`"" }
  Say 'codex: AGENTS.md (global, workspace, repos), prompts, MCP servers in config.toml - run: codex mcp login atlassian-isos'
}

# 6. Secret guard (git runs hooks under its own bash; perl ships with Git for Windows)
if (Test-Path (Join-Path $Kit '.git')) {
  $hook = Join-Path $Kit '.git\hooks\pre-commit'
  "#!/usr/bin/env bash`ngit diff --cached -U0 -- . ':(exclude)claude/secret-guard.pl' | perl `"`$(git rev-parse --show-toplevel)/claude/secret-guard.pl`" || { echo `"pre-commit: staged diff looks like it contains a credential - point at the secret name instead`"; exit 1; }`n" | Set-Content -NoNewline -Encoding ascii $hook
  Say 'installed secret guard (pre-commit)'
}
Say 'done. Next: claude -> /mcp (authenticate atlassian-isos); twg; aws sso login; open tunnels (access\ACCESS.md); then .\doctor.ps1'
