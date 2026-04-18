---
name: token-efficiency
description: "Analyze your Claude Code token usage efficiency — see wasted tokens, unused context capacity, activity heatmaps, and productivity metrics across all sessions."
trigger: /token-efficiency
---

# /token-efficiency

Analyzes token usage across all your Claude Code sessions and prints a dashboard showing:

- **Token totals** — input, output, cache reads/writes, combined usage
- **Cache hit rate** — how often context is served from cache (cheap vs expensive)
- **Estimated cost** — USD spend using Anthropic's published rates
- **Activity heatmap** — GitHub-style grid showing token volume + productivity quality per day
- **Session breakdown** — classifies each session as PRODUCTIVE / EXPLORING / CONVERSATION / EMPTY
- **Waste analysis** — tokens spent in non-coding sessions + friction rework
- **Context window utilization** — how much of the 200K Sonnet cap each session used
- **Unused capacity** — total available capacity minus what you actually used (the tokens you "left on the table")
- **Monthly summary** — tokens and cost grouped by month
- **Efficiency metrics** — tokens per line of code, message-to-tool ratio
- **Potential vs achieved** — goal outcomes from session facets

## Usage

```
/token-efficiency
```

No arguments needed. The skill reads from `~/.claude/` on any user's machine.

## How It Works

When the user invokes `/token-efficiency`, run the bundled Python script:

```bash
python3 ~/.claude/skills/token-efficiency/analyzer.py
```

The script reads three local data sources that Claude Code writes automatically:

| File | Contents |
|------|----------|
| `~/.claude/stats-cache.json` | Aggregate tokens by model, daily activity |
| `~/.claude/usage-data/session-meta/*.json` | Per-session tokens, lines changed, tool calls |
| `~/.claude/usage-data/facets/*.json` | Goal outcome, friction, satisfaction |

No external APIs, no auth — everything is local.

## What to Do After Running

After executing the script and showing the output:

1. **Call out the headline insights** — highlight the 1-2 most striking numbers (e.g., cache hit rate, unused capacity %, waste %)
2. **Interpret the verdict** — explain what "Low/Moderate/Good/Excellent" utilization means for their workflow
3. **Give actionable advice** based on the data:
   - If utilization rate < 30%: suggest batching smaller tasks into longer sessions
   - If waste % > 30%: suggest planning prompts more carefully before opening Claude
   - If cache hit rate < 60%: suggest keeping the same project/context across sessions
   - If many EMPTY sessions: the user is opening Claude but not completing work

## Notes

- Pricing is hardcoded (Sonnet 4.6 $3/$15 in/out per MTok; Haiku 4.5 $0.80/$4 per MTok) — update the `PRICING` dict in `analyzer.py` when Anthropic's rates change.
- Context window is assumed 200K (Sonnet 4.6). Update `CONTEXT_WINDOW` constant if the user primarily uses a different model.
- If the user has fewer than 3 sessions, the report will still run but metrics like "best session efficiency" will be degenerate. Mention this caveat if applicable.
- ANSI color codes are used for the productivity heatmap (green/yellow/red). These render correctly in terminals but may appear as raw escape codes if piped to files.
