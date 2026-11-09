# Commits any changes in the project folder and pushes them to GitHub.
# Run by the Windows scheduled task "Sidewalks-mapping auto-sync" (daily) and safe to run by hand.
# Files over 50 MB are never committed (GitHub rejects >100 MB); they are listed in the log instead.

$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $env:LOCALAPPDATA 'SidewalksMappingSync'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir 'sync.log'
function Log($msg) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg" | Out-File -Append -Encoding utf8 $log }

Set-Location $repo
$env:GIT_TERMINAL_PROMPT = '0'

# Bring in anything pushed from elsewhere first.
git pull --rebase --autostash -q origin main 2>&1 | ForEach-Object { Log "pull: $_" }

git add -A 2>$null

# Unstage oversized files so a push never fails on them.
$limit = 50MB
git diff --cached --name-only -z 2>$null | ForEach-Object { $_ -split "`0" } | Where-Object { $_ } | ForEach-Object {
    $p = Join-Path $repo $_
    if ((Test-Path -LiteralPath $p) -and ((Get-Item -LiteralPath $p).Length -gt $limit)) {
        git reset -q -- "$_" 2>$null
        Log "skipped large file (add to .gitignore): $_"
    }
}

$staged = git diff --cached --name-only 2>$null
if (-not $staged) { Log 'no changes'; exit 0 }

$count = @($staged).Count
git commit -q -m "Auto-sync $(Get-Date -Format 'yyyy-MM-dd HH:mm') ($count files)" 2>&1 | ForEach-Object { Log "commit: $_" }
$out = git push -q origin main 2>&1
if ($LASTEXITCODE -eq 0) { Log "pushed $count changed files" } else { Log "PUSH FAILED: $out" }
