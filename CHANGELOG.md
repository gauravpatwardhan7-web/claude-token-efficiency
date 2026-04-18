# Changelog

All notable changes to the Claude Token Efficiency Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-18

### Changed
- **Simplified to objective metrics only**: removed subjective "productive session" classification
- **Cache hit rate**: kept as reliable metric (% of tokens from cache)
- **Capacity utilization**: now clearly labeled as Claude Code sessions only, with disclaimer
- **Session statistics**: replaced productivity metrics with raw min/max/average token counts
- Removed cost estimation (not reliable for subscription-based plans)
- Removed activity heatmaps (requires subjective session classification)
- Removed waste/friction analysis (too speculative)
- Significantly reduced analyzer.py (160 lines, down from 200+)
- Updated all documentation to reflect honest, objective approach

### Why
User feedback: "Productivity is subjective to the user. Stick to hard facts and numbers."

### Benefits
- Clearer, more honest reporting
- No false precision about session quality
- Easier to understand and act on
- Matches what Claude Code actually tracks reliably

## [1.0.0] - 2026-04-18

### Added
- Initial release of Claude Token Efficiency Analyzer
- **Activity heatmap** with dual grids: token intensity + productivity quality
- **Token usage overview**: input, output, cache reads/writes, cost estimation
- **Session breakdown** with classification (PRODUCTIVE/EXPLORING/CONVERSATION/EMPTY)
- **Waste analysis**: empty sessions, friction rework estimation
- **Context window utilization**: per-session % of 200K cap used
- **Unused capacity analysis**: total available vs. used across all sessions
- **Monthly summary**: tokens and cost grouped by month
- **Efficiency metrics**: tokens per line, message-to-tool ratio, session type breakdown
- **Potential vs achieved**: goal outcomes and friction detection
- ANSI color support for terminal visualization
- Supports Sonnet 4.6 and Haiku models (pricing pre-configured)
- Pure Python implementation with no external dependencies
- Full documentation: README, INSTALL, CONTRIBUTE guides

### Features
- Reads local `~/.claude/` data — no API calls or auth required
- Zero pip dependencies — uses Python stdlib only
- Works on macOS, Linux, Windows
- Customizable pricing and context window constants
- Color-coded heatmap for quick visual analysis

## [Unreleased]

### Planned
- [ ] Interactive HTML report export
- [ ] Session-over-session trend analysis
- [ ] Per-project token breakdown
- [ ] CSV/JSON export for external analysis
- [ ] Cost projections for future usage
- [ ] Integration with GitHub PR/issue comments
- [ ] Slack webhook support for monthly summaries
- [ ] Multi-model cost comparison
- [ ] Custom date range filtering

### Future Ideas
- Web dashboard (cloud-hosted, optional)
- Team analytics (aggregate across users)
- Benchmarking (compare against community averages)
- ML-based productivity prediction
- Auto-suggestions for session batching
