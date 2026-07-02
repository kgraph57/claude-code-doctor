# Linux Read-Only Probe Plan

Linux coverage is beta. Use this as a reviewable shell probe plan before a Linux or WSL checkup, not as a mutation script.

## Boundaries

- Confirm no-go paths before running any command.
- Apply the no-go exclusions to every `find` command before running it.
- Do not run rm, mv, mkdir, touch, chmod, chown, sed -i, package-manager commands, systemctl start/stop/enable/disable, or crontab -e.
- Do not print secrets. If a value looks secret-shaped, report only path and category.
- Prefer shell commands that list metadata, sizes, dates, timers, and listeners.

## Roots To Confirm

- `$HOME`
- `$HOME/.claude`
- `$HOME/.config`
- Any development root such as `$HOME/dev`, `$HOME/Developer`, or `$HOME/src`
- Any WSL mount paths that should be excluded, such as `/mnt/c/Users/...`

## Domain Probes

### Domain 1: Directory structure

```shell
ls -la "$HOME"
```

```shell
find "$HOME/Desktop" "$HOME/Downloads" -maxdepth 2 -type f -printf "%TY-%Tm-%Td\t%s\t%p\n" 2>/dev/null | head -200
```

### Domain 2: Development repositories

```shell
find "$HOME/dev" "$HOME/Developer" "$HOME/src" -name .git -type d -prune -print 2>/dev/null
```

```shell
git status --short --branch
```

### Domain 3: CLAUDE.md hierarchy

```shell
find "$HOME" -path "$HOME/.cache" -prune -o -name CLAUDE.md -type f -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null
```

### Domain 4: Settings and permissions

```shell
ls -la "$HOME/.claude" "$HOME/.config" 2>/dev/null
```

```shell
head -80 "$HOME/.claude/settings.json" 2>/dev/null
```

### Domain 5: Skills

```shell
find "$HOME/.claude/skills" -name SKILL.md -type f -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null
```

### Domain 6: Commands

```shell
find "$HOME/.claude/commands" -type f -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null
```

### Domain 7: Subagents

```shell
find "$HOME/.claude/agents" -type f -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null
```

### Domain 8: MCP and plugins

```shell
find "$HOME/.claude" "$HOME/.config" \( -iname "*mcp*" -o -iname "*plugin*" \) -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null
```

```shell
ss -ltnp 2>/dev/null | head -100
```

### Domain 9: Automations and git hygiene

```shell
crontab -l 2>/dev/null
```

```shell
systemctl --user list-timers --all --no-pager 2>/dev/null
```

```shell
systemctl --user list-unit-files --type=timer --no-pager 2>/dev/null
```

```shell
ls -la "$HOME/.config/systemd/user" 2>/dev/null
```

### Domain 10: Usage reality and disk hygiene

```shell
du -sh "$HOME/.claude" "$HOME/.config/claude-code" 2>/dev/null
```

```shell
find "$HOME/.claude" -type f -printf "%s\t%TY-%Tm-%Td\t%p\n" 2>/dev/null | sort -nr | head -30
```
