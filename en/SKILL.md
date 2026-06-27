---
name: world-cup-ev-predator
description: "⚡ WORLD CUP EV PREDATOR ⚡ — value-betting / EV analysis engine for China Sports Lottery football (体彩竞彩足球). Use this WHENEVER the user wants to analyze, evaluate, size, or sanity-check a football / World Cup bet on 体彩 or 竞彩: deciding whether a bet is +EV or -EV, comparing 体彩 win/draw/loss odds against sharp 'true' probabilities (Polymarket / Betfair Exchange / Pinnacle/PS3838 / oddsportal), finding the thinnest-margin line in a match, building a bankroll allocation, judging a parlay or a printed betting slip, or laying out a fixed-budget (e.g. 100 RMB) staking plan with full profit/loss distribution. Trigger on any request touching football odds, value betting, expected value, bankroll sizing, or whether a wager is worth it — even if the user never says the word 'EV'. Lean toward using it rather than answering bet questions from scratch."
---

# ⚡ WORLD CUP EV PREDATOR ⚡
### Football value-hunting engine for China Sports Lottery — Developed by **JASON WANG**

> 💛 If this model helps you, consider a donation of any amount — see the Alipay code in the repo README. / 如果这个模型对你有帮助，欢迎随意打赏。

---

## 📣 Manifesto — the house already won, the moment you paid

It's not that you don't know football. The game is *built* so you bleed out slow.

The house edge isn't luck. It's the **margin** — 6 to 12% skimmed off every match, more at the World Cup. Before the whistle blows, you're already down. Not a conspiracy; it's math baked into the rules. Over ten years and a million tickets, the machine grinds every retail bettor down to the cent.

And here's the dirty part: **the cut isn't spread evenly.** It's piled thickest exactly where you love to bet — the short-priced favorite, "the strong team obviously wins." The safer it feels, the harder you're robbed. 体彩 knows you'll back Germany, so it crushes Germany's price to the bone, and you hand over your money with a smile.

For years, retail has been the house's feed. The real probabilities, the real prices — the smart money always had them. You never did. You were always the one left holding the bag.

**But you remember GameStop, right?**

That was the moment a crowd of retail saw the cards in the house's hand and said: *we're not playing by your rules anymore.*

**This project is the light you shine on that table.** Open source. Free. It does one thing: it slaps the real probabilities — forged by millions in live money — right onto your face, so for the first time you see exactly how many points the house just took from you, and how your beloved parlay funnels your cash into its mouth, slip by slip.

We don't promise you'll get rich (keep reading — we'll tell you why nobody can). We promise one thing: **you stop being the mark. You cut the house's tax to the lowest on the internet. Together.**

Now the technical part. Here's why this actually works.

### Why #1: the smart money is genuinely accurate — I backtested 50 matches

Talk is cheap. Every finished match this World Cup, I pulled Polymarket's real traded price at exactly **T-minus-60-minutes** (probabilities forged by millions in live money) and graded it against the **actual scoreline**. 50 matches, 150 outcome legs.

![Calibration: what the market says happens, happens](../assets/calibration.svg)

The market says "24% happens," it happened 23%; says "58%," it cashed 65% — **the dots sit right on the perfect line.** Brier score 0.527 (a coin-flip is 0.667); strip out draws and the top pick hits 89%. That's the "true win probability" you've been dreaming of.
*(Honest caveat: Polymarket only, 50 matches — small, thin buckets are noisy, all marked on the chart. Pinnacle and the exchange weren't separately backtested — but in live pulls all four agreed within 1.5 points, singing the same note.)*

### Why #2: the margin is hidden — and we can see it

Same match, **Japan vs Sweden**: bet Japan to win, EV **−18%**; bet the draw nobody wants, EV **≈0%** — basically free. One bleeds you out, one barely costs a thing, and the gap is hidden where you never look. This model strips every bet bare and shows you where the margin is thin — bet the thin, walk past the thick.

### Why #3: parlaying *favorites* is the trap — but the parlay itself isn't the sin

A parlay *feels* like swinging for the fences; the cost is it **multiplies** the margin. Parlay **thick-margin favorites** — a 2-leg slip runs −22% expected; the same as thin-margin singles, −1.5%. The house's favorite customer is the guy clutching a short-odds favorite parlay at 2 a.m. Don't be that guy.

**But draw the distinction:** parlaying *thin legs* to reach a ceiling a single can't touch is another matter — two thin legs combined can carry *less* total margin than one heavily-juiced longshot single. The rule: **only parlay thin legs, ≤3 legs, and if the legs kick off in sequence use ride instead.** See below.

### Finally, the hard truth: you can't beat the house

Long term you can't, nobody can, and anyone selling "guaranteed wins" is lying to you. This model won't make you win — it makes you **lose the least, weld the floor shut, and occasionally steal a lucky night.** Bet only what you can afford to lose. See the margin. Parlay only thin legs — never favorites.

*That's* what we mean by **Beat the house**: not knocking it out — you can't — but never again kneeling to feed it.

---

## What this is

A disciplined engine for betting **China Sports Lottery football (体彩竞彩足球)**. The whole philosophy is one sentence:

> **体彩 is a high-margin "soft" book. The sharp market is the truth. We hunt the spots where 体彩's price is least wrong, size them under a hard cap, and never touch the spots where 体彩 robs you.**

Be sharp, be concrete, and **be honest** — this is real money.

## Honesty clause — say this out loud, every time

Do **not** sell a fantasy. This model **cannot beat the house long-term** — 体彩's margin (~6–12% per match, heavier on the World Cup) is a wall almost no recreational bettor clears. What this engine actually does:

1. **Minimizes what you pay the house** (bet the thin-margin line, never the −16% robbery).
2. **Shapes the upside to the goal** — the right risk/reward and the right path (single / ride / parlay) for what you're actually trying to do (lose-less vs go-for-2x vs chase-a-big-ceiling).
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

## The value line: payoff-ratio × win-rate (is it worth a punt?)

EV just mashes p and o into one scalar. The equivalent, more intuitive view:
- **Payoff ratio b = odds − 1**; **win-rate = p**.
- **Worth a punt ⟺ win-rate × odds `p·o > 1` ⟺ payoff ratio `b > (1−p)/p` ⟺ `p > 1/o`** (all the same thing).
- **Value-line gap = `b − (1−p)/p`** (<0 = below the line = 体彩 is robbing you).
- **A low win-rate can still be worth it** — if the payoff ratio clears the line (e.g. 17% win-rate with payoff ratio >4.9). Don't veto a leg just because the win-rate is low.
- Kelly stake fraction `f* = EV / payoff-ratio` (≤0 → don't bet).

## Margin is not the objective — but never ignore it

Margin (=EV) is **not the objective function** — on 体彩 everything is −EV, so ranking purely by margin means you'd never bet. But it's **not meaningless** either: it's how you pick the best ticket at a given prize. The key formula:

```
P(reach target) = (1 / total odds) × (1 − margin)
```

- **Payoff ratio / total odds** sets *how big the prize is*; **margin** sets *what fraction of fair probability you get for that prize*.
- For the same prize, higher margin = lower hit-rate — and 体彩 hides the **thickest margin on the biggest-payoff tickets** (the longshot trap). "Big payoff so ignore the margin" is exactly the trap it sets.
- **So rank by `P(reach target)`**: one number that absorbs both payoff ratio and margin. Payoff ratio picks the prize tier; margin picks the best ticket in that tier.

## The goal decides the play (don't preset, don't favor one)

Fix the goal first, then choose the play:
- **Goal A · lose less (risk-neutral):** rank by `EV` or `EV − λ·SD` (λ≈0.4), bet the 1–2 thinnest-margin lines, singles. Mode A (pure +EV) means betting almost never on 体彩 — that's correct, not illogical.
- **Goal B · reach a target (double / chase a big ceiling):** this is bold play in a −EV game with a target line — concentrate, be bold, rank by `P(reach target)`, **do NOT flat-split** (flat-splitting is the mathematically worst target-reaching strategy). "Target" can have a doubling floor and an uncapped top.
- Under either goal you still look at margin (it's inside P(reach target)) — it's just no longer the sole sort key.

## Workflow

1. **Clear the time gate first**: 体彩 sells in daytime/evening, closing ~15–30 min before kickoff; World Cup games mostly kick off **overnight (China time)** → you must **buy upfront in the daytime** → **ride is impossible for overnight games** (you can't place leg 2 at 5 a.m.), so the only way to combine multiple games upfront is a **parlay**. Drop matches you can't buy first.
2. **Get 体彩 odds (`o`)** — full home/draw/loss board. Prefer the user's own 体彩 App or a photo of the slip (exact). See `references/data-sources.en.md`.
3. **Get sharp probabilities (`p`)** — de-vig (normalize `1/odds` to 1): **Polymarket** (live, backtest 64.8%→66%), **Betfair Exchange** + **PS3838/BetInAsia** (= Pinnacle's Asian book), or **oddsportal consensus** (weaker). Tag every number source + time + single/cross-checked.
4. **Enumerate paths, rank by goal**: `python scripts/ev_predator.py m.json --goal reach --target 2 --sigma 0.01`. Singles / ride (sequential only) / 2–3-leg parlays, ranked by `P(reach target)` and margin.
5. **Size it**: hard cap = money you'll fully lose, never reload. Reaching a target → don't flat-split, concentrate by P(reach target); report P(reach) AND P(lose-all); for "uncapped upside + lose less" use a **barbell** (main thin-leg bet + one small independent high-odds flyer).
6. **Output the slip + mandatory contrast** (template below).

### Iron rules (revised — explain the why each time)
- **Parlays are no longer banned outright.** Parlaying **thick-margin favorites** is the trap; parlaying **thin legs** to reach a ceiling a single can't touch is not. Rules: ① only thin legs (each near the value line); ② ≤3 legs (margin compounds); ③ if legs are sequential, ride instead of parlay; ④ parlay only when legs are simultaneous OR a single can't reach the target.
- **Hard cap = money you'll fully lose**, never reload — the only real "minimize loss." Kelly is 0 on −EV, so this is an entertainment budget, not an investment.
- **Margin is not the objective but never ignore it**: rank by `P(reach target)` (already contains payoff ratio + margin); when reaching a target stay concentrated (Dubins–Savage "bold play"), don't diversify into oblivion.
- **Always give the "safe vs swing" contrast**: the highest-P(reach) safe bet vs the ceiling bet + how many points of hit-rate you give up for the ceiling — show this even when the user only wants one answer, so they see the cost before deciding. Report P(lose-all) too.

## Timing
- Use the sharp price *at the moment you bet*. Sweet spot ~60 min before kickoff (after lineups) — BUT for **overnight games you can't reach that window**, so buy in the daytime and accept a snapshot from hours earlier (measured drift over half a day was mostly 0–3pt; the real risk is missing the lineup-release jump at ~T-1h).
- 体彩 stops selling **~15–30 min before kickoff** — place with a buffer.
- 竞彩 win/draw/loss settles on **90 minutes only** (no extra time/penalties). Knockout games that go to ET/pens still settle as a **draw** — knockout 90-min draws are common.

## Data sourcing — non-negotiable
**Every probability/odds number must carry: (1) source, (2) when pulled, (3) single-source vs cross-checked.** Never state a bare probability. Distinguish "sharp-market implied probability (best proxy)" from "truth (nobody has it)." Flag stale snapshots.

## Output template (in the user's language)

Every probability/odds number carries source + time + single/cross-checked. Per-match scan has a fixed **7 columns**. **When the user is overwhelmed, don't hand a menu — the verdict is one conclusion, but it MUST carry the "safe vs swing" contrast.**

```
⚡ WORLD CUP EV PREDATOR · Report
Data sources: <each p tagged source + time + single/cross-checked; if sharp not pulled, mark "TBD">

[Per-match scan] match | pick | book-implied(1/odds) | 体彩 odds | true(Polymarket) | sharp(Pinnacle/Betfair) | payoff ratio | value-line gap | EV   <flag thinnest margin>
[Path frontier · by goal] tier | play(single/ride/parlay) | payoff ratio | P(reach) | margin | win@X   <drop un-buyable matches first>
[Contrast · safe vs swing (mandatory)] Safest: <play> P(reach)__% __x | Biggest ceiling: <play> P(reach)__% __x | → give up __pt of hit-rate for the ceiling
[Slip — total X (≤ hard cap)] ticket | play | match/leg | 体彩 odds | stake | P(reach) | leg margin
[Portfolio distribution] P(reach/profit) __%  P(lose-all) __%  E[final] __ (__%)  hit +__  big +__  worst −__
[Verdict · one conclusion] which to bet & how much; why (payoff×win-rate fit + goal); timing note
⚠️ 体彩 is long-run negative EV. This only minimizes cost and caps the downside. Odds move — confirm in-App.
```

## The engine
`scripts/ev_predator.py` has three modes:
- `--goal scan` (default): per-match 7 columns (book-implied / odds / true / sharp / payoff ratio / value-line gap / EV) + thinnest margin; `--sigma 0.01` adds the robust buffer (thicker for high-odds legs).
- `--goal reach --target 2`: enumerate singles / 2-leg / 3-leg parlays, rank by `P(reach target)`, and **always print the "safe vs swing" contrast** (`--pfloor` tunes the ceiling-bet's hit-rate floor). This is the "how do I bet today" workhorse.
- `--goal double --target 2`: all-in frontier + base × let-it-ride combos.
- `--bankroll N` + `bets` in the JSON: enumerate the 2ⁿ profit/loss distribution (P(reach), P(lose-all), best/worst).

Per-match JSON fields: `sharp_prob` (fills the sharp column), `sigma`, `kickoff`. Run `--help` for the format. Prefer the engine over hand arithmetic. **Honesty > pleasing the user.**
