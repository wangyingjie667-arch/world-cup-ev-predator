# ⚡ World Cup EV Predator · 世界杯 EV 狩猎者

**A disciplined value-betting / EV engine for China Sports Lottery football (体彩竞彩足球).**
**体彩竞彩足球的价值下注 / EV 分析引擎。**

> Developed by **JASON WANG** · 开发者 **JASON WANG**

---

## 🇬🇧 English

China Sports Lottery (体彩) is a high-margin **soft book**. The sharp market (Polymarket / Betfair Exchange / Pinnacle) is the **truth**. This engine compares 体彩's win/draw/loss odds against sharp true probabilities, finds the **thinnest-margin** line in each match, and sizes a **singles-only** bankroll under a hard cap — printing the full profit/loss distribution.

**Honest disclaimer:** this **cannot beat the house long-term**. It minimizes the margin you pay, shapes your upside, and caps your downside. It is harm-reduction, not a money printer.

- 📖 Skill: [`en/SKILL.md`](en/SKILL.md)
- 🧮 Engine: [`scripts/ev_predator.py`](scripts/ev_predator.py) — `python scripts/ev_predator.py matches.json --bankroll 100`
- 🔌 Data-sourcing playbook: [`references/data-sources.en.md`](references/data-sources.en.md)

## 🇨🇳 中文

中国体彩是高水位的**软盘**,锐利市场(Polymarket / Betfair 交易所 / Pinnacle)才是**真值**。这个引擎拿体彩的胜平负赔率去对比锐利盘真值概率,找出每场**水位最薄**的那条线,在硬上限内做**只单关**的本金分配,并打印完整盈亏分布。

**诚实声明:** 它**长期赢不了庄家**。它能做的是把你交的水位压到最低、把上限的形状做好、把下限焊死。是降低伤害,不是印钞机。

- 📖 技能: [`zh/SKILL.md`](zh/SKILL.md)
- 🧮 引擎: [`scripts/ev_predator.py`](scripts/ev_predator.py) —— `python scripts/ev_predator.py matches.json --bankroll 100`
- 🔌 数据抓取手册: [`references/data-sources.zh.md`](references/data-sources.zh.md)

---

## 💛 Support / 捐赠

If this model helped you, feel free to **donate any amount** via Alipay — entirely optional, just a thank-you.
如果这个模型对你有帮助,欢迎用支付宝**随意打赏**——完全自愿,纯属心意。

<p align="center">
  <img src="assets/donate-alipay.png" alt="Alipay donate / 支付宝打赏 — Jason Wang" width="280">
</p>

<p align="center"><sub>Alipay · Jason Wang</sub></p>

---

## License / 许可

[MIT](LICENSE) — free to use, modify, and share. 自由使用、修改、分享。
