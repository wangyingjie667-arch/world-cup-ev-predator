#!/usr/bin/env python3
"""
⚡ EV PREDATOR ⚡ — value-betting engine for 体彩竞彩足球 (China Sports Lottery soccer).
Developed by JASON WANG.

Core idea: 体彩 is a high-margin "soft" book. The sharp market (Polymarket /
Betfair Exchange / Pinnacle/PS3838) is the true-probability anchor. We compute the
EV of every outcome (主胜/平/客胜) of every match, find where 体彩's margin is
thinnest, and (optionally) size a SINGLES-ONLY portfolio under a hard bankroll cap,
printing the full profit/loss distribution.

----------------------------------------------------------------------------------
USAGE
    python ev_predator.py matches.json [--bankroll 100]

matches.json:
{
  "matches": [
    {
      "name": "日本 vs 瑞典",
      "tiyancai": {"home": 1.61, "draw": 3.57, "away": 4.25},     # 体彩 主胜/平/客胜 decimal odds
      "true_prob": {"home": 0.509, "draw": 0.28, "away": 0.212},  # sharp probs (sum ~1)
      "source": "Polymarket live 21:45 + Betfair x-check"         # REQUIRED: provenance
    }
  ],
  // OPTIONAL: an explicit staking plan -> triggers the portfolio distribution.
  "bets": [
    {"label": "日本-瑞典 平", "odds": 3.57, "prob": 0.28, "stake": 40},
    {"label": "厄瓜多尔-德国 平", "odds": 4.90, "prob": 0.20, "stake": 30},
    {"label": "乌拉圭-西班牙 平", "odds": 4.22, "prob": 0.23, "stake": 30}
  ]
}

Instead of "true_prob" a match may give the sharp side as odds; it will be de-vigged:
    "true_odds": {"home": 1.93, "draw": 3.70, "away": 4.60}

Honest note: 体彩 is long-run negative EV. This tool minimizes the margin paid and
shapes the variance; it does not make a losing game winning.
----------------------------------------------------------------------------------
"""
import json
import sys
import argparse
from itertools import product

OUTCOMES = ["home", "draw", "away"]
ZH = {"home": "主胜", "draw": "平 ", "away": "客胜"}


def devig(odds):
    """Normalize 1/odds across outcomes -> implied true probabilities (margin removed)."""
    raw = {k: 1.0 / v for k, v in odds.items()}
    s = sum(raw.values())
    return {k: raw[k] / s for k in raw}, s - 1.0  # probs, overround


def true_probs(match):
    if "true_prob" in match:
        p = match["true_prob"]
        s = sum(p.values())
        return {k: p[k] / s for k in p}  # renormalize defensively
    if "true_odds" in match:
        p, _ = devig(match["true_odds"])
        return p
    raise ValueError(f"match '{match.get('name')}' needs true_prob or true_odds")


def scan(matches):
    """Per-outcome EV table; returns the best (highest-EV) line per match."""
    print("=" * 68)
    print("  逐场 EV 扫描  (EV = 真值概率 × 体彩赔率 − 1)")
    print("=" * 68)
    bests = []
    for m in matches:
        o = m["tiyancai"]
        p = true_probs(m)
        _, ov = devig(o)
        print(f"\n● {m['name']}    [体彩总水位 ≈ {ov*100:4.1f}%]")
        print(f"  真值来源: {m.get('source', '⚠️ 未标注来源!')}")
        rows = []
        for k in OUTCOMES:
            ev = p[k] * o[k] - 1.0
            rows.append((k, ev))
            print(f"    {ZH[k]}  体彩 {o[k]:>5.2f}   真值 {p[k]*100:4.1f}%   "
                  f"EV {ev*100:+6.1f}%")
        best = max(rows, key=lambda r: r[1])
        tag = "✅ 可下" if best[1] > 0 else ("🟡 临界" if best[1] > -0.03 else "🔴 全场都不该碰")
        print(f"  → 最薄水位: {ZH[best[0]].strip()}  (EV {best[1]*100:+.1f}%)  {tag}")
        bests.append({"match": m["name"], "outcome": best[0],
                      "odds": o[best[0]], "prob": p[best[0]], "ev": best[1]})
    return bests


def portfolio(bets):
    """Enumerate all 2^n win/lose combinations of independent SINGLES."""
    n = len(bets)
    total = sum(b["stake"] for b in bets)
    scenarios = []
    for combo in product([0, 1], repeat=n):  # 0=lose, 1=win, per leg
        prob = 1.0
        ret = 0.0
        hits = []
        for bit, b in zip(combo, bets):
            if bit:
                prob *= b["prob"]
                ret += b["stake"] * b["odds"]
                hits.append(b["label"])
            else:
                prob *= (1.0 - b["prob"])
        scenarios.append({"prob": prob, "ret": ret, "net": ret - total,
                          "hits": hits, "k": sum(combo)})
    ev = sum(s["prob"] * s["net"] for s in scenarios)
    p_profit = sum(s["prob"] for s in scenarios if s["net"] > 1e-9)
    p_loseall = sum(s["prob"] for s in scenarios if s["ret"] < 1e-9)
    best = max(scenarios, key=lambda s: s["net"])
    worst = min(scenarios, key=lambda s: s["net"])

    print("\n" + "=" * 68)
    print(f"  下注单 — 总额 {total:.0f} 元 · 单关 (singles only)")
    print("=" * 68)
    for b in bets:
        single_ev = b["prob"] * b["odds"] - 1.0
        print(f"  {b['label']:<22} 押@{b['odds']:>5.2f}  注 {b['stake']:>5.1f}  "
              f"中{b['prob']*100:4.1f}%  拿回{b['stake']*b['odds']:>6.1f}  "
              f"EV {single_ev*100:+5.1f}%")

    print("\n  【整单盈亏分布 · 按命中张数归类】")
    by_k = {}
    for s in scenarios:
        by_k.setdefault(s["k"], {"prob": 0.0, "nets": []})
        by_k[s["k"]]["prob"] += s["prob"]
        by_k[s["k"]]["nets"].append(s["net"])
    for k in sorted(by_k):
        d = by_k[k]
        lo, hi = min(d["nets"]), max(d["nets"])
        rng = f"{lo:+.0f}" if abs(hi - lo) < 1e-6 else f"{lo:+.0f} ~ {hi:+.0f}"
        print(f"    中 {k} 张   概率 {d['prob']*100:5.1f}%   净盈亏 {rng}")

    print("\n  【关键数字】")
    print(f"    赚钱概率 : {p_profit*100:5.1f}%")
    print(f"    全损概率 : {p_loseall*100:5.1f}%")
    print(f"    期望盈亏 : {ev:+.1f} 元  ({ev/total*100:+.1f}%)")
    print(f"    最好     : {best['net']:+.0f} 元  ({'+'.join(best['hits']) or '无'})")
    print(f"    最坏     : {worst['net']:+.0f} 元")
    print("\n  ⚠️ 体彩长期负EV。本单只是把成本压到最低、上限焊死。赔率会动，下单前App核对。")
    return {"ev": ev, "p_profit": p_profit, "p_loseall": p_loseall,
            "total": total, "best": best["net"], "worst": worst["net"]}


def main():
    ap = argparse.ArgumentParser(description="⚡ EV PREDATOR ⚡ by JASON WANG")
    ap.add_argument("json_file", help="matches.json (see header for format)")
    ap.add_argument("--bankroll", type=float, default=None,
                    help="total stake; if no explicit 'bets', flat-split across best lines")
    args = ap.parse_args()

    with open(args.json_file, encoding="utf-8") as f:
        data = json.load(f)

    matches = data.get("matches", [])
    if matches:
        bests = scan(matches)

    bets = data.get("bets")
    # If no explicit bets but a bankroll is given, auto-build a flat-split portfolio
    # from the least-bad line of each match (Mode B default).
    if not bets and args.bankroll and matches:
        playable = bests  # one line per match; user can prune in the JSON next time
        stake = args.bankroll / len(playable)
        bets = [{"label": f"{b['match']} {ZH[b['outcome']].strip()}",
                 "odds": b["odds"], "prob": b["prob"], "stake": stake}
                for b in playable]
        print(f"\n(自动用每场最薄水位线、平分 {args.bankroll:.0f} 元建仓；"
              f"真正下注前请人工删掉EV太差的场次)")

    if bets:
        portfolio(bets)
    elif not matches:
        print("JSON 里既无 matches 也无 bets。见文件头格式说明。")


if __name__ == "__main__":
    main()
