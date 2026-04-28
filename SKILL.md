---
name: token-efficiency
description: "Analyze your Claude Code token usage efficiency — see how many tokens you waste per session due to poor batching."
trigger: /token-efficiency
---

# /token-efficiency

Analyzes token usage across all your Claude Code sessions and prints a single-screen dashboard showing:

- **Cache hit rate** — how often context is reused (% of tokens served from cache)
- **Wasted tokens per session** — tokens left unused when each session window resets (200K - actual_used)
- **Efficiency per session** — what % of each session's context window was actually consumed
- **Visualization** — chart showing used (green) vs wasted (red) for each session, plus efficiency trend

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

After executing the script:

1. **ALWAYS print the full output** — do NOT summarize or condense the report, including the visualization
2. Output everything from the script without interruption
3. THEN provide interpretation:
   - Highlight total wasted tokens and which sessions are most inefficient (shown in red on the chart)
   - Explain the pattern: sessions below 30% efficiency are critical waste, above 50% are good
   - Point to the visualization chart: green = used tokens, red = wasted capacity
   - Give specific recommendations for batching related work into longer sessions

## Notes

- Context window is assumed 200K (Sonnet 4.6). Update `CONTEXT_WINDOW` constant if the user primarily uses a different model.
- If the user has fewer than 3 sessions, the metrics will still run but may not be representative. Mention this caveat if applicable.
- The script reads only local data — no API calls, no authentication required.
