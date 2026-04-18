#!/usr/bin/env python3
"""Claude token efficiency analyzer — 3 solid metrics, one-screen dashboard."""

import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CLAUDE_DIR = Path.home() / ".claude"
CONTEXT_WINDOW = 200_000  # Sonnet 4.6


def load_stats_cache():
    path = CLAUDE_DIR / "stats-cache.json"
    return json.loads(path.read_text()) if path.exists() else {}


def load_session_metas():
    pattern = str(CLAUDE_DIR / "usage-data" / "session-meta" / "*.json")
    metas = []
    for p in sorted(glob.glob(pattern)):
        try:
            metas.append(json.loads(Path(p).read_text()))
        except Exception:
            pass
    return sorted(metas, key=lambda m: m.get("start_time", ""))


def calc_cache_hit_rate(stats):
    """Calculate overall cache hit rate."""
    total_input = sum(u.get("inputTokens", 0) for u in stats.get("modelUsage", {}).values())
    total_cache_read = sum(u.get("cacheReadInputTokens", 0) for u in stats.get("modelUsage", {}).values())
    total = total_input + total_cache_read
    return (total_cache_read / total * 100) if total > 0 else 0


def calc_capacity_utilization(metas):
    """Calculate how much of available context window was used."""
    total_available = len(metas) * CONTEXT_WINDOW
    total_used = sum(
        m.get("input_tokens", 0) + m.get("output_tokens", 0)
        for m in metas
    )
    return (total_used / total_available * 100) if total_available > 0 else 0, total_used, total_available


def calc_session_stats(metas):
    """Calculate raw session statistics."""
    if not metas:
        return 0, 0, 0, 0
    tokens = [m.get("input_tokens", 0) + m.get("output_tokens", 0) for m in metas]
    return min(tokens), max(tokens), sum(tokens) // len(tokens), len(metas)


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d (%a)")
    except Exception:
        return iso[:10] if iso else "?"


def make_bar(pct, width=20):
    """Create a simple bar chart (e.g., 50% -> ██████░░░░)."""
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def verdict_cache(rate):
    if rate > 85:
        return "EXCELLENT"
    elif rate > 60:
        return "GOOD"
    else:
        return "LOW"


def verdict_capacity(rate):
    if rate > 70:
        return "HIGH"
    elif rate > 30:
        return "MODERATE"
    else:
        return "LOW"




def print_report(stats, metas):
    if not metas:
        print("No session data found. Run Claude Code a few times first!")
        return

    cache_rate = calc_cache_hit_rate(stats)
    capacity_pct, tokens_used, capacity_total = calc_capacity_utilization(metas)
    min_tokens, max_tokens, avg_tokens, session_count = calc_session_stats(metas)

    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║           CLAUDE CODE TOKEN USAGE                            ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")

    bar1 = make_bar(cache_rate, 20)
    print(f"CACHE HIT RATE:        {cache_rate:5.1f}%  {bar1}  {verdict_cache(cache_rate)}")
    print("                       (Context reused across sessions)\n")

    bar2 = make_bar(capacity_pct, 20)
    print(f"CAPACITY USED:         {capacity_pct:5.1f}%  {bar2}  {verdict_capacity(capacity_pct)}")
    print(f"                       ({fmt_tokens(tokens_used)} of {fmt_tokens(capacity_total)} available)\n")

    print("═══════════════════════════════════════════════════════════════\n")
    print("SESSION BREAKDOWN:\n")
    print(f"  Sessions:            {session_count}")
    print(f"  Avg tokens/session:  {fmt_tokens(avg_tokens)}")
    print(f"  Min tokens:          {fmt_tokens(min_tokens)}")
    print(f"  Max tokens:          {fmt_tokens(max_tokens)}\n")

    print("RECENT ACTIVITY:\n")
    for meta in metas[-7:]:
        date = fmt_date(meta.get("start_time", ""))
        tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
        print(f"  {date:<20}  {fmt_tokens(tokens):>7}")

    print("\n" + "═" * 63)
    print("⚠️  Claude Code sessions only — VS Code sessions not tracked\n")

    if capacity_pct < 30:
        print(f"💡 You're using only {capacity_pct:.0f}% of context window.")
        print("   Batch related tasks into longer sessions to improve cache reuse.")
    elif cache_rate < 60:
        print(f"💡 Cache reuse is low ({cache_rate:.0f}%).")
        print("   Keep related projects in the same session for better efficiency.")
    else:
        print("✓ STRONG CACHE REUSE: Context is being leveraged across sessions.")

    print()


if __name__ == "__main__":
    stats = load_stats_cache()
    metas = load_session_metas()
    print_report(stats, metas)
