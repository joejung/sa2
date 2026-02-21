# sahelper — Institutional Investment Terminal Requirements

_Maintained by Agent 4 (Requirements Recorder). Target: Professional Prop Trader (JP Morgan Standard)._

---

## 1. Executive Summary
`sahelper` is transitioning from a basic helper to an **Institutional Terminal**. It must provide a unified view of Market Macro context alongside granular Portfolio Management, mirroring the data density and reliability of professional terminals (Bloomberg/Eikon).

---

## 2. Institutional Functional Requirements

### FR-100: Market Macro Dashboard
- **Description**: Real-time tracking of Global Macro indicators:
  - **Equity Indices**: S&P 500 (SPY), Nasdaq (QQQ), Russell 2000 (IWM).
  - **Fixed Income**: 10Y Treasury Yield (TNX), 2Y Yield.
  - **Commodities/FX**: Gold (GLD), Oil (USO), Dollar Index (DXY).
- **Visualization**: Mini-sparklines for intraday trends.

### FR-101: Advanced Portfolio Analytics
- **Description**: Beyond "Price/Change", implement:
  - **Sector Exposure**: Interactive breakdown (Tech, Energy, Finance, etc.).
  - **Beta & Correlation**: Basic risk metrics against SPY.
  - **Performance Attribution**: Contribution of each holding to total daily P&L.

### FR-102: Targeted Seeking Alpha Sync (ID: 62720994)
- **Description**: Precision scraping of the specific portfolio URL.
- **Data Points**: Ticker, Shares, Market Value, P/E, Div Yield, and Rating (Buy/Hold/Sell).

---

## 3. UI/UX Standards (Enterprise)
- **High Density**: Minimize whitespace; use smaller, crisp fonts (Inter/Roboto).
- **Color Coding**: Institutional standards for gains (Emerald) and losses (Crimson).
- **Responsiveness**: Async data fetching must never lag the UI thread.

---

## 4. Technical Constraints
- **Database**: SQLite with optimized indexing for fast ticker lookups.
- **Async**: Strict separation of IO (Playwright) and UI (Qt).
