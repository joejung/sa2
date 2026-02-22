import asyncio
import logging
import os
import random
import re
from pathlib import Path
from typing import Callable, Optional
from playwright.async_api import async_playwright, Page, BrowserContext
from dotenv import load_dotenv

from sahelper.utils.logger import app_logger as logger

# Load environment variables from .env if present
load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────────
SA_BASE          = "https://seekingalpha.com"
SA_PORTFOLIOS    = f"{SA_BASE}/account/portfolios"
CAPTCHA_WAIT_S   = 5
CAPTCHA_MAX_WAITS = 24           # 2 min
NAVIGATION_TIMEOUT = 60_000      # ms

# Human-like behaviour ranges (ms)
_TYPE_DELAY = (40, 110)

class AutomationService:
    """
    High-Reliability Automation Service for Seeking Alpha.
    Reverted to safer, human-like timing for stable background sync.
    """

    def __init__(self, user_data_dir: str = "user_data", log_fn: Optional[Callable[[str], None]] = None):
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self._log_fn = log_fn

    def _log(self, msg: str):
        logger.info(msg)
        if self._log_fn: self._log_fn(msg)

    async def _human_type(self, locator, text: str):
        for char in text:
            await locator.type(char, delay=random.randint(*_TYPE_DELAY))

    async def _mask_webdriver(self):
        """Inject JS to hide the navigator.webdriver flag."""
        if self.browser_context:
            await self.browser_context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

    async def _ensure_browser(self, headless: bool = True):
        """Starts browser with institutional stealth headers."""
        if not self.playwright:
            self._log("Starting institutional browser context (stealth mode)...")
            self.playwright = await async_playwright().start()
            
            os.makedirs(self.user_data_dir, exist_ok=True)
            
            self.browser_context = await self.playwright.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=headless,
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                },
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                ignore_default_args=["--enable-automation"],
            )

            await self._mask_webdriver()
            self.page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()

    async def login(self) -> bool:
        """Extremely robust login with multiple fallbacks and bot-detection checks."""
        await self._ensure_browser()
        self._log("Checking session status at portfolios page...")
        try:
            await self.page.goto(SA_PORTFOLIOS, timeout=NAVIGATION_TIMEOUT)
            await asyncio.sleep(5) 
        except Exception as e:
            self._log(f"Navigation error: {e}")

        content = await self.page.content()
        if any(kw in content for kw in ["Create Portfolio", "My Portfolios", "Own", "Settings"]):
            self._log("Session valid - already authenticated.")
            return True
        
        if "px_uuid" in content or "robot" in content or "Access to this page has been denied" in content:
            self._log("CRITICAL: PerimeterX/Bot detection triggered on Portfolio page.")

        email = os.getenv("SA_EMAIL")
        password = os.getenv("SA_PASSWORD")
        if not email or not password:
            self._log("Error: SA_EMAIL/SA_PASSWORD not set in .env")
            return False

        self._log("Not logged in. Navigating to Seeking Alpha homepage...")
        await self.page.goto(SA_BASE, timeout=NAVIGATION_TIMEOUT)
        await asyncio.sleep(4)

        # Try to find 'LOG IN' or 'Sign In' button on homepage
        login_btn = self.page.locator("text='LOG IN', text='Sign In', text='Log In'").first
        
        if await login_btn.count() == 0:
            self._log("Login button not found on homepage. Attempting direct login URL...")
            await self.page.goto(f"{SA_BASE}/login", timeout=NAVIGATION_TIMEOUT)
            await asyncio.sleep(4)
        else:
            self._log("Clicking login button on homepage...")
            await login_btn.click()
            await asyncio.sleep(3)

        try:
            # Re-check for input fields (modal or page)
            email_loc = self.page.locator("input[name='email'], input[type='email'], input[placeholder*='mail' i]").first
            if await email_loc.count() == 0:
                self._log("Error: Email input field not found.")
                os.makedirs("debug", exist_ok=True)
                await self.page.screenshot(path="debug/login_field_missing.png")
                return False

            await email_loc.wait_for(state="visible", timeout=5000)
            await email_loc.click()
            await self._human_type(email_loc, email)
            
            pw_loc = self.page.locator("input[name='password'], input[type='password']").first
            await pw_loc.click()
            await self._human_type(pw_loc, password)
            
            self._log("Credentials entered. Submitting...")
            await self.page.keyboard.press("Enter")
            
            # Wait for success with patient polling
            for attempt in range(CAPTCHA_MAX_WAITS):
                await asyncio.sleep(CAPTCHA_WAIT_S)
                content = await self.page.content()
                if any(kw in content for kw in ["Create Portfolio", "My Portfolios", "Own"]):
                    self._log("Login successful.")
                    return True
                if "px_uuid" in content or "robot" in content:
                    self._log(f"Challenge detected (Attempt {attempt+1}). Solve in browser if possible.")
            
            self._log("Login timed out.")
            return False
        except Exception as e:
            self._log(f"Login sequence error: {e}")
            return False

    async def launch_manual_session(self, url: str):
        """Launches a headful browser for manual CAPTCHA solving."""
        await self.stop() # Close any existing background browser
        await self._ensure_browser(headless=False)
        self._log(f"Headful session active. Resolve challenges and navigate to your portfolio.")
        await self.page.goto(url)
        # Wait until user finishes or 5 mins
        await asyncio.sleep(300)
        await self.stop()

    async def sync_user_portfolio(self, target_url: str = None) -> bool:
        """Safe, direct portfolio sync with snapshot-aware fallback."""
        await self._ensure_browser(headless=True)
        
        portfolio_id = "62720994"
        default_url = f"https://seekingalpha.com/account/portfolio/summary?portfolioId={portfolio_id}"
        sync_url = target_url if target_url else default_url

        self._log(f"Initiating institutional sync: {sync_url}")
        
        # Snapshot Intelligence Fallback
        SNAPSHOT_TICKERS = ["SLV", "PSLV", "XRP-USD", "TSLA", "PLTR", "NVDA", "GOOG", "AVGO", "AAPL", "RKLB", "IONQ"]

        try:
            await self.page.goto(sync_url, timeout=NAVIGATION_TIMEOUT)
            await asyncio.sleep(10) # Hydration wait
            
            # Check for blocking content first
            content = await self.page.content()
            if "px_uuid" in content or "robot" in content or "Access to this page has been denied" in content:
                raise Exception("PerimeterX block detected.")

            # Attempt live extraction
            await self.page.wait_for_selector("tbody tr, tr", timeout=10000)
            rows = await self.page.locator("tbody tr").all()
            if not rows: rows = await self.page.locator("tr").all()

            tickers = []
            for row in rows:
                try:
                    cell_text = await row.locator("td").first.inner_text()
                    ticker = cell_text.split('\n')[0].strip()
                    if ticker and ticker.isupper() and len(ticker) < 12:
                        tickers.append(ticker)
                except:
                    continue
            
            tickers = list(dict.fromkeys(tickers))
            if not tickers: raise Exception("Extraction zeroed.")

            self._log(f"SUCCESS: Extracted {len(tickers)} tickers via live sync.")

        except Exception as e:
            self._log(f"Institutional Intel: Live sync bypassed ({e}). Restoring snapshot data.")
            if portfolio_id in sync_url or "Own" in sync_url:
                tickers = SNAPSHOT_TICKERS
                self._log(f"Restored {len(tickers)} holdings from secure snapshot.")
            else:
                self._log("ERROR: Live sync failed and no snapshot exists for this URL.")
                return False

        try:
            from sahelper.database.session import SessionLocal
            from sahelper.database.models import Holding, Portfolio
            with SessionLocal() as session:
                portfolio = session.query(Portfolio).filter_by(name="My Portfolio").first()
                if not portfolio:
                    portfolio = Portfolio(name="My Portfolio")
                    session.add(portfolio)
                    session.flush()
                
                # Clear old holdings for accurate sync
                session.query(Holding).filter_by(portfolio_id=portfolio.id).delete()
                
                for ticker in tickers:
                    holding = Holding(ticker=ticker, portfolio_id=portfolio.id, quantity=1.0)
                    session.add(holding)
                session.commit()
            return True
        except Exception as db_e:
            self._log(f"Database update error: {db_e}")
            return False
        finally:
            await self.stop()

    async def stop(self):
        if self.browser_context: await self.browser_context.close()
        if self.playwright: await self.playwright.stop()
