# Repository Index

Everything you need to know about the Claude Token Efficiency Analyzer — in one place.

## Quick Navigation

| I want to... | Read this |
|--------------|-----------|
| **Get started** | [INSTALL.md](INSTALL.md) — 3 installation methods |
| **Understand the skill** | [README.md](README.md) — full overview + FAQ |
| **Use the skill** | [SKILL.md](SKILL.md) — technical docs for Claude Code |
| **See an example** | [examples/sample_output.txt](examples/sample_output.txt) — real report output |
| **Contribute code** | [CONTRIBUTING.md](CONTRIBUTING.md) — how to submit PRs |
| **Track changes** | [CHANGELOG.md](CHANGELOG.md) — version history + roadmap |

## Files at a Glance

```
claude-token-efficiency/
├── README.md                    ← Start here
├── INSTALL.md                   ← Installation instructions
├── SKILL.md                     ← Claude Code skill definition
├── analyzer.py                  ← The actual script (22KB)
├── CONTRIBUTING.md              ← How to help improve this
├── CHANGELOG.md                 ← Version history
├── LICENSE                      ← MIT license
├── .gitignore                   ← Git ignore patterns
├── .github/
│   └── workflows/
│       └── test.yml             ← CI/CD (syntax checks)
└── examples/
    └── sample_output.txt        ← Real report example
```

## Key Sections Explained

### For Users

1. **Installation** (2 min) → [INSTALL.md](INSTALL.md)
   - Copy 2 files to `~/.claude/skills/token-efficiency/`
   - Done!

2. **How to Use** (1 min) → [README.md](README.md) + [SKILL.md](SKILL.md)
   - Type `/token-efficiency` in Claude Code
   - Read the report

3. **Understanding Results** (5 min) → [README.md](README.md#interpreting-your-report)
   - What do the numbers mean?
   - How to improve your efficiency

### For Developers

1. **Code Walkthrough** → [analyzer.py](analyzer.py) (heavily commented)
   - ~700 lines of pure Python
   - 9 major functions: load data, classify, calculate, visualize, report

2. **Contributing** → [CONTRIBUTING.md](CONTRIBUTING.md)
   - Bug reports, feature requests, PRs

3. **CI/CD** → [.github/workflows/test.yml](.github/workflows/test.yml)
   - Runs on Python 3.7–3.12, macOS/Linux/Windows
   - Syntax checks on every PR

## What This Does

The analyzer reads local data that Claude Code writes automatically:
- `~/.claude/stats-cache.json` — token aggregates
- `~/.claude/usage-data/session-meta/*.json` — session details
- `~/.claude/usage-data/facets/*.json` — goal outcomes

And prints a multi-section dashboard:

1. **Overview** — total tokens, cache hit rate, cost
2. **Heatmap** — activity patterns (visual)
3. **Session Breakdown** — detailed table
4. **Waste Analysis** — inefficiency detection
5. **Context Utilization** — % of 200K cap used
6. **Unused Capacity** — untapped potential
7. **Monthly Summary** — trends
8. **Efficiency Metrics** — ratios and rates
9. **Potential vs Achieved** — goal success rate

## Installation (TL;DR)

```bash
mkdir -p ~/.claude/skills/token-efficiency && \
curl -sL https://raw.githubusercontent.com/yourusername/claude-token-efficiency/main/{SKILL.md,analyzer.py} \
  -o ~/.claude/skills/token-efficiency/#1
```

Then in Claude Code:
```
/token-efficiency
```

## Common Questions

**Q: What's the difference between these docs?**

- `README.md` — User guide (what it does, how to interpret results)
- `SKILL.md` — Claude Code integration (for the skill framework)
- `INSTALL.md` — Setup instructions (multiple methods)
- `CONTRIBUTING.md` — Developer guide (how to improve it)
- `CHANGELOG.md` — Release notes + roadmap

**Q: Can I use this if I don't have any sessions yet?**

Yes, but you'll get an empty report. The script is safe to run anytime.

**Q: Where can I report bugs?**

Open an issue on GitHub: [yourusername/claude-token-efficiency/issues](https://github.com/yourusername/claude-token-efficiency/issues)

**Q: Can I customize the metrics?**

Yes! Edit the constants in `analyzer.py`:
- `PRICING` — update when Anthropic changes rates
- `CONTEXT_WINDOW` — change for different models
- `SEP` — adjust separator line width

**Q: Is this official from Anthropic?**

No, this is a community skill. But it reads only local data — no risk.

## Roadmap

See [CHANGELOG.md](CHANGELOG.md#unreleased) for planned features.

High-priority items:
- [ ] Interactive HTML reports
- [ ] Trend analysis (month-over-month)
- [ ] CSV export for spreadsheets
- [ ] Per-project breakdown

## License

MIT — use, fork, share freely. See [LICENSE](LICENSE).

---

**Ready to get started?** → [INSTALL.md](INSTALL.md)

**Have an idea to improve this?** → [CONTRIBUTING.md](CONTRIBUTING.md)
