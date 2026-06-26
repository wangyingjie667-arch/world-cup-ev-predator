#!/usr/bin/env python3
"""
Reproducible calibration chart for the World Cup EV Predator backtest.
Data is REAL: 50 finished World Cup matches, Polymarket pre-match (~60 min before
kickoff) implied probabilities vs actual results. Each match contributes 3 outcome
"legs" (home/draw/away) -> 150 legs, bucketed by predicted probability.

Source: Polymarket clob API price snapshots, pulled at T-60min, graded on real
results. Polymarket ONLY (Pinnacle/Betfair historical snapshots are paywalled, so
they are NOT in this backtest — their accuracy rests on published literature + the
fact that in live pulls all three agreed within ~1.5 points).

Run:  python make_calibration_chart.py   ->  writes calibration.svg
"""

# (avg_predicted_%, actual_%, n)  -- the real bucketed backtest output
BUCKETS = [
    (5.8,  4.8,  21),
    (14.6, 20.6, 34),
    (24.4, 23.1, 39),
    (33.8, 22.2, 9),
    (44.8, 66.7, 6),
    (58.5, 64.7, 17),
    (77.6, 66.7, 24),
]
# headline aggregate
FAV_PRED, FAV_ACT = 64.8, 66.0
BRIER, BRIER_RAND = 0.527, 0.667
HITRATE_EXDRAW = 89  # %

# ---- plot geometry ----
L, R, T, B = 80, 440, 60, 420          # plot box (360 x 360, square)
def X(p): return L + p * (R - L) / 100.0
def Y(a): return B - a * (B - T) / 100.0
def rad(n): return 4 + n ** 0.5 * 1.5

def svg():
    s = []
    s.append('<svg viewBox="0 0 560 520" xmlns="http://www.w3.org/2000/svg" '
             'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" '
             'role="img" aria-label="Polymarket calibration backtest">')
    s.append('<title>Polymarket 开赛前赔率校准 · 50场回测</title>')
    s.append('<desc>市场隐含概率 vs 实际发生频率;点越贴近对角线说明概率越可信。</desc>')
    # panel
    s.append('<rect x="0" y="0" width="560" height="520" fill="#ffffff"/>')
    s.append('<rect x="0.5" y="0.5" width="559" height="519" fill="none" stroke="#e6e6e0"/>')
    # title
    s.append('<text x="30" y="34" font-size="19" font-weight="700" fill="#16182b">'
             '市场说的概率,到底准不准?</text>')
    s.append('<text x="30" y="52" font-size="12.5" fill="#6b6f80">'
             'Polymarket 开赛前60分钟真实成交价 vs 真实赛果 · 50场 / 150条结果腿</text>')
    # gridlines + ticks
    for v in (0, 25, 50, 75, 100):
        x, y = X(v), Y(v)
        s.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{B}" stroke="#f0f0ec"/>')
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="#f0f0ec"/>')
        s.append(f'<text x="{x:.1f}" y="{B+18}" font-size="11" fill="#9a9aa5" '
                 f'text-anchor="middle">{v}%</text>')
        s.append(f'<text x="{L-10}" y="{y+4:.1f}" font-size="11" fill="#9a9aa5" '
                 f'text-anchor="end">{v}%</text>')
    # axis box
    s.append(f'<rect x="{L}" y="{T}" width="{R-L}" height="{B-T}" fill="none" stroke="#d6d6cf"/>')
    # perfect-calibration diagonal
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(100):.1f}" y2="{Y(100):.1f}" '
             'stroke="#b9b9c4" stroke-width="1.6" stroke-dasharray="6 5"/>')
    s.append(f'<text x="{X(100)-6:.1f}" y="{Y(100)+16:.1f}" font-size="10.5" '
             'fill="#b0b0bb" text-anchor="end" font-style="italic">完美校准线</text>')
    # bubbles
    for pred, act, n in BUCKETS:
        cx, cy, r = X(pred), Y(act), rad(n)
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                 'fill="#2f7d6b" fill-opacity="0.34" stroke="#2f7d6b" stroke-width="1.4"/>')
        s.append(f'<text x="{cx:.1f}" y="{cy+3.5:.1f}" font-size="9" fill="#1c4d42" '
                 f'text-anchor="middle">n={n}</text>')
    # callouts
    s.append(f'<text x="{X(24.4):.1f}" y="{Y(23.1)+30:.1f}" font-size="10.5" fill="#2f7d6b" '
             'text-anchor="middle">低概率事件:报得极准</text>')
    s.append(f'<text x="{X(77.6)-2:.1f}" y="{Y(66.7)-22:.1f}" font-size="10.5" fill="#b5760e" '
             'text-anchor="middle">强热门略被高估</text>')
    s.append(f'<text x="{X(77.6):.1f}" y="{Y(66.7)-9:.1f}" font-size="9.5" fill="#b5760e" '
             'text-anchor="middle">(被逼平拖累)</text>')
    # axis titles
    s.append(f'<text x="{(L+R)/2:.1f}" y="{B+38}" font-size="12.5" fill="#41434f" '
             'text-anchor="middle" font-weight="600">市场说会发生的概率  →</text>')
    s.append(f'<text x="26" y="{(T+B)/2:.1f}" font-size="12.5" fill="#41434f" '
             f'text-anchor="middle" font-weight="600" transform="rotate(-90 26 {(T+B)/2:.1f})">'
             '↑  实际发生的频率</text>')
    # stat strip
    sy = 470
    s.append(f'<rect x="30" y="{sy}" width="500" height="34" rx="6" fill="#f6f6f1"/>')
    stats = (f'庄家热门 报64.8% → 实赢66.0%   ·   Brier 0.527 (随机0.667)   ·   '
             f'去掉平局命中率 89%')
    s.append(f'<text x="42" y="{sy+22}" font-size="11.5" fill="#2b2d3a">{stats}</text>')
    s.append('<text x="30" y="514" font-size="9.5" fill="#a9a9b3">'
             'World Cup EV Predator · 回测 by JASON WANG · 来源 Polymarket API (T-60min) vs 真实赛果</text>')
    s.append('</svg>')
    return "\n".join(s)

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg())
    print("wrote", out)
