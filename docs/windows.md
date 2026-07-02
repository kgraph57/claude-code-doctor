# Windows Read-Only Probe Plan

Windows coverage is beta. Use this as a reviewable probe plan before a Windows checkup, not as a mutation script.

## Boundaries

- Confirm no-go paths before running any command.
- Do not run Set-Item, Remove-Item, New-Item, Move-Item, Copy-Item, schtasks /Change, schtasks /Delete, or any registry write.
- Do not print secrets. If a value looks secret-shaped, report only path and category.
- Prefer PowerShell commands that list metadata, sizes, and dates.

## Roots To Confirm

- `$env:USERPROFILE`
- `$env:APPDATA`
- `$env:LOCALAPPDATA`
- Any development root such as `$env:USERPROFILE\source` or `$env:USERPROFILE\dev`

## Domain Probes

### Domain 1: Directory structure

```powershell
Get-ChildItem -Force $env:USERPROFILE | Select-Object Name,Mode,Length,LastWriteTime
```

```powershell
Get-ChildItem -Force $env:USERPROFILE\Desktop,$env:USERPROFILE\Downloads -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

### Domain 2: Development repositories

```powershell
Get-ChildItem -Recurse -Force -Directory -Filter .git $env:USERPROFILE\source,$env:USERPROFILE\dev -ErrorAction SilentlyContinue | Select-Object FullName
```

```powershell
git status --short --branch
```

### Domain 3: CLAUDE.md hierarchy

```powershell
Get-ChildItem -Recurse -Force -Filter CLAUDE.md $env:USERPROFILE -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

### Domain 4: Settings and permissions

```powershell
Get-ChildItem -Force $env:APPDATA,$env:LOCALAPPDATA -ErrorAction SilentlyContinue | Select-Object FullName,Mode,LastWriteTime
```

```powershell
Get-Content -TotalCount 80 $env:APPDATA\Claude\settings.json -ErrorAction SilentlyContinue
```

### Domain 5: Skills

```powershell
Get-ChildItem -Recurse -Force -Filter SKILL.md $env:USERPROFILE\.claude\skills -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

### Domain 6: Commands

```powershell
Get-ChildItem -Recurse -Force $env:USERPROFILE\.claude\commands -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

### Domain 7: Subagents

```powershell
Get-ChildItem -Recurse -Force $env:USERPROFILE\.claude\agents -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

### Domain 8: MCP and plugins

```powershell
Get-ChildItem -Recurse -Force $env:APPDATA,$env:LOCALAPPDATA -Include *mcp*,*plugin* -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess
```

### Domain 9: Automations and git hygiene

```powershell
Get-ScheduledTask | Select-Object TaskName,TaskPath,State
```

```powershell
schtasks /Query /FO LIST /V
```

### Domain 10: Usage reality and disk hygiene

```powershell
Get-ChildItem -Force $env:USERPROFILE\.claude -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
```

```powershell
Get-ChildItem -Recurse -Force $env:USERPROFILE\.claude -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 30 FullName,Length,LastWriteTime
```
