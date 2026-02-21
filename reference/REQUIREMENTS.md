# sahelper — Project Requirements

_Maintained by Agent 4 (Requirements Recorder). Last updated: 2026-02-22_

---

## 1. Project Overview

`sahelper` is a Python automation tool that authenticates with **Seeking Alpha** using stored credentials and automates portfolio management tasks. It uses Playwright for browser automation with a persistent Chromium session to avoid repeated logins. The target UI is Streamlit, providing an interactive interface for triggering automation tasks and entering stock data.

**Target Users**: Individual investors who use Seeking Alpha for portfolio tracking and want to automate repetitive portfolio management tasks.

**Key Business Problem**: Manually copying portfolios, adding stock entries, and managing positions on Seeking Alpha is time-consuming and error-prone.

---

## 2. Functional Requirements

### FR-001: Browser-Based Login to Seeking Alpha

- **Description**: The system must log into Seeking Alpha using email/password credentials stored in environment variables.
- **Inputs**: `SA_EMAIL`, `SA_PASSWORD` from `.env` file
- **Outputs**: Authenticated browser session with cookies persisted
- **Acceptance Criteria**: After login, navigating to `/account/portfolios` returns the portfolio list without a redirect to login
- **Status**: Implemented (`automation.py` → `login_google()`)

### FR-002: Persistent Browser Session

- **Description**: The browser session (cookies, local storage) must be saved between runs so the user does not need to log in every time.
- **Inputs**: Chromium `user_data/` directory
- **Outputs**: Reused session on next run if still valid
- **Acceptance Criteria**: Running the tool a second time skips the login step
- **Status**: Implemented (`automation.py` → `start_browser()`)

### FR-003: Copy Portfolio "Own" to "Own-Test"

- **Description**: The system must find the portfolio named "Own" and create a copy named "Own-Test".
- **Inputs**: Authenticated session on `/account/portfolios`
- **Outputs**: New portfolio "Own-Test" created on Seeking Alpha
- **Acceptance Criteria**: "Own-Test" appears in the portfolio list with the same holdings as "Own"
- **Status**: Partially Implemented (`automation.py` → `copy_portfolio()` — incomplete)

### FR-004: Add Stock Entry

- **Description**: The user can input a ticker symbol, quantity, and purchase date. The system records this entry.
- **Inputs**: Ticker (string), Quantity (integer), Purchase Date (date)
- **Outputs**: Entry appended to `stocks.csv`
- **Acceptance Criteria**: CSV file contains new row; API returns success message
- **Status**: Partially Implemented (`main.py` → `/add-stock`)

### FR-005: Streamlit User Interface

- **Description**: Replace the current Jinja2/HTML frontend with a Streamlit application providing controls for all automation actions and stock entry.
- **Inputs**: User interactions via Streamlit widgets
- **Outputs**: Triggers automation tasks; displays status/results
- **Acceptance Criteria**: User can: (1) trigger copy portfolio, (2) add a stock entry, (3) see status feedback — all through Streamlit
- **Status**: Planned

### FR-006: Structured Logging

- **Description**: All `print()` calls must be replaced with structured `logging` module calls with consistent format, log levels, and file output.
- **Inputs**: Application events
- **Outputs**: Log entries in `logs/sahelper.log` and stdout
- **Acceptance Criteria**: No bare `print()` calls in any `.py` file; log file created on startup
- **Status**: Planned

---

## 3. Non-Functional Requirements

### NFR-001: File Size Limit

- No Python source file may exceed **1500 lines**
- Enforced per the `file_size_limit` skill

### NFR-002: Credential Security

- Credentials (`SA_EMAIL`, `SA_PASSWORD`) must only be read from `.env`, never hardcoded
- Credentials must never appear in log output

### NFR-003: Session Reliability

- If a CAPTCHA is detected, the system must notify the user and wait (up to 2 minutes) for manual resolution
- Session must recover gracefully from expired cookies

### NFR-004: Code Quality

- All files must have type annotations and docstrings on public methods
- No bare `except:` blocks
- PEP 8 compliance

---

## 4. Technical Constraints

| Constraint | Value |
|---|---|
| Python version | 3.14 |
| Browser engine | Chromium (via Playwright) |
| Key libraries | FastAPI, Uvicorn, Playwright (async), python-dotenv, Streamlit (planned) |
| Session storage | `user_data/` directory (Chromium persistent context) |
| Credentials | `.env` file: `SA_EMAIL`, `SA_PASSWORD` |
| Log output | `logs/sahelper.log` + stdout |
| Max file size | 1500 lines |

---

## 5. External Integrations

### Seeking Alpha (seekingalpha.com)

- **Auth method**: Email/password login via web form
- **Data exchanged**: Portfolio list, portfolio holdings, stock entries
- **Failure modes**: CAPTCHA, session expiry, page layout changes (selectors breaking)
- **No official API**: All interactions via browser automation

---

## 6. UI Requirements (Streamlit — Planned)

### Page: Main Dashboard

- **Sidebar**: App title, navigation links
- **Section 1 — Portfolio Actions**:
  - Button: "Copy Portfolio (Own → Own-Test)"
  - Status indicator: shows last run result
- **Section 2 — Add Stock Entry**:
  - Input: Ticker (text)
  - Input: Quantity (number)
  - Input: Purchase Date (date picker)
  - Button: "Add Entry"
  - Display: Confirmation message

---

## 7. Out of Scope

- Real-time portfolio value tracking
- Multi-user support / authentication within the tool itself
- Any Seeking Alpha API that requires a paid subscription
- Mobile application

---

## Changelog

| Date | Change | Agent |
|---|---|---|
| 2026-02-22 | Initial requirements capture from `main.py` and `automation.py` | Agent 4 |
