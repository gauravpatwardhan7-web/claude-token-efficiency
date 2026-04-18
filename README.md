# Claude Token Efficiency Analyzer

A Claude Code skill that analyzes your token usage across all sessions and reveals:

- **Actual efficiency**: tokens used vs. wasted
- **Unused potential**: how much context window capacity you left on the table
- **Productivity patterns**: which sessions produced code vs. just exploration/chat
- **Cost analysis**: estimated USD spend using Anthropic's published rates
- **Activity heatmaps**: GitHub-style visualization of when you were active and productive
- **Monthly trends**: tokens and cost grouped by month
- **Actionable insights**: specific recommendations to improve efficiency

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

### Overview
- Total tokens used (input, output, cache reads/writes)
- **99.9% cache hit rate** example: you're reusing context across sessions (excellent!)
- Estimated cost using Anthropic's published pricing

### Activity Heatmap
Side-by-side grids showing:
- **Left**: token volume per day (light to peak usage)
- **Right**: productivity quality (green = productive code, yellow = exploration, red = empty)

Example: see at a glance which days were high-effort vs. low-effort

### Session Breakdown
Table showing each session:
- Date, project, duration, tokens, lines changed
- Classification: **PRODUCTIVE** (code written), **EXPLORING** (tools used), **CONVERSATION** (Q&A), **EMPTY** (nothing done)
- Goal outcome: fully/mostly/partially achieved

### Waste Analysis
- Tokens in non-productive sessions (empty, conversation, exploration)
- Friction rework estimate (20% of sessions with "wrong approach" friction)
- Overall inefficiency percentage

### Unused Capacity
The headline metric — **how much context window you left unused**:
```
Total available capacity    : 1.2M  (6 sessions × 200K per session)
Total tokens you used       : 177.1K
Total unused capacity       : 1.0M
Overall utilization rate    : 14.8%
Verdict                     : Low — you could tackle much more in each session
```

### Efficiency Metrics
- Tokens per line of code (lower = more efficient)
- Message-to-tool-call ratio (balanced talking vs. doing)
- Session type breakdown

### Potential vs Achieved
- Goal achievement rate from session facets
- Sessions with friction points (misunderstood request, wrong approach)

## How It Works

Reads three local JSON data sources that Claude Code writes automatically — **no API calls, no auth, no data leaves your machine**:

| File | Data |
|------|------|
| `~/.claude/stats-cache.json` | Aggregate tokens by model, daily activity |
| `~/.claude/usage-data/session-meta/*.json` | Per-session: tokens, code changes, tool calls, duration |
| `~/.claude/usage-data/facets/*.json` | Goal outcomes, friction indicators, satisfaction |

## Interpreting Your Report

### Cache Hit Rate
- **>85%**: Excellent — context is highly reused
- **60–85%**: Good — reasonable reuse
- **<60%**: Low — consider keeping related work in same project

### Utilization Rate
- **<30%**: Low — batch smaller tasks into longer sessions
- **30–60%**: Moderate — room to tackle more per session
- **60–80%**: Good — using context well
- **>80%**: Excellent — pushing context window effectively

### Session Types
- **PRODUCTIVE**: lines were added/removed to files ✓
- **EXPLORING**: tools were called but no code written
- **CONVERSATION**: just Q&A, no tools
- **EMPTY**: session opened but nothing happened

## Customization

Edit `analyzer.py` to adjust:

```python
# Update when Anthropic's pricing changes
PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.0,      # $/million tokens
        "output": 15.0,
        "cache_read": 0.30,
        "cache_write": 3.75,
    },
    ...
}

# Change for different models (default 200K = Sonnet 4.6)
CONTEXT_WINDOW = 200_000

# Adjust what counts as "productive"
def classify_session(meta):
    tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
    lines = meta.get("lines_added", 0) + meta.get("lines_removed", 0)
    ...
```

## Requirements

- Python 3.7+ (uses only stdlib — no pip installs needed)
- Claude Code installed (the script reads `~/.claude/` data)
- A terminal with ANSI color support (for heatmap visualization)

## Limitations

- **Cost estimates**: Use published rates, not actual billing (Pro/Team plans are subscription-based)
- **Productivity inference**: Only counts code changes — valuable sessions (design, debugging, teaching) may not register
- **Cache hit rate**: Reflects Claude Code's prompt caching, not conversation memory
- **Early datasets**: Metrics are noisy if you have <3 sessions

## FAQ

**Q: Does this send data to Anthropic?**
A: No. The script reads local JSON files in `~/.claude/` and prints to your terminal. No network calls.

**Q: How often should I run it?**
A: Monthly or whenever you want to check efficiency trends. The script reads live data, so you get current stats each time.

**Q: Can I share my results?**
A: Yes, the printed report is plain text. Feel free to share the heatmap and metrics with your team.

**Q: What if I use different models (Opus, Haiku)?**
A: Update `PRICING` and `CONTEXT_WINDOW` in `analyzer.py` to match your primary model.

**Q: Why does the report say I "wasted" tokens?**
A: "Waste" includes exploration, Q&A, and friction rework — not all are bad. Exploration builds knowledge; friction is iteration toward the right solution. The report flags them so you can decide if they're valuable.

## Contributing

Found a bug? Have ideas for new metrics? Open an issue or PR!

## License

MIT — use, modify, share freely.

---

**Made for Claude Code users who want to understand their token efficiency at a glance.**
