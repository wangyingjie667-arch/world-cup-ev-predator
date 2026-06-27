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
    python ev_predator.py matches.json --sigma 0.01            # 加稳健值博线安全垫
    python ev_predator.py matches.json --goal double --target 2 # 搏翻倍 前沿 + ride 执行卡

值博线 / 盈亏比·胜率 (衡量"值不值得博", 已内置到每次扫描):
    盈亏比 b = 赢净赚/输净亏 = 赔率o − 1 ; 胜率 = p
    值得博(正EV) ⟺ p·b > 1−p ⟺ 盈亏比 b > (1−p)/p ⟺ 胜率×赔率 p·o > 1 ⟺ p > 1/o
    凯利下注比例 f* = (p·b−(1−p))/b = EV / 盈亏比     (≤0 就别下)
    稳健: dEV/dp = o → 胜率错1点 EV 放大 o 倍; 故要求 胜率 ≥ 1/o + k·σ_p (高赔腿安全垫更厚)
    低胜率也能值得博 —— 只要盈亏比 > (1−p)/p (例: 胜率17%配盈亏比>5 即过线)。
    体彩注定全在线下方(抽水); 这条线告诉你哪条最接近、以及任何非体彩的+EV机会该不该下。

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
from itertools import product, combinations

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


def value_line(p, o, sigma=0.0, k=1.0):
    """盈亏比/胜率「值博线」指标。
    定义: 盈亏比 b = 赢时净赚/输时净亏 = o-1; 胜率 = p。
    值得博(正EV) ⟺ p·b > 1-p ⟺ 盈亏比 b > (1-p)/p ⟺ 胜率×赔率 p·o > 1 ⟺ p > 1/o。
    凯利下注比例 f* = (p·b-(1-p))/b = EV/盈亏比。
    稳健性: dEV/dp = o, 胜率每错1点 EV 被放大 o 倍 → 高赔腿最不可信,
            需把回本胜率抬到 1/o + k·σ_p (σ_p=锐利源分歧)。
    """
    b = o - 1.0                                       # 盈亏比
    po = p * o                                        # 胜率×赔率 (>1 => 值得)
    ev = po - 1.0
    bstar = (1.0 - p) / p if p > 0 else float("inf")  # 回本盈亏比
    gap = b - bstar                                   # >0 => 过线(+EV)
    kelly = ev / b if b > 0 else 0.0                  # 凯利比例 = EV/盈亏比
    p_need_raw = 1.0 / o                              # 裸回本胜率
    p_need_robust = 1.0 / o + k * sigma               # 稳健回本胜率(加安全垫)
    ev_robust = ev - k * o * sigma                    # 稳健EV(误差经赔率放大)
    return {"b": b, "po": po, "ev": ev, "bstar": bstar, "gap": gap,
            "kelly": kelly, "p_need_raw": p_need_raw,
            "p_need_robust": p_need_robust, "ev_robust": ev_robust,
            "worth_raw": po > 1.0, "worth_robust": p >= p_need_robust}


def scan(matches, sigma=0.0, kappa=1.0):
    """逐场 EV + 值博线(盈亏比/胜率) 扫描; returns best (highest-EV) line per match."""
    print("=" * 78)
    print("  逐场扫描  EV=p·o−1 | 盈亏比 b=o−1 | 值博线: 胜率×赔率 p·o>1 (即 b>(1−p)/p)")
    if sigma > 0:
        print(f"  稳健值博线: 胜率 ≥ 1/赔率 + {kappa:g}·σ_p (σ_p={sigma:g}); 稳健EV = EV − {kappa:g}·赔率·σ_p")
    print("=" * 78)
    bests = []
    for m in matches:
        o = m["tiyancai"]
        p = true_probs(m)
        _, ov = devig(o)
        msig = m.get("sigma", sigma)
        sharp = m.get("sharp_prob", {})   # 可选: 锐利盘(Pinnacle/Betfair)去抽水胜率
        print(f"\n● {m['name']}    [体彩总水位 ≈ {ov*100:4.1f}%]")
        print(f"  真值来源: {m.get('source', '⚠️ 未标注来源!')}")
        print(f"  列: 庄=庄家胜率(1/赔率) 真=真值(Polymarket) 锐=锐利盘 盈亏比=赔率−1 缺口=距值博线 EV=真×赔−1")
        rows = []
        for key in OUTCOMES:
            vl = value_line(p[key], o[key], msig, kappa)
            rows.append((key, vl["ev"]))
            if not vl["worth_raw"]:
                verdict = "❌不值"
            elif msig > 0 and not vl["worth_robust"]:
                verdict = "🟡过裸线但欠安全垫"
            else:
                verdict = "✅值得"
            sp = sharp.get(key)
            sp_str = f"{sp*100:>4.1f}%" if isinstance(sp, (int, float)) else "  —  "
            print(f"    {ZH[key]}  赔{o[key]:>5.2f} 庄{vl['p_need_raw']*100:>4.1f}% "
                  f"真{p[key]*100:>4.1f}% 锐{sp_str} 盈亏比{vl['b']:>4.2f} "
                  f"缺口{vl['gap']:>+5.2f} EV{vl['ev']*100:>+6.1f}% Kelly{vl['kelly']*100:>+5.1f}% {verdict}")
        best = max(rows, key=lambda r: r[1])
        bo, bp = o[best[0]], p[best[0]]
        bvl = value_line(bp, bo, msig, kappa)
        tag = "✅ 可下" if best[1] > 0 else ("🟡 临界" if best[1] > -0.03 else "🔴 全场都不该碰")
        print(f"  → 最薄水位: {ZH[best[0]].strip()}  (EV {best[1]*100:+.1f}%, "
              f"庄{bvl['p_need_raw']*100:.1f}% vs 真{bp*100:.1f}%, 距值博线缺口 {bvl['gap']:+.2f})  {tag}")
        bests.append({"match": m["name"], "outcome": best[0],
                      "odds": bo, "prob": bp, "ev": best[1]})
    return bests


def goal_double(matches, bankroll=100.0, target_mult=2.0, sigma=0.0, kappa=1.0):
    """搏翻倍(下限=target_mult倍)+上探 前沿 + 'ride'(打底再滚)执行卡。
    单关一步要把本金B搏到 T=mult·B, 满注赢=B·o, 需 o≥mult; P(达标)=胜率p。
    ride: 用最高胜率腿满注打底→赢了锁住T、只用利润(B·o−T)滚一场高赔腿, 上不封顶。
    """
    target = bankroll * target_mult
    legs = []
    for m in matches:
        o = m["tiyancai"]
        p = true_probs(m)
        for key in OUTCOMES:
            legs.append({"match": m["name"], "key": key, "o": o[key], "p": p[key],
                         "sig": m.get("sigma", sigma)})
    cap = sorted([L for L in legs if L["o"] >= target_mult], key=lambda L: -L["p"])
    print("\n" + "=" * 78)
    print(f"  目标: {bankroll:.0f} 搏 {target_mult:g} 倍 (终值≥{target:.0f}) · 下限达标 + 上不封顶")
    print(f"  规则: 满注单关, o≥{target_mult:g}; 赢=本金×赔率, 概率=胜率; 输=0。串关叠抽水→不用。")
    print("=" * 78)
    if not cap:
        print(f"  没有 o≥{target_mult:g} 的腿, 单关一步达不了标。")
        return
    print(f"\n  【满注单关前沿】(按 P(达标) 高→低; 期望终值=本金·p·o)")
    print(f"  {'比赛':<15}{'押':<5}{'赔率':>6}{'P(达标)':>9}{'赢得':>7}{'期望终值':>9}{'胜×赔':>7}{'距线':>7}")
    for L in cap:
        vl = value_line(L["p"], L["o"], L["sig"], kappa)
        print(f"  {L['match'][:13]:<13}{ZH[L['key']].strip():<5}{L['o']:>6.2f}"
              f"{L['p']*100:>8.1f}%{bankroll*L['o']:>7.0f}{bankroll*L['p']*L['o']:>9.1f}"
              f"{vl['po']:>7.2f}{vl['gap']:>+7.2f}")
    print(f"\n  【打底 × 滚利润 组合】(打底满注锁达标 → 中了锁{target:.0f}、只滚利润 → 输了归零)")
    print(f"  第一行=翻倍胜算最高(但低赔→上探空间小); 往下=胜算略降、上探更大。按你偏好挑。")
    for fl in cap[:3]:
        fwin = bankroll * fl["o"]
        sp = fwin - target
        ride = max((L for L in cap if L["match"] != fl["match"]),
                   key=lambda L: L["o"], default=None)
        head = (f"\n  ● 打底 {fl['match']} {ZH[fl['key']].strip()}@{fl['o']:.2f} 满注{bankroll:.0f}"
                f" → {fl['p']*100:.1f}% 达标(拿{fwin:.0f}), {(1-fl['p'])*100:.1f}% 归零")
        if sp <= 1e-6 or ride is None:
            print(head + f"; 无利润可滚, 期望终值 {fl['p']*fwin:.1f}")
            continue
        rwin = target + sp * ride["o"]
        p_floor = fl["p"] * (1 - ride["p"])
        p_big = fl["p"] * ride["p"]
        efinal = p_floor * target + p_big * rwin
        print(head)
        print(f"      滚 {ride['match']} {ZH[ride['key']].strip()}@{ride['o']:.2f} (利润{sp:.0f}): "
              f"{(1-fl['p'])*100:.1f}%归零 | {p_floor*100:.1f}%落{target:.0f} | "
              f"{p_big*100:.1f}%落{rwin:.0f}({rwin/bankroll:.1f}x) | 期望终值{efinal:.1f}")
    print("\n  ⚠️ 全是负EV, 归零概率=搏翻倍的门票钱。单关不串关; 高赔腿赛前重扫锐利盘(填 σ)。")


def goal_reach(matches, bankroll=50.0, target_mult=2.0, sigma=0.0, kappa=1.0, pfloor=0.05):
    """枚举 单关 + 2串 + 3串(不同场才能串), 按 P(达标) 与水位排出前沿。
    P(达标)=Π真值; 总赔率=Π体彩赔率; 水位=1−P(达标)×总赔率。这是"今天怎么买"的主力。
    末尾强制打印"稳 vs 冲"对照: 最高P(达标)的稳注 vs 博上限注, 摊出为冲上限放弃多少命中率。
    """
    def leg_name(name, key):
        base = name.split("(")[0].strip()
        parts = base.split(" vs ")
        if len(parts) != 2:
            return f"{base[:6]}{ZH[key].strip()}"
        home, away = parts[0].strip()[:6], parts[1].strip()[:6]
        return {"home": f"{home}胜", "draw": f"{home}-{away}平", "away": f"{away}胜"}[key]

    legs = []
    for m in matches:
        o = m["tiyancai"]
        p = true_probs(m)
        for key in OUTCOMES:
            legs.append({"m": m["name"], "leg": leg_name(m["name"], key),
                         "o": o[key], "p": p[key]})

    def paths(n):
        out = []
        for c in combinations(legs, n):
            if len({x["m"] for x in c}) < n:    # 必须不同场才能串
                continue
            O = P = 1.0
            for x in c:
                O *= x["o"]; P *= x["p"]
            out.append({"legs": c, "O": O, "P": P, "vig": 1 - P * O})
        return out

    def label(c):
        return "×".join(x["leg"] for x in c)

    def show(title, rows, k):
        print(f"\n  {title}")
        print(f"    {'打法':<30}{'盈亏比':>6}{'P达标':>7}{'水位':>7}{bankroll:>6.0f}元赢")
        for r in rows[:k]:
            print(f"    {label(r['legs'])[:30]:<30}{r['O']:>5.1f}x{r['P']*100:>6.1f}%"
                  f"{r['vig']*100:>6.1f}%{bankroll*r['O']:>8.0f}")

    P1, P2, P3 = paths(1), paths(2), paths(3)
    singles = sorted([r for r in P1 if r["O"] >= target_mult], key=lambda r: -r["P"])
    print("\n" + "=" * 78)
    print(f"  目标: {bankroll:.0f} 元搏 ≥{target_mult:g} 倍 (终值≥{bankroll*target_mult:.0f}) · 枚举 单关/2串/3串")
    print("  排序键 P(达标)=Π真值; 只串薄腿、不同场; 凌晨球须白天提前一次买好(ride 用不了)")
    print("=" * 78)
    show(f"【单关】能一步≥{target_mult:g}x, 按 P达标 高→低", singles, 6)
    show("【2串】按 P达标 高→低", sorted(P2, key=lambda r: -r["P"]), 6)
    show("【2串】按 水位最低(最划算)", sorted(P2, key=lambda r: r["vig"]), 6)
    show("【3串·博大上限】按 水位最低(过滤 P达标≥1.5%)",
         sorted([r for r in P3 if r["P"] >= 0.015], key=lambda r: r["vig"]), 6)

    # —— 强制对照: 稳(最高P达标) vs 冲(博上限), 摊出命中率代价 ——
    cand = [r for r in (P1 + P2 + P3) if r["O"] >= target_mult]
    if cand:
        safe = max(cand, key=lambda r: r["P"])
        pool = [r for r in cand if r["P"] >= pfloor] or cand
        bold = max(pool, key=lambda r: r["O"])
        print("\n  " + "—" * 60)
        print("  【对照 · 稳 vs 冲】(同一目标, 看为冲上限放弃多少命中率)")
        print(f"    最稳达标: {label(safe['legs'])[:28]:<28} {safe['O']:>5.1f}x  "
              f"P达标{safe['P']*100:>5.1f}%  水位{safe['vig']*100:>4.1f}%  {bankroll:.0f}元赢{bankroll*safe['O']:.0f}")
        print(f"    博大上限: {label(bold['legs'])[:28]:<28} {bold['O']:>5.1f}x  "
              f"P达标{bold['P']*100:>5.1f}%  水位{bold['vig']*100:>4.1f}%  {bankroll:.0f}元赢{bankroll*bold['O']:.0f}")
        print(f"    → 为把上限 {safe['O']:.1f}x → {bold['O']:.1f}x, 命中率 {safe['P']*100:.1f}% → "
              f"{bold['P']*100:.1f}% (放弃 {(safe['P']-bold['P'])*100:.1f}pt)。要稳选上行, 要冲选下行。")

    print("\n  挑法: 少亏→高P达标低水位的单关/2串; 博大上限→高赔2/3串; "
          "杠铃→主力薄腿注 + 一小笔独立高赔飞票。")
    print("  ⚠️ 全负EV; 只串薄腿、腿≤3; 当娱乐预算; 下单前App核对、锐利盘交叉。")


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
    ap.add_argument("--goal", choices=["scan", "double", "reach"], default="scan",
                    help="scan=逐场值博线扫描(默认); reach=枚举单关/2串/3串按P(达标)排; double=满注前沿+ride")
    ap.add_argument("--target", type=float, default=2.0,
                    help="goal=double 的倍数下限 (默认 2 = 翻倍)")
    ap.add_argument("--sigma", type=float, default=0.0,
                    help="锐利源分歧 σ_p, 稳健值博线安全垫 (如 0.01 = 1个百分点)")
    ap.add_argument("--kappa", type=float, default=1.0, help="安全垫系数 k (默认 1)")
    ap.add_argument("--pfloor", type=float, default=0.05,
                    help="goal=reach 对照里'博上限注'的最低P(达标)地板 (默认 0.05=5%)")
    args = ap.parse_args()

    with open(args.json_file, encoding="utf-8") as f:
        data = json.load(f)

    matches = data.get("matches", [])

    if args.goal == "double":
        if not matches:
            print("goal=double 需要 matches。见文件头格式。")
            return
        scan(matches, args.sigma, args.kappa)
        goal_double(matches, args.bankroll or 100.0, args.target, args.sigma, args.kappa)
        return

    if args.goal == "reach":
        if not matches:
            print("goal=reach 需要 matches。见文件头格式。")
            return
        scan(matches, args.sigma, args.kappa)
        goal_reach(matches, args.bankroll or 50.0, args.target, args.sigma, args.kappa, args.pfloor)
        return

    if matches:
        bests = scan(matches, args.sigma, args.kappa)

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
