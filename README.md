# Claude Token Efficiency Analyzer

A Claude Code skill that analyzes your token usage with honest metrics:

- **Cache hit rate**: how much context is reused across sessions (% of tokens from cache)
- **Capacity utilization**: how much of your 200K session window you actually use per session
- **Session statistics**: min/max/average tokens, total sessions — raw numbers
- **No subjective guessing**: objective facts only, with a disclaimer about what's measured

## Quick Start

### Installation

```bash
# Copy the skill into your Claude Code directory
mkdir -p ~/.claude/skills/token-efficiency
curl -sL https://raw.githubusercontent.com/yourusername/claude-token-efficiency/main/SKILL.md \
  -o ~/.claude/skills/token-efficiency/SKILL.md
curl -sL https://raw.githubusercontent.com/yourusername/claude-token-efficiency/main/analyzer.py \
  -o ~/.claude/skills/token-efficiency/analyzer.py
```

Or clone the repo:
```bash
git clone https://github.com/yourusername/claude-token-efficiency.git
cp -r claude-token-efficiency/skill/* ~/.claude/skills/token-efficiency/
```

### Usage

Inside Claude Code, type:
```
/token-efficiency
```

Or run directly:
```bash
python3 ~/.claude/skills/token-efficiency/analyzer.py
```

## What You Get

### Cache Hit Rate
- **Percentage of tokens served from cache** across all Claude Code sessions
- Shows how well you're reusing context
- Example: 99.9% = excellent reuse

### Capacity Utilization (Claude Code only)
- **What percentage of your 200K session window you use** on average
- Shows your batching strategy: small isolated sessions vs. longer batched work
- Example: 14.8% = mostly small sessions, room to batch more work together

### Session Statistics
- **Total sessions tracked**
- **Average tokens per session**
- **Min/max tokens** — shows the range of session sizes
- Recent activity table with dates and token counts

### Important Disclaimer
⚠️ **Claude Code sessions only** — VS Code sessions and other editors are not tracked. Capacity utilization reflects Claude Code usage only.

## How It Works

Reads three local JSON data sources that Claude Code writes automatically — **no API calls, no auth, no data leaves your machine**:

| File | Data |
|------|------|
| `~/.claude/stats-cache.json` | Aggregate tokens by model, daily activity |
| `~/.claude/usage-data/session-meta/*.json` | Per-session: tokens, code changes, tool calls, duration |
| `~/.claude/usage-data/facets/*.json` | Goal outcomes, friction indicators, satisfaction |

## Interpreting Your Report

### Cache Hit Rate Verdicts
- **>85% (EXCELLENT)**: You're reusing context effectively across sessions
- **60–85% (GOOD)**: Reasonable cache reuse
- **<60% (LOW)**: Try keeping related projects in the same session to improve reuse

### Capacity Utilization Verdicts
- **>70% (HIGH)**: You're using a lot of your 200K context per session
- **30–70% (MODERATE)**: Room to batch more work into longer sessions
- **<30% (LOW)**: Consider combining smaller tasks into longer sessions to maximize cache benefits

### What These Mean
- **High cache hit rate** = context is being carried forward effectively
- **Low capacity usage** = sessions are short/isolated; batching them would improve efficiency
- Both together = opportunity to work on larger problems in longer sessions with full context

## Customization

Edit `analyzer.py` to adjust:

```python
# Change for different models (default 200K = Sonnet 4.6)
CONTEXT_WINDOW = 200_000
```

That's it. The analyzer uses only local data and doesn't require pricing or classification logic.

## Requirements

- Python 3.7+ (uses only stdlib — no pip installs needed)
- Claude Code installed (the script reads `~/.claude/` data)
- A terminal with ANSI color support (for heatmap visualization)

## Limitations

- **Claude Code only**: VS Code and other editors are not tracked. Add your VS Code metrics manually if needed.
- **Context window assumption**: Assumes 200K context (Sonnet 4.6). Update `CONTEXT_WINDOW` if you use a different primary model.
- **Early datasets**: Metrics are less meaningful with <3 sessions
- **No subjective quality**: Only shows raw token counts and cache reuse. Doesn't measure solution quality, learning, or other unmeasurable value.

## FAQ

**Q: Does this send data to Anthropic?**
A: No. The script reads local JSON files in `~/.claude/` and prints to your terminal. No network calls.

**Q: How often should I run it?**
A: Whenever you want to check your Claude Code efficiency. Weekly or monthly works well for tracking trends.

**Q: Can I share my results?**
A: Yes, the printed report is plain text. Feel free to share with your team.

**Q: Why only Claude Code sessions, not VS Code?**
A: VS Code doesn't write the same session metadata files to `~/.claude/`. Only Claude Code Web and IDE extensions generate the data this tool reads. You'd need a separate tool for VS Code session tracking.

**Q: What if I use different models (Opus, Haiku)?**
A: Update `CONTEXT_WINDOW` in `analyzer.py` to match your model's context size.

**Q: Why doesn't the report include productivity or goal outcomes?**
A: Those metrics are subjective and hard to measure reliably. Instead, the tool shows objective facts: cache reuse rate and session token counts. You decide if that's valuable.

## Contributing

Found a bug? Have ideas for new metrics? Open an issue or PR!

## License

MIT — use, modify, share freely.

---

**Made for Claude Code users who want to understand their token efficiency at a glance.**
