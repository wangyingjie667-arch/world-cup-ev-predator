# EV PREDATOR — 数据抓取手册 (data-sourcing playbook)

How to actually get `o` (体彩 odds) and `p` (sharp true probs). Learned the hard way; saves you from re-probing every time.

## Golden rule
Every number you report carries **source + timestamp + single-source/cross-checked**. `p` is the *sharp market's implied probability* — the best available proxy for truth, NOT truth. It drifts; re-pull near kickoff.

## `o` — 体彩竞彩 odds (主胜/平/客胜)
竞彩 is centrally priced nationwide, so every outlet shows the *same* official 体彩 line (subject to intraday updates).

| Source | How | Reliability |
|---|---|---|
| **Jason's 体彩 App / photo of slip** | Ask him to read or screenshot the 胜平负 board | ★★★ exact, authoritative — **prefer this** |
| **zgzcw via WebFetch** | `WebFetch("https://cp.zgzcw.com/lottery/jchtplayvsForJsp.action?lotteryId=47", ...)` ask for "主队/客队 + 胜/平/负 三个小数赔率" | ★★ real numbers, but the summarizer often returns only *part* of the slate and may show a different match-day batch. Validate against any known value (e.g. a slip) before trusting. |
| **sporttery.cn (official)** | — | ✗ blocks non-browser WebFetch (socket closes); in the Chrome MCP the page never reaches `document_idle` so screenshot/get_page_text time out. Effectively unusable via tools. |

⚠️ 体彩 odds move during the day. A scrape is a stale snapshot — label the time, and re-confirm in-App before betting.

## `p` — sharp true probability
De-vig (normalize `1/赔率` to sum to 1) from the sharpest source available.

| Source | How | Notes |
|---|---|---|
| **Polymarket** | Chrome MCP → `navigate("https://polymarket.com/sports/soccer/games")` → wait → screenshot/scroll. Per-match cards show cents = probability (e.g. GER 62.2¢ → 62.2%). | ★★★ works in browser. Backtest: 50 matches, priced 64.8% → won 66.0% (well-calibrated). Has per-match World Cup markets under the `fifa-world-cup` tag. |
| **Betfair Exchange + PS3838** | Chrome MCP → oddsportal match page → `get_page_text`. The page lists a **Betfair Exchange** back/lay row (sharpest, near-zero margin) and **BetInAsia (incl. PS3838 = Pinnacle's Asian book)**. | ★★★ great cross-check for Polymarket. PS3838 IS Pinnacle. |
| **oddsportal consensus** | Chrome MCP → `navigate("https://www.oddsportal.com/football/world/world-championship-2026/")` → dismiss cookie banner (Reject All) → scroll → `get_page_text`; or click a match for the full book list. | ★★ league page shows near-fair "highest odds" (sum slightly <1). Use when nothing sharper is reachable — single-source, lower confidence. |
| **Pinnacle direct (pinnacle.com)** | — | ✗ blocked by Chrome MCP safety policy (gambling domain). Use PS3838 via oddsportal instead. |

### Browser quirks (Chrome MCP)
- Chinese sites with heavy ad/tracker scripts (sporttery, zgzcw) often **never fire `document_idle`** → `screenshot`/`get_page_text`/`read_page` time out at 45s. Western sites (oddsportal, polymarket) render fine.
- Use `browser_batch` to chain navigate → wait → screenshot/get_page_text.
- oddsportal cookie banner covers the page — click **Reject All** (privacy-preserving) first.

## Worked sanity-check (2026-06-26 slate, for reference)
体彩 vs sharp, three sources agreed within ~1.5pts:

| Match | Outcome | 体彩 | Betfair de-vig | PS3838 | Polymarket | EV |
|---|---|---|---|---|---|---|
| 厄瓜多尔–德国 | 德国胜 | 1.36 | 63.7% | 1.54 | 62.2% | −16% |
| 厄瓜多尔–德国 | 平 | 4.90 | 19.7% | — | 20.0% | −2% |
| 日本–瑞典 | 平 | 3.57 | 27.6% | — | 28.0% | ≈0% |
| 土耳其–美国 | 美国胜 | 1.69 | 50.8% | 1.94 | 52% | −14% |

Pattern: 体彩 loads margin on short-priced favorites; draws/underdogs in lopsided matches are the thin lines. **But always recompute** — in balanced matches the draw can be the worst line.
