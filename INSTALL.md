# Installation Guide

Choose one method to install the Claude Token Efficiency skill.

## Method 1: Quick Install (One-liner)

```bash
mkdir -p ~/.claude/skills/token-efficiency && \
curl -sL https://raw.githubusercontent.com/yourusername/claude-token-efficiency/main/SKILL.md \
  -o ~/.claude/skills/token-efficiency/SKILL.md && \
curl -sL https://raw.githubusercontent.com/yourusername/claude-token-efficiency/main/analyzer.py \
  -o ~/.claude/skills/token-efficiency/analyzer.py && \
echo "✓ Skill installed!"
```

## Method 2: Clone the Repo

```bash
git clone https://github.com/yourusername/claude-token-efficiency.git
cp SKILL.md analyzer.py ~/.claude/skills/token-efficiency/
```

If the `~/.claude/skills/token-efficiency/` directory doesn't exist, create it:
```bash
mkdir -p ~/.claude/skills/token-efficiency
```

## Method 3: Manual Copy

1. Download `SKILL.md` and `analyzer.py` from this repo
2. Create the directory: `mkdir -p ~/.claude/skills/token-efficiency`
3. Move the files into that directory

## Verify Installation

Inside Claude Code, type:
```
/token-efficiency
```

You should see the token efficiency report. If not, check:

1. Files are in `~/.claude/skills/token-efficiency/` (the exact path)
2. Both `SKILL.md` and `analyzer.py` are present
3. Python 3.7+ is available: `python3 --version`
4. You have at least one Claude Code session (data in `~/.claude/usage-data/`)

## Troubleshooting

**"Skill not found"**
- Make sure both `SKILL.md` and `analyzer.py` are in the exact directory: `~/.claude/skills/token-efficiency/`
- Restart Claude Code to force skill discovery

**"No data available" or empty report**
- You need at least one Claude Code session to analyze
- Check that `~/.claude/usage-data/session-meta/` has JSON files

**"ModuleNotFoundError" or Python errors**
- Ensure Python 3.7+: `python3 --version`
- The script uses only the standard library — no pip installs needed

**Colors not showing in heatmap**
- Your terminal may not support ANSI colors
- Try: `echo -e "\033[32mgreen\033[0m"` to test
- The report will still work; colors are just cosmetic

## Updating

To update to the latest version:

```bash
# If you cloned the repo:
cd claude-token-efficiency && git pull && \
cp SKILL.md analyzer.py ~/.claude/skills/token-efficiency/

# If you used quick install:
# Re-run the one-liner above
```

## Uninstalling

```bash
rm -rf ~/.claude/skills/token-efficiency
```

## Next Steps

Once installed, run it anytime:

```
/token-efficiency
```

Or from your terminal:
```bash
python3 ~/.claude/skills/token-efficiency/analyzer.py
```

See [README.md](README.md) for detailed usage and interpretation guide.
