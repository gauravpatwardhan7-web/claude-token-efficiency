#!/usr/bin/env python3
"""Claude token efficiency analyzer — reads ~/.claude/ data and prints a report."""

import json
import glob
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

CLAUDE_DIR = Path.home() / ".claude"
CONTEXT_WINDOW = 200_000  # Claude Sonnet 4.6 input context

# Pricing per million tokens (April 2026)
PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.0, "output": 15.0, "cache_read": 0.30, "cache_write": 3.75,
    },
    "claude-haiku-4-5-20251001": {
        "input": 0.80, "output": 4.0, "cache_read": 0.08, "cache_write": 1.0,
    },
}
DEFAULT_PRICING = {"input": 3.0, "output": 15.0, "cache_read": 0.30, "cache_write": 3.75}

SEP = "─" * 80


def load_stats_cache():
    path = CLAUDE_DIR / "stats-cache.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_session_metas():
    pattern = str(CLAUDE_DIR / "usage-data" / "session-meta" / "*.json")
    metas = []
    for p in sorted(glob.glob(pattern)):
        try:
            metas.append(json.loads(Path(p).read_text()))
        except Exception:
            pass
    return sorted(metas, key=lambda m: m.get("start_time", ""))


def load_facets():
    pattern = str(CLAUDE_DIR / "usage-data" / "facets" / "*.json")
    facets = {}
    for p in glob.glob(pattern):
        try:
            data = json.loads(Path(p).read_text())
            facets[data["session_id"]] = data
        except Exception:
            pass
    return facets


def classify_session(meta):
    tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
    lines = meta.get("lines_added", 0) + meta.get("lines_removed", 0)
    files = meta.get("files_modified", 0)
    tool_calls = sum(meta.get("tool_counts", {}).values())

    if tokens == 0:
        return "EMPTY"
    if lines > 0 or files > 0:
        return "PRODUCTIVE"
    if tool_calls > 0:
        return "EXPLORING"
    return "CONVERSATION"


def estimate_cost(model_usage):
    total = 0.0
    breakdown = {}
    for model, usage in model_usage.items():
        p = PRICING.get(model, DEFAULT_PRICING)
        cost = (
            usage.get("inputTokens", 0) / 1e6 * p["input"]
            + usage.get("outputTokens", 0) / 1e6 * p["output"]
            + usage.get("cacheReadInputTokens", 0) / 1e6 * p["cache_read"]
            + usage.get("cacheCreationInputTokens", 0) / 1e6 * p["cache_write"]
        )
        breakdown[model] = cost
        total += cost
    return total, breakdown


def calc_cache_hit_rate(usage):
    reads = usage.get("cacheReadInputTokens", 0)
    inputs = usage.get("inputTokens", 0)
    total = reads + inputs
    return reads / total if total > 0 else 0.0


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return iso[:10] if iso else "?"


def short_project(path):
    if not path:
        return "unknown"
    return Path(path).name or path


def print_activity_graph(daily_activity, daily_model_tokens, metas):
    """Print two side-by-side heatmaps: token intensity + productivity quality."""
    # ANSI colours
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    GREY   = "\033[90m"
    RESET  = "\033[0m"

    token_by_day = {}
    for entry in daily_model_tokens:
        token_by_day[entry["date"]] = sum(entry.get("tokensByModel", {}).values())

    msg_by_day = {}
    for entry in daily_activity:
        msg_by_day[entry["date"]] = entry.get("messageCount", 0)

    # Best session type per day (PRODUCTIVE > EXPLORING > CONVERSATION > EMPTY)
    TYPE_RANK = {"PRODUCTIVE": 4, "EXPLORING": 3, "CONVERSATION": 2, "EMPTY": 1}
    prod_by_day = {}
    for m in metas:
        d = fmt_date(m.get("start_time", ""))
        stype = classify_session(m)
        if d not in prod_by_day or TYPE_RANK.get(stype, 0) > TYPE_RANK.get(prod_by_day[d], 0):
            prod_by_day[d] = stype

    all_dates = sorted(set(list(token_by_day.keys()) + list(prod_by_day.keys())))
    if not all_dates:
        return

    start = datetime.strptime(all_dates[0], "%Y-%m-%d")
    end   = datetime.strptime(all_dates[-1], "%Y-%m-%d")
    while start.weekday() != 0:
        start -= timedelta(days=1)
    while end.weekday() != 6:
        end += timedelta(days=1)

    max_tok = max(token_by_day.values()) if token_by_day else 1
    SHADES = ["·", "░", "▒", "▓", "█"]

    def intensity_cell(tok):
        if tok == 0:
            return GREY + "·" + RESET
        level = int((tok / max_tok) * (len(SHADES) - 1))
        return SHADES[max(1, level)]

    def productivity_cell(d):
        stype = prod_by_day.get(d)
        if stype is None:
            return GREY + "·" + RESET
        if stype == "PRODUCTIVE":
            return GREEN + "█" + RESET
        if stype == "EXPLORING":
            return YELLOW + "▒" + RESET
        if stype == "CONVERSATION":
            return YELLOW + "░" + RESET
        return RED + "·" + RESET  # EMPTY — session opened, nothing done

    # Build week grid
    weeks = []
    cur = start
    while cur <= end:
        week = []
        for _ in range(7):
            week.append(cur.strftime("%Y-%m-%d"))
            cur += timedelta(days=1)
        weeks.append(week)

    days_label = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def month_header(weeks):
        parts = ["    "]
        prev = None
        for week in weeks:
            m = datetime.strptime(week[0], "%Y-%m-%d").strftime("%b")
            parts.append(f"{m:<3}" if m != prev else "   ")
            prev = m
        return "  " + " ".join(parts[1:])

    gap = "      "  # space between the two grids

    print(f"\n{SEP}")
    print("  ACTIVITY HEATMAP")
    print(SEP)
    print(f"  Token intensity              {gap}  Productivity quality")
    print(f"  · none ░ light ▒ med ▓ heavy {gap}  {GREEN}█{RESET} productive  {YELLOW}▒{RESET} exploring/chat  {RED}·{RESET} empty session")
    print()

    hdr = month_header(weeks)
    print(f"  {hdr}   {gap}  {hdr}")

    for day_idx in range(7):
        lbl = days_label[day_idx]
        left = right = ""
        for week in weeks:
            d = week[day_idx]
            tok = token_by_day.get(d, 0)
            left  += intensity_cell(tok) + "  "
            right += productivity_cell(d) + "  "
        print(f"  {lbl} {left}  {gap}  {lbl} {right}")

    # Bar chart — only active days
    active_days = [(d, t) for d, t in sorted(token_by_day.items()) if t > 0]
    if active_days:
        print(f"\n  Token volume per active day:")
        bar_max = max(t for _, t in active_days)
        bar_width = 38
        for d, t in active_days:
            msgs   = msg_by_day.get(d, 0)
            stype  = prod_by_day.get(d, "")
            if stype == "PRODUCTIVE":
                color = GREEN
            elif stype in ("EXPLORING", "CONVERSATION"):
                color = YELLOW
            elif stype == "EMPTY":
                color = RED
            else:
                color = GREY  # token data exists but no session meta for this date
            bar_len = max(1, int(t / bar_max * bar_width))
            bar    = color + "█" * bar_len + RESET
            label  = stype if stype else "no session meta"
            print(f"    {d}  {bar:<{bar_width + 10}}  {fmt_tokens(t):>7}  {color}{label}{RESET}  ({msgs} msgs)")


def print_report(stats, metas, facets):
    model_usage = stats.get("modelUsage", {})
    total_cost, cost_breakdown = estimate_cost(model_usage)

    all_input = sum(u.get("inputTokens", 0) for u in model_usage.values())
    all_output = sum(u.get("outputTokens", 0) for u in model_usage.values())
    all_cache_read = sum(u.get("cacheReadInputTokens", 0) for u in model_usage.values())
    all_cache_write = sum(u.get("cacheCreationInputTokens", 0) for u in model_usage.values())
    total_tokens = all_input + all_output + all_cache_read + all_cache_write

    daily = stats.get("dailyActivity", [])
    dates = [d["date"] for d in daily if d.get("date")]
    first_date = min(dates) if dates else "?"
    last_date = max(dates) if dates else "?"

    print(f"\n{'═'*80}")
    print("  CLAUDE TOKEN EFFICIENCY REPORT")
    print(f"{'═'*80}")
    print(f"  Period : {first_date}  →  {last_date}")
    print(f"  Sessions: {stats.get('totalSessions', len(metas))}   Messages: {stats.get('totalMessages', '?')}")
    print(f"\n  Token Usage (all models combined):")
    print(f"    Input tokens      : {fmt_tokens(all_input):>8}")
    print(f"    Output tokens     : {fmt_tokens(all_output):>8}")
    print(f"    Cache reads       : {fmt_tokens(all_cache_read):>8}  ← tokens served from cache (cheap)")
    print(f"    Cache writes      : {fmt_tokens(all_cache_write):>8}  ← tokens stored in cache")
    print(f"    ─────────────────────────────")

    combined_cache_hit = calc_cache_hit_rate(
        {"inputTokens": all_input, "cacheReadInputTokens": all_cache_read}
    )
    print(f"    Cache hit rate    : {combined_cache_hit*100:.1f}%  ({'excellent' if combined_cache_hit > 0.85 else 'good' if combined_cache_hit > 0.6 else 'low'})")
    print(f"\n  Estimated Cost     : ${total_cost:.4f} USD")
    for model, cost in cost_breakdown.items():
        label = model.split("-")[1].capitalize() + " " + model.split("-")[2]
        print(f"    {label:<30}: ${cost:.4f}")
    print(f"  (Rates: Sonnet $3/$15 in/out per MTok; Haiku $0.80/$4 in/out per MTok)")

    # ── Activity Heatmap ────────────────────────────────────────────────────
    print_activity_graph(stats.get("dailyActivity", []), stats.get("dailyModelTokens", []), metas)

    # ── 2. Session Breakdown ────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  SESSION BREAKDOWN")
    print(SEP)
    header = f"  {'Date':<12} {'Project':<22} {'Min':>4} {'Tokens':>8} {'Lines':>6} {'Type':<13} {'Outcome'}"
    print(header)
    print(f"  {'-'*12} {'-'*22} {'-'*4} {'-'*8} {'-'*6} {'-'*13} {'-'*20}")

    session_tokens_total = 0
    wasted_tokens = 0
    friction_tokens = 0
    productive_lines = 0
    productive_tokens = 0

    for meta in metas:
        sid = meta.get("session_id", "")
        date = fmt_date(meta.get("start_time", ""))
        project = short_project(meta.get("project_path", ""))[:22]
        dur = meta.get("duration_minutes", 0)
        tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
        lines = meta.get("lines_added", 0) + meta.get("lines_removed", 0)
        stype = classify_session(meta)
        facet = facets.get(sid, {})
        outcome = facet.get("outcome", "—")
        friction = sum(facet.get("friction_counts", {}).values())

        session_tokens_total += tokens

        if stype == "EMPTY":
            wasted_tokens += tokens
        elif stype == "CONVERSATION":
            wasted_tokens += tokens
        elif stype == "EXPLORING":
            wasted_tokens += tokens // 2  # partial credit

        if friction > 0:
            friction_tokens += int(tokens * 0.20)

        if stype == "PRODUCTIVE":
            productive_lines += lines
            productive_tokens += tokens

        friction_flag = " ⚠" if friction > 0 else ""
        outcome_str = (outcome + friction_flag)[:22]
        print(f"  {date:<12} {project:<22} {dur:>4} {fmt_tokens(tokens):>8} {lines:>6} {stype:<13} {outcome_str}")

    print()

    # ── 3. Waste Analysis ───────────────────────────────────────────────────
    effective_tokens = session_tokens_total - wasted_tokens
    waste_pct = (wasted_tokens / session_tokens_total * 100) if session_tokens_total > 0 else 0

    print(f"{SEP}")
    print("  WASTE ANALYSIS")
    print(SEP)
    print(f"  Total tokens in sessions : {fmt_tokens(session_tokens_total)}")
    print(f"  Effective (productive)   : {fmt_tokens(effective_tokens)}  ({100-waste_pct:.0f}%)")
    print(f"  Wasted (empty/chat/explore): {fmt_tokens(wasted_tokens)}  ({waste_pct:.0f}%)")
    print(f"  Friction rework estimate : {fmt_tokens(friction_tokens)}  (20% of sessions with wrong-approach friction)")
    total_waste = wasted_tokens + friction_tokens
    total_waste_pct = (total_waste / session_tokens_total * 100) if session_tokens_total > 0 else 0
    print(f"  ─────────────────────────────")
    print(f"  Total inefficiency       : {fmt_tokens(total_waste)}  ({total_waste_pct:.0f}% of tokens spent unproductively)")

    # ── 4. Context Window Utilization ───────────────────────────────────────
    print(f"\n{SEP}")
    print("  CONTEXT WINDOW UTILIZATION  (Sonnet 4.6 = 200K input cap)")
    print(SEP)
    print(f"  {'Session':<12} {'Tokens Used':>12} {'% of 200K cap':>15} {'Assessment'}")
    print(f"  {'-'*12} {'-'*12} {'-'*15} {'-'*20}")
    for meta in metas:
        date = fmt_date(meta.get("start_time", ""))
        tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
        pct = tokens / CONTEXT_WINDOW * 100
        if pct == 0:
            assessment = "EMPTY — nothing done"
        elif pct < 5:
            assessment = "Very light use"
        elif pct < 30:
            assessment = "Light use"
        elif pct < 70:
            assessment = "Moderate use"
        elif pct < 95:
            assessment = "Heavy use"
        else:
            assessment = "Near/at limit"
        print(f"  {date:<12} {fmt_tokens(tokens):>12} {pct:>14.1f}% {assessment}")

    # ── 5. Unused Capacity Analysis ─────────────────────────────────────────
    print(f"\n{SEP}")
    print("  UNUSED CAPACITY ANALYSIS  (How much context window you left on the table)")
    print(SEP)

    total_available = len(metas) * CONTEXT_WINDOW
    underutilized = []
    for meta in metas:
        tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
        if tokens > 0:
            unused = CONTEXT_WINDOW - tokens
            unused_pct = unused / CONTEXT_WINDOW * 100
            if unused_pct > 90:  # <10% of capacity used
                underutilized.append((fmt_date(meta.get("start_time", "")), tokens, unused_pct))

    print(f"  Total available capacity   : {fmt_tokens(total_available)}  ({len(metas)} sessions × {fmt_tokens(CONTEXT_WINDOW)} per session)")
    print(f"  Total tokens you used      : {fmt_tokens(session_tokens_total)}")
    print(f"  Total unused capacity      : {fmt_tokens(total_available - session_tokens_total)}")
    overall_util = (session_tokens_total / total_available * 100) if total_available > 0 else 0
    print(f"  ─────────────────────────────")
    print(f"  Overall utilization rate   : {overall_util:.1f}%")
    if overall_util < 30:
        verdict = "Low — you could tackle much more in each session"
    elif overall_util < 60:
        verdict = "Moderate — room to expand what you do per session"
    elif overall_util < 80:
        verdict = "Good — using context efficiently"
    else:
        verdict = "Excellent — pushing the context window well"
    print(f"  Verdict                    : {verdict}")

    if underutilized:
        print(f"\n  Severely under-utilized sessions (<10% of capacity used):")
        for date, tok, unused_pct in underutilized:
            print(f"    {date}  {fmt_tokens(tok):>7} used, {unused_pct:>5.0f}% unused")

    # ── 6. Monthly Summary ──────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  MONTHLY SUMMARY")
    print(SEP)

    monthly = defaultdict(lambda: {"days": set(), "sessions": 0, "messages": 0, "tokens": 0})
    for day in stats.get("dailyActivity", []):
        month = day["date"][:7]
        monthly[month]["days"].add(day["date"])
        monthly[month]["sessions"] += day.get("sessionCount", 0)
        monthly[month]["messages"] += day.get("messageCount", 0)

    for day in stats.get("dailyModelTokens", []):
        month = day["date"][:7]
        monthly[month]["tokens"] += sum(day.get("tokensByModel", {}).values())

    print(f"  {'Month':<10} {'Days':>5} {'Sessions':>9} {'Messages':>9} {'Tokens':>9} {'Est Cost':>10}")
    print(f"  {'-'*10} {'-'*5} {'-'*9} {'-'*9} {'-'*9} {'-'*10}")
    for month in sorted(monthly):
        m = monthly[month]
        # rough cost estimate: assume 70% sonnet, 30% haiku, no cache (conservative)
        tok = m["tokens"]
        rough_cost = tok / 1e6 * 3.0  # sonnet input rate as floor estimate
        print(f"  {month:<10} {len(m['days']):>5} {m['sessions']:>9} {m['messages']:>9} {fmt_tokens(tok):>9} {f'~${rough_cost:.4f}':>10}")

    # ── 7. Efficiency Metrics ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  EFFICIENCY METRICS")
    print(SEP)

    prod_sessions = [m for m in metas if classify_session(m) == "PRODUCTIVE"]
    if prod_sessions:
        ratios = []
        for m in prod_sessions:
            tokens = m.get("input_tokens", 0) + m.get("output_tokens", 0)
            lines = m.get("lines_added", 0) + m.get("lines_removed", 0)
            if lines > 0 and tokens > 0:
                ratios.append((tokens / lines, m))

        if ratios:
            best = min(ratios, key=lambda x: x[0])
            worst = max(ratios, key=lambda x: x[0])
            avg = sum(r[0] for r in ratios) / len(ratios)
            print(f"  Tokens per line of code changed:")
            print(f"    Best session   : {best[0]:,.0f} tok/line  ({fmt_date(best[1].get('start_time',''))} — {short_project(best[1].get('project_path',''))})")
            print(f"    Worst session  : {worst[0]:,.0f} tok/line  ({fmt_date(worst[1].get('start_time',''))} — {short_project(worst[1].get('project_path',''))})")
            print(f"    Your average   : {avg:,.0f} tok/line")

    all_tool_calls = sum(
        sum(m.get("tool_counts", {}).values()) for m in metas
    )
    all_messages = sum(m.get("user_message_count", 0) for m in metas)
    if all_tool_calls > 0:
        msg_tool_ratio = all_messages / all_tool_calls
        verdict = "Balanced" if msg_tool_ratio < 2 else "Talkative (more chat than action)"
        print(f"\n  Message-to-tool-call ratio: {msg_tool_ratio:.1f}  ({verdict})")

    empty_sessions = [m for m in metas if classify_session(m) == "EMPTY"]
    conv_sessions = [m for m in metas if classify_session(m) == "CONVERSATION"]
    print(f"\n  Session type breakdown:")
    print(f"    PRODUCTIVE    : {len(prod_sessions)} sessions  (code was written)")
    print(f"    EXPLORING     : {len([m for m in metas if classify_session(m) == 'EXPLORING'])} sessions  (tool calls, no code)")
    print(f"    CONVERSATION  : {len(conv_sessions)} sessions  (Q&A, no tools, no code)")
    print(f"    EMPTY         : {len(empty_sessions)} sessions  (0 tokens — abandoned/setup)")

    # ── 8. Potential vs Achieved ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  POTENTIAL vs ACHIEVED")
    print(SEP)

    if ratios:
        best_efficiency = best[0]  # tok/line for best session
        total_productive_tokens = sum(
            m.get("input_tokens", 0) + m.get("output_tokens", 0)
            for m in metas if classify_session(m) == "PRODUCTIVE"
        )
        potential_lines = total_productive_tokens / best_efficiency
        actual_lines = productive_lines

        print(f"  Best session efficiency   : {best_efficiency:,.0f} tokens per line changed")
        print(f"  Actual lines changed      : {actual_lines:,} lines")
        print(f"  Potential lines (at best) : {potential_lines:,.0f} lines")
        if potential_lines > 0:
            achievement_pct = actual_lines / potential_lines * 100
            print(f"  Achievement ratio         : {achievement_pct:.0f}%")

    if facets:
        outcomes = [f.get("outcome", "") for f in facets.values()]
        fully = outcomes.count("fully_achieved")
        mostly = outcomes.count("mostly_achieved")
        partial = outcomes.count("partially_achieved")
        not_ach = outcomes.count("not_achieved")
        total_f = len(outcomes)
        print(f"\n  Goal outcomes (from {total_f} rated sessions):")
        if fully:   print(f"    Fully achieved   : {fully}/{total_f}  ({fully/total_f*100:.0f}%)")
        if mostly:  print(f"    Mostly achieved  : {mostly}/{total_f}  ({mostly/total_f*100:.0f}%)")
        if partial: print(f"    Partially        : {partial}/{total_f}  ({partial/total_f*100:.0f}%)")
        if not_ach: print(f"    Not achieved     : {not_ach}/{total_f}  ({not_ach/total_f*100:.0f}%)")

        friction_sessions = [f for f in facets.values() if sum(f.get("friction_counts", {}).values()) > 0]
        if friction_sessions:
            print(f"\n  Sessions with friction (wrong approach / misunderstood):")
            for f in friction_sessions:
                sid = f.get("session_id", "")
                meta = next((m for m in metas if m.get("session_id") == sid), {})
                date = fmt_date(meta.get("start_time", ""))
                detail = f.get("friction_detail", "")[:60]
                print(f"    {date}: {detail}")

    print(f"\n{'═'*80}\n")


if __name__ == "__main__":
    stats = load_stats_cache()
    metas = load_session_metas()
    facets = load_facets()
    print_report(stats, metas, facets)
