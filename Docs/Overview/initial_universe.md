---
title: Initial Universe
tags: [universe, strategy, instruments, setup]
---

# 📊 Initial Trading Universe

This document outlines the recommended starting universe of financial instruments for a modular AI trading system based in Canberra, Australia. It balances local exposure, trading costs, data availability, and strategic potential.

## 🧭 Strategy Context

- **Capital**: $50,000–$100,000 after testing
- **Time Horizon**: Daily to weekly signals
- **Signal Types**: Macroeconomic, financial event, and news/event-driven
- **Execution**: Long/short, starting with simple instruments
- **Brokerage**: IBKR or Alpaca (IBKR preferred for ASX access)

---

## ✅ Recommended Universe

### 🇦🇺 ASX Large-Cap Equities
Start with highly liquid, top-tier Australian stocks:
- S&P/ASX 50 or ASX 200 constituents (e.g. BHP, CBA, WES, WOW, FMG, NAB, WBC)
- Benefits: liquidity, franking credits, news coverage, local timezone alignment

### 📈 ASX-Listed ETFs
Add diversified or sector-based exposure:
- Broad market: IOZ (iShares ASX 200), STW (SPDR ASX 200)
- Sectoral: banking, materials, technology
- Flexibility to mimic leverage later via 2× ETFs

### 💵 U.S.-Listed Index ETFs *(Optional)*
If trading via Alpaca or IBKR:
- SPY (S&P 500), QQQ (NASDAQ 100)
- Use for global macro plays
- Note FX costs (IBKR: ~0.03% per leg) if using AUD→USD

### 🧾 Bonds via ETFs
Include fixed-income exposure:
- IAF (iShares Core Composite Bond ETF)
- VGB (Vanguard Australian Government Bond ETF)
- Useful for regime signals and macro coverage

---

## 🔍 Selection Rationale

- **Liquidity First**: Stay with instruments that have tight spreads and deep books
- **Simple to Start**: Avoid derivatives or illiquid microcaps until infrastructure and edge are proven
- **Coverage**: Instruments selected ensure access to macro, fundamental, and news-based signals
- **Broker Support**: All options are supported by IBKR, and U.S. ETFs are zero-commission via Alpaca

---

## 📌 Expansion Path

As signal quality and systems mature:
- Add leveraged or inverse ETFs (domestic or U.S.)
- Introduce options or futures via IBKR
- Include foreign equities if justified by signal advantage

---

This starting universe prioritizes **signal relevance, execution feasibility, and cost-efficiency**, giving your ML system room to scale.

