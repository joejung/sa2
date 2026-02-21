# Architecture Blueprint (SAHelper - Enterprise)

**Agent #1 (Planner)**: This document outlines the structural transformation from a single-window script to a modular, enterprise-grade application.

---

## 1. High-Level Design (MVC Pattern)

We will adopt a classic Model-View-Controller (MVC) pattern adapted for PyQt6 (Model-View-Delegate).

### A. The Model (Database & Data Access)
- **Technology**: `SQLAlchemy` (ORM) + `SQLite`.
- **Entities**:
  - `Portfolio`: Name, Description, Total Value.
  - `Position`: Ticker, Quantity, Cost Basis, Current Price.
  - `Transaction`: Buy/Sell records.
  - `StockData`: Fundamental metrics (PE, Yield, Sector) cached from Seeking Alpha.

### B. The View (UI Layer)
- **Main Window**: A `QMainWindow` with a `QDockWidget` sidebar for navigation.
- **Widgets**:
  - `DashboardWidget`: Summary cards (Total Value, Daily Change), Top Gainers/Losers list.
  - `PortfolioTableWidget`: Custom `QTableView` with sorting, filtering, and conditional formatting (Green/Red).
  - `StockDetailWidget`: Chart + Data grid for a selected ticker.
  - `AutomationPanel`: Controls for the existing Playwright tasks (Login, Sync).

### C. The Controller (Business Logic)
- **DataController**: Manages database CRUD operations.
- **MarketDataService**: Fetches prices/news (Scraping via `automation.py` or free APIs).
- **AutomationManager**: Runs the Playwright tasks in a background thread/process to keep UI responsive.

---

## 2. Directory Structure

```
sahelper/
├── main.py                # Entry point
├── config.py              # App settings
├── database/              # Data Layer
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   └── session.py         # DB connection management
├── ui/                    # Presentation Layer
│   ├── main_window.py     # Shell application
│   ├── dashboard.py       # Overview panel
│   ├── portfolio.py       # Detailed grid view
│   ├── analysis.py        # Stock charts & data
│   └── styles.qss         # Custom themes
├── services/              # Business Logic
│   ├── market_data.py     # Price fetcher
│   └── automation.py      # Existing Playwright logic (refactored)
└── utils/                 # Helpers
    └── logger.py
```

---

## 3. Implementation Phases

1.  **Phase 1: Foundation.** Set up Database, Models, and basic Project Structure.
2.  **Phase 2: UI Shell.** Implement the Navigation Sidebar and Empty Placeholders.
3.  **Phase 3: Portfolio Manager.** CRUD for portfolios/positions (Manual Entry).
4.  **Phase 4: Market Data Integration.** Connect to scraping logic to populate prices.
5.  **Phase 5: Automation UI.** Integrate existing Login/Copy logic into the new UI.

---
