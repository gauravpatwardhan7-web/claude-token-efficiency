#!/usr/bin/env python3
"""Claude Code token efficiency analyzer — focus on wasted context window."""

import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

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


def calc_efficiency_metrics(metas):
    """Calculate tokens used, wasted, and efficiency per session."""
    sessions = []
    total_available = len(metas) * CONTEXT_WINDOW
    total_used = 0
    total_wasted = 0

    for meta in metas:
        used = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
        wasted = CONTEXT_WINDOW - used
        efficiency = (used / CONTEXT_WINDOW * 100) if CONTEXT_WINDOW > 0 else 0

        sessions.append({
            "date": fmt_date(meta.get("start_time", "")),
            "used": used,
            "wasted": wasted,
            "efficiency": efficiency,
            "start_time": meta.get("start_time", "")
        })
        total_used += used
        total_wasted += wasted

    overall_efficiency = (total_used / total_available * 100) if total_available > 0 else 0
    return sessions, total_used, total_wasted, overall_efficiency


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso[:10] if iso else "?"


def make_bar(pct, width=20):
    """Create a bar showing used (filled) vs unused (empty) tokens."""
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def generate_chart(sessions):
    """Generate a visualization of token usage per session."""
    if not HAS_MATPLOTLIB:
        return None

    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Chart 1: Used vs Wasted tokens per session
        dates = [s["date"] for s in sessions]
        used = [s["used"] / 1000 for s in sessions]  # Convert to K
        wasted = [s["wasted"] / 1000 for s in sessions]

        x = range(len(sessions))
        ax1.bar(x, used, label="Used", color="#2ecc71", alpha=0.8)
        ax1.bar(x, wasted, bottom=used, label="Wasted", color="#e74c3c", alpha=0.6)
        ax1.set_ylabel("Tokens (K)")
        ax1.set_xlabel("Session")
        ax1.set_title("Token Usage per Session: Used vs Wasted")
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45, ha="right", fontsize=8)
        ax1.legend()
        ax1.grid(axis="y", alpha=0.3)

        # Chart 2: Efficiency percentage per session
        efficiency = [s["efficiency"] for s in sessions]
        colors = ["#2ecc71" if e > 50 else "#f39c12" if e > 30 else "#e74c3c" for e in efficiency]
        ax2.bar(x, efficiency, color=colors, alpha=0.8)
        ax2.axhline(y=50, color="orange", linestyle="--", label="50% threshold", alpha=0.5)
        ax2.axhline(y=30, color="red", linestyle="--", label="30% threshold", alpha=0.5)
        ax2.set_ylabel("Efficiency (%)")
        ax2.set_xlabel("Session")
        ax2.set_title("Window Utilization per Session")
        ax2.set_xticks(x)
        ax2.set_xticklabels(dates, rotation=45, ha="right", fontsize=8)
        ax2.set_ylim(0, 105)
        ax2.legend()
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig("graphify-out/token_efficiency.png", dpi=150, bbox_inches="tight")
        return "graphify-out/token_efficiency.png"
    except Exception as e:
        print(f"Warning: Could not generate chart: {e}")
        return None


def print_report(stats, metas):
    if not metas:
        print("No session data found. Run Claude Code a few times first!")
        return

    cache_rate = calc_cache_hit_rate(stats)
    sessions, total_used, total_wasted, overall_eff = calc_efficiency_metrics(metas)

    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║        CLAUDE CODE TOKEN EFFICIENCY — WASTED CAPACITY         ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")

    print(f"CACHE HIT RATE:        {cache_rate:5.1f}%")
    print("                       (Context reused across sessions)\n")

    print(f"OVERALL EFFICIENCY:    {overall_eff:5.1f}%  {make_bar(overall_eff)}")
    print(f"                       ({fmt_tokens(total_used)} used, {fmt_tokens(total_wasted)} wasted)\n")

    print("═══════════════════════════════════════════════════════════════\n")
    print("SESSIONS (sorted by waste):\n")

    sorted_sessions = sorted(sessions, key=lambda s: s["wasted"], reverse=True)
    for i, s in enumerate(sorted_sessions, 1):
        bar = make_bar(s["efficiency"])
        print(f"  {i}. {s['date']:<12}  {s['efficiency']:5.1f}%  {bar}  {fmt_tokens(s['used']):>7} used, {fmt_tokens(s['wasted']):>7} wasted")

    print("\n" + "═" * 63)
    print("⚠️  Claude Code sessions only — VS Code sessions not tracked\n")

    # Recommendations
    worst_waste_pct = max(s["efficiency"] for s in sessions) if sessions else 0
    best_waste_pct = min(s["efficiency"] for s in sessions) if sessions else 0
    avg_waste_pct = overall_eff

    if best_waste_pct < 30:
        print("💡 CRITICAL: You're running mostly short sessions.")
        print(f"   Combine related work into fewer, longer sessions to use more of the {fmt_tokens(CONTEXT_WINDOW)} window.")
        print(f"   Example: {fmt_tokens(total_wasted)} tokens wasted across {len(sessions)} sessions could have been another few hours of work.\n")
    elif avg_waste_pct < 50:
        print(f"💡 OPPORTUNITY: Average session uses only {avg_waste_pct:.0f}% of the window.")
        print(f"   Batch tasks together — you're leaving {fmt_tokens(total_wasted)} tokens on the table.")
        print(f"   That's equivalent to ~{total_wasted // 5000} 'lost sessions' of productive work.\n")
    else:
        print("✓ GOOD BATCHING: You're using context windows well.")
        print(f"   You're capturing most of the available capacity. Keep batching related work.\n")

    # Generate visualization
    if HAS_MATPLOTLIB:
        chart_path = generate_chart(sessions)
        if chart_path:
            print(f"📊 Visualization saved to: {chart_path}")
    else:
        print("📊 (Install matplotlib for token efficiency charts: pip install matplotlib)")

    print()


if __name__ == "__main__":
    stats = load_stats_cache()
    metas = load_session_metas()
    print_report(stats, metas)
