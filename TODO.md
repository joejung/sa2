# TODO.md - SAHelper Project Roadmap

## 1. Completed Features ✅
The following core functionalities have been successfully implemented:
- **Real-time Data Integration**: Background fetching of market prices and indices using `yfinance`.
- **Professional Candlestick Charts**: Interactive OHLC charts with volume and basic technical overlays (SMA) using `pyqtgraph`.
- **Fundamental Analysis**: Automated extraction of P/E, Dividend Yield, Market Cap, Beta, and EPS.
- **Sentiment Analysis**: Integration of `vaderSentiment` for real-time news headline analysis (Bullish/Bearish/Neutral).
- **Institutional Risk Metrics**: Automated calculation of Portfolio Beta, Sharpe Ratio, Max Drawdown, and Annualized Volatility.
- **Stock Screener**: Multi-criteria screening engine with real-time result updates.
- **Data Export**: Professional Excel export functionality for screener results using `openpyxl`.

---

## 2. Remaining Professional Features (Backlog) 🛠️
Targeting "Institutional Terminal" standards:

### UI/UX & Layout
- [x] **Multi-Split Workspace Layout**: Implementation of a flexible `QSplitter` based system for AI Workspace (v1).
- [x] **Interactive AI Assistant (Command Center)**: Integrated LLM chat/terminal for natural language querying (v1).
- [x] **Technical Indicators Toggle**: A UI sidebar in the Chart view to toggle EMA, RSI, MACD, and Bollinger Bands.
- [x] **Portfolio Heatmaps**: Sized-by-weight heatmaps for sector exposure and performance visualization.

### Data & Analytics
- [x] **Global News Aggregator**: A dedicated macro news feed with keyword filtering and cross-source sentiment scoring.
- [x] **Advanced Screener Filters**: Technical signal filters (e.g., "Golden Cross", "RSI Oversold") and custom formula support.
- [x] **Historical Performance Attribution**: Tracking how individual trades contributed to portfolio P&L over time.
- [x] **Macro Event Calendar**: Integrated economic calendar (FED meetings, CPI releases) with impact alerts.

### Automation & Integration
- [x] **Seeking Alpha Cloud Sync (Refinement)**: Enhance Playwright automation for more robust handling of dynamic login modals.
- [x] **Alert Engine**: User-defined price/technical alerts with system tray notifications.

---

## 3. Design Proposal: Integrated AI "Command Split" 🤖

### Concept
A high-density terminal interface within the PyQt6 app that allows users to interact with an LLM to analyze the current workspace data or execute UI commands.

### Architecture
- **Component**: `AICommandWorkspace` (inherited from `QSplitter`).
- **Input**: A CLI-style input bar (`QLineEdit`) with auto-completion for tickers and commands.
- **Output**: A Markdown-rendered chat history (`QTextBrowser`) supporting tables and small sparkline charts.

### The "Multiple Splits" Design
1. **Dynamic Tiling**: Users can use a shortcut (e.g., `Ctrl+`) to split the AI terminal vertically or horizontally. This allows for:
   - *Split 1*: Analyzing Macro trends.
   - *Split 2*: Deep-diving into a specific ticker's 10-K sentiment.
2. **Context Awareness**: The LLM in each split can be "locked" to a specific context (e.g., `Context: Portfolio A`) or remain global.
3. **Application Control (Agentic AI)**:
   - Command: `/chart TSLA` -> App switches to Analysis tab and loads TSLA.
   - Command: `/risk report` -> LLM pulls data from `RiskService` and summarizes the portfolio's weaknesses.
   - Command: `/screen "Undervalued Tech"` -> App runs the screener with specific pre-defined AI parameters.

### Implementation Path
1. Create `sahelper/ui/ai_assistant.py`.
2. Implement a `ChatPanel` widget with a history and input area.
3. Wrap `ChatPanel` inside a `QSplitter` manager that handles the logic for adding/removing splits dynamically.
4. Connect the input to a background `AIService` that interfaces with OpenAI/Anthropic/Local LLMs.
