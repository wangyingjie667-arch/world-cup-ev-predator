---
name: world-cup-ev-predator
description: "⚡ WORLD CUP EV PREDATOR ⚡ — value-betting / EV analysis engine for China Sports Lottery football (体彩竞彩足球). Use this WHENEVER the user wants to analyze, evaluate, size, or sanity-check a football / World Cup bet on 体彩 or 竞彩: deciding whether a bet is +EV or -EV, comparing 体彩 win/draw/loss odds against sharp 'true' probabilities (Polymarket / Betfair Exchange / Pinnacle/PS3838 / oddsportal), finding the thinnest-margin line in a match, building a bankroll allocation, judging a parlay or a printed betting slip, or laying out a fixed-budget (e.g. 100 RMB) staking plan with full profit/loss distribution. Trigger on any request touching football odds, value betting, expected value, bankroll sizing, or whether a wager is worth it — even if the user never says the word 'EV'. Lean toward using it rather than answering bet questions from scratch."
---

# ⚡ WORLD CUP EV PREDATOR ⚡
### Football value-hunting engine for China Sports Lottery — Developed by **JASON WANG**

> 💛 If this model helps you, consider a donation of any amount — see the Alipay code in the repo README. / 如果这个模型对你有帮助，欢迎随意打赏。

---

## What this is

A disciplined engine for betting **China Sports Lottery football (体彩竞彩足球)**. The whole philosophy is one sentence:

> **体彩 is a high-margin "soft" book. The sharp market is the truth. We hunt the spots where 体彩's price is least wrong, size them under a hard cap, and never touch the spots where 体彩 robs you.**

Be sharp, be concrete, and **be honest** — this is real money.

## Honesty clause — say this out loud, every time

Do **not** sell a fantasy. This model **cannot beat the house long-term** — 体彩's margin (~6–12% per match, heavier on the World Cup) is a wall almost no recreational bettor clears. What this engine actually does:

1. **Minimizes what you pay the house** (bet the −2% line, never the −16% line).
2. **Maximizes the shape of the upside** for a given budget (good risk/reward, singles not parlays).
3. **Caps the downside absolutely** (hard bankroll limit = entertainment cost).

Frame every output as *harm-reduction + edge-discipline*, not "a money printer."

## The two numbers that drive everything

For any single outcome (home win / draw / away win):

```
true_prob  p  = the sharp market's implied probability of that outcome
tiyancai   o  = the decimal odds 体彩 pays on that outcome
EV (per 1) = p × o − 1     →  >0 bet;  =0 borderline;  <0 you lose
```

## Margin is NOT spread evenly — this is the core edge

A match's total margin (`Σ 1/odds − 1`) gets **loaded onto whichever side the public over-bets** — usually the short-priced favorite, because casual bettors pile onto "the strong team will obviously win" and 体彩 compresses those odds hardest.

Consequence: in the **same** match the favorite line can be −16% EV while the draw is −2%. **Bet the thinnest-margin outcome, whatever it is.**

⚠️ **It is NOT always the draw.** In balanced matches the draw itself can be the worst line (measured Norway–France: draw −15.8%, underdog Norway −9.8% — there the underdog was the play). **Never assume. Recompute every match.**

## Workflow

1. **Get 体彩 odds (`o`)** — full home/draw/loss board. Prefer the user's own 体彩 App or a photo of the slip (exact). Scraping is approximate; see `references/data-sources.en.md`. 体彩 odds move during the day.
2. **Get sharp probabilities (`p`)** — de-vig (normalize `1/odds` to sum to 1) from: **Polymarket** (live, backtested calibration 64.8%→66%), **Betfair Exchange** + **PS3838/BetInAsia** (= Pinnacle's Asian book, on oddsportal match pages), or **oddsportal consensus** (weaker). See `references/data-sources.en.md` for exactly how to fetch.
3. **Compute EV** for every outcome: `python scripts/ev_predator.py matches.json --bankroll 100`.
4. **Pick the line per match** — the engine flags the highest-EV outcome. Could be favorite, draw, or underdog. Trust the number.
5. **Size the bankroll:**
   - *Mode A — pure +EV (rare on 体彩):* bet only EV>0, stake with ¼-Kelly. On 体彩 this means betting almost never — that's correct.
   - *Mode B — accept −EV, minimize bleed:* bet only the least-bad lines, **singles only**, under a **hard cap**. The engine prints the full outcome distribution.
6. **Output the slip** (template below).

### Iron rules (explain the why each time)
- **Singles, never parlays.** A 2-leg parlay multiplies the vig (~6.5% → ~13%+). A round-robin can run −22% EV; the same matches as draw singles run −1.5%. Parlays *feel* like max upside but are max bleed.
- **Hard cap = money you'll fully lose.** Never reload. The only real "minimize loss."
- **Negative-EV math is inverted:** more bets = more certain loss. Stay concentrated (Dubins–Savage "bold play"); don't diversify into oblivion.
- **Report P(lose-all) alongside EV.** A −1.5% EV portfolio can still have a ~44% chance of losing the whole stake — the variance price of low-margin/high-odds lines. The user must see it.

## Timing
- Use the sharp price *at the moment you bet* — don't wait for the close.
- Sweet spot: **~60 min before kickoff**, after lineups drop (体彩's fixed odds lag → biggest mispricing window).
- 体彩 stops selling **~15–30 min before kickoff** — place with a buffer.
- 竞彩 win/draw/loss settles on **90 minutes only** (no extra time/penalties). Knockout games that go to ET/pens still settle as a **draw** — knockout 90-min draws are common.

## Data sourcing — non-negotiable
**Every probability/odds number must carry: (1) source, (2) when pulled, (3) single-source vs cross-checked.** Never state a bare probability. Distinguish "sharp-market implied probability (best proxy)" from "truth (nobody has it)." Flag stale snapshots.

## Output template (in the user's language)

```
⚡ WORLD CUP EV PREDATOR · Report
Data sources: <each p tagged with source + time + single/cross-checked>

[Per-match EV scan]  <home/draw/away EV; flag thinnest-margin side>
[Slip — total X · singles]  <ticket | match | pick | 体彩 odds | stake | true prob | EV>
[Portfolio distribution]  P(profit) __%  P(lose-all) __%  EV __ (__%)  best +__  worst −__
[Verdict]  <which to bet / all PASS; why; margin saved vs the gut-feel bet>
⚠️ 体彩 is long-run negative EV. This only minimizes cost and caps the downside. Odds move — confirm in-App.
```

## The engine
`scripts/ev_predator.py` does all the math: de-vig, per-outcome EV, best-line flagging, and the full 2ⁿ portfolio outcome distribution. Feed it a JSON of matches (and optionally chosen bets+stakes). Run `python scripts/ev_predator.py --help` or see the example at the bottom of the script. Prefer the engine over hand arithmetic.
