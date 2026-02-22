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
    from sahelper.services.alert_service import AlertService

    apply_stylesheet(app, theme='dark_teal.xml')
    init_db()

    market_service = MarketDataService()
    alert_service = AlertService(market_service)
    
    from sahelper.services.calendar_service import CalendarService
    calendar_service = CalendarService()
    
    from sahelper.services.attribution_service import AttributionService
    attribution_service = AttributionService()
    # Add some sample trades for demonstration
    attribution_service.record_trade("SPY", 10, 480.0)
    attribution_service.record_trade("NVDA", 5, 600.0)
    attribution_service.record_trade("TSLA", 20, 190.0)

    window = SAHelperWindow(alert_service=alert_service, attribution_service=attribution_service)
    window.show()
    
    def on_alert(ticker, cond, price):
        if hasattr(window, 'view_alerts'):
            window.view_alerts.refresh_table()
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(window)
        msg.setWindowTitle("PRICE ALERT!")
        msg.setText(f"<b>{ticker}</b> has crossed your alert level!")
        msg.setInformativeText(f"Condition: {cond} | Current Price: ${price:,.2f}")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.show()

    alert_service.alert_triggered.connect(on_alert)
    # 1. Macro View
    if hasattr(window, 'view_market'):
         market_service.data_updated.connect(window.view_market.update_macro_data)
         market_service.news_updated.connect(window.view_market.update_news)
         calendar_service.events_ready.connect(window.view_market.update_calendar)

    # 2. Overview Dashboard
    def update_overview(data):
        if data and hasattr(window, 'view_overview'):
            # SPY data
            spy = next((d for d in data if d['ticker'] == 'SPY'), data[0] if data else None)
            if spy:
                 window.view_overview.update_performance(spy["history"])
    market_service.data_updated.connect(update_overview)

    # Start Background Tasks
    loop.create_task(market_service.run_live_feed())
    loop.create_task(calendar_service.fetch_events())
    loop.create_task(attribution_service.calculate_attribution())

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
