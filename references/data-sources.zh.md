# 世界杯 EV 狩猎者 —— 数据抓取手册

如何真正拿到 `o`(体彩赔率)和 `p`(锐利真值概率)。踩过坑后总结的,省得每次重新摸索。

## 黄金法则
每个数都带 **来源 + 时间 + 单源/多源交叉**。`p` 是*锐利市场的隐含概率*——真值的最佳代理,**不是**真值本身。它会漂移,临场要重新拉。

## `o` —— 体彩竞彩赔率(主胜/平/客胜)
竞彩全国统一定价,所以各家显示的都是**同一套官方体彩盘**(日内会更新)。

| 来源 | 怎么用 | 可靠度 |
|---|---|---|
| **体彩 App / 彩票照片** | 让用户读出或截图胜平负盘 | ★★★ 精确权威,**首选** |
| **竞彩网 WebFetch** | `WebFetch("https://cp.zgzcw.com/lottery/jchtplayvsForJsp.action?lotteryId=47", ...)` 要"主队/客队 + 胜/平/负三个小数赔率" | ★★ 数字真,但摘要常只返回部分场次、可能给错比赛日那批。先拿已知值(如彩票)校验再信 |
| **sporttery.cn(官网)** | —— | ✗ 拦非浏览器 WebFetch(socket 断);Chrome 里页面永不进 `document_idle`,截图/取文本 45 秒超时。基本用不了 |

⚠️ 体彩赔率一天里会动。爬来的是过期快照——标时间,下单前 App 再确认。

## `p` —— 锐利真值概率
去水(把 `1/赔率` 归一化到和为1),取能拿到的最锐利源。

| 来源 | 怎么用 | 备注 |
|---|---|---|
| **Polymarket** | Chrome → `navigate("https://polymarket.com/sports/soccer/games")` → 等 → 截图/滚动。逐场卡片上"分=概率"(如 GER 62.2¢ → 62.2%) | ★★★ 浏览器能开。回测 50 场:报 64.8% → 实赢 66.0%(校准好)。世界杯逐场盘在 `fifa-world-cup` tag 下 |
| **Betfair 交易所 + PS3838** | Chrome → oddsportal 比赛页 → `get_page_text`。页面列 **Betfair Exchange** back/lay(最锐、近零水位)和 **BetInAsia(含 PS3838 = Pinnacle 亚洲盘)** | ★★★ 给 Polymarket 做交叉。PS3838 就是 Pinnacle |
| **oddsportal 共识** | Chrome → `navigate("https://www.oddsportal.com/football/world/world-championship-2026/")` → 关 cookie 弹窗(Reject All)→ 滚动 → `get_page_text`;或点进某场看全部博彩公司 | ★★ 联赛页是接近公允的"最高赔率"(和略<1)。没更锐利源时用——单源,可信度低一档 |
| **Pinnacle 官网** | —— | ✗ 被 Chrome 安全策略拦(赌博域名)。改用 oddsportal 上的 PS3838 |

### 浏览器小坑(Chrome MCP)
- 广告/追踪脚本重的中文站(sporttery、zgzcw)常**永不触发 `document_idle`** → 截图/取文本/读页 45 秒超时。西方站(oddsportal、polymarket)正常。
- 用 `browser_batch` 串 navigate → wait → 截图/取文本。
- oddsportal 的 cookie 弹窗会盖住页面——先点 **Reject All**(隐私优先)。

## 一个校验样本(2026-06-26 那批,供参考)
体彩 vs 锐利,三源一致(误差约 1.5 个点内):

| 比赛 | 选项 | 体彩 | Betfair去水 | PS3838 | Polymarket | EV |
|---|---|---|---|---|---|---|
| 厄瓜多尔–德国 | 德国胜 | 1.36 | 63.7% | 1.54 | 62.2% | −16% |
| 厄瓜多尔–德国 | 平 | 4.90 | 19.7% | — | 20.0% | −2% |
| 日本–瑞典 | 平 | 3.57 | 27.6% | — | 28.0% | ≈0% |
| 土耳其–美国 | 美国胜 | 1.69 | 50.8% | 1.94 | 52% | −14% |

规律:体彩把水位堆在短赔大热门上;势力悬殊的比赛里平局/冷门是薄线。**但永远重算**——势均力敌时平局可能反而最差。
