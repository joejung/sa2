import sys
import logging
import asyncio
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from qasync import QEventLoop

# Initialize Database
from sahelper.database.session import init_db
from sahelper.ui.main_window import SAHelperWindow
from sahelper.services.market_data import MarketDataService

logging.basicConfig(level=logging.INFO)

async def main_async():
    app = QApplication(sys.argv)
    loop = asyncio.get_event_loop()
    
    # Apply Enterprise Theme
    apply_stylesheet(app, theme='dark_teal.xml')
    
    # Initialize DB (Create tables)
    init_db()

    # Launch UI
    window = SAHelperWindow()
    window.show()

    # Start Institutional Data Feed
    market_service = MarketDataService()
    
    # Initialize Alerting
    from sahelper.services.alert_service import AlertService
    alert_service = AlertService(market_service)
    
    def on_alert(ticker, cond, price):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(window)
        msg.setWindowTitle("PRICE ALERT!")
        msg.setText(f"<b>{ticker}</b> has crossed your alert level!")
        msg.setInformativeText(f"Condition: {cond} | Current Price: ${price:,.2f}")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.show()

    alert_service.alert_triggered.connect(on_alert)
    
    # Add a sample alert for SPY (e.g., if it goes above a high value)
    alert_service.add_alert("SPY", ">", 500.0)
    alert_service.add_alert("QQQ", ">", 400.0)

    # 1. Update Macro Dashboard (Index Cards/Sparklines)
    # Ensure view_market exists and has the slot
    if hasattr(window, 'view_market'):
        market_service.data_updated.connect(window.view_market.update_macro_data)
    
    # 2. Update Overview Dashboard (Portfolio Chart)
    def update_overview(data):
        if data and hasattr(window, 'view_overview'):
            spy = data[0] # SPY
            # Assuming update_performance expects a list of floats
            window.view_overview.update_performance(spy["history"])
    market_service.data_updated.connect(update_overview)

    # Start the feed
    loop.create_task(market_service.run_live_feed())
    
    # Run the event loop
    while True:
        await asyncio.sleep(0.01)
        app.processEvents()

def main():
    # Use qasync for proper asyncio + PyQt6 integration
    import sys
    from PyQt6.QtWidgets import QApplication
    from qasync import QEventLoop, QApplication as QAsyncApplication

    app = QAsyncApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    from qt_material import apply_stylesheet
    from sahelper.database.session import init_db
    from sahelper.ui.main_window import SAHelperWindow
    from sahelper.services.market_data import MarketDataService

    apply_stylesheet(app, theme='dark_teal.xml')
    init_db()

    window = SAHelperWindow()
    window.show()

    market_service = MarketDataService()
    
    # Connect Signals
    # 1. Macro View
    if hasattr(window, 'view_market'):
         market_service.data_updated.connect(window.view_market.update_macro_data)

    # 2. Overview Dashboard
    def update_overview(data):
        if data and hasattr(window, 'view_overview'):
            # SPY data
            spy = next((d for d in data if d['ticker'] == 'SPY'), data[0] if data else None)
            if spy:
                 window.view_overview.update_performance(spy["history"])
    market_service.data_updated.connect(update_overview)

    # Start Background Task
    loop.create_task(market_service.run_live_feed())

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
