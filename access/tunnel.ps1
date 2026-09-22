# DB tunnels through the bastion (Windows OpenSSH). Targets from tunnels.env; key from $env:ABE_SSH_KEY or ~\.ssh\ABE.pem.
# Usage: powershell -File access\tunnel.ps1 up|down|status [3375 3382 3383]
param([ValidateSet('up','down','status')][string]$Cmd = 'status', [int[]]$Ports = @(3375, 3382, 3383))
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg = @{}
foreach ($f in 'tunnels.env', 'tunnels.local.env') { $p = Join-Path $here $f; if (Test-Path $p) { Get-Content $p | ? { $_ -match '^\s*([A-Z_0-9]+)=([^#]+)' } | % { $cfg[$Matches[1]] = $Matches[2].Trim() } } }
$key = if ($env:ABE_SSH_KEY) { $env:ABE_SSH_KEY } else { Join-Path $HOME '.ssh\ABE.pem' }
foreach ($port in $Ports) {
  $target = $cfg["TUNNEL_$port"]; if (-not $target) { Write-Error "no TUNNEL_$port in tunnels.env"; exit 1 }
  $proc = Get-CimInstance Win32_Process -Filter "Name='ssh.exe'" | ? { $_.CommandLine -like "*-L ${port}:$target*" }
  switch ($Cmd) {
    'status' { if ($proc) { "  up   $port -> $target" } else { "  down $port -> $target" } }
    'down'   { if ($proc) { $proc | % { Stop-Process -Id $_.ProcessId }; "  down $port" } else { "  $port was not running" } }
    'up'     {
      if ($proc) { "  up   $port -> $target (already)"; continue }
      if (-not (Test-Path $key)) { Write-Error "PEM key not found: $key - set ABE_SSH_KEY or copy the key to ~\.ssh\ABE.pem"; exit 1 }
      Start-Process ssh -WindowStyle Hidden -ArgumentList @('-i', "`"$key`"", '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=60', '-L', "${port}:$target", "$($cfg.BASTION_USER)@$($cfg.BASTION_HOST)", '-N')
      "  up   $port -> $target (if it drops at once: the bastion security group must allow your public IP on port 22)"
    }
  }
}
