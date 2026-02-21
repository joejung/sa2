import sys
import logging
import asyncio
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from qasync import QEventLoop

# Initialize Database
from sahelper.database.session import init_db
from sahelper.ui.main_window import SAHelperWindow

logging.basicConfig(level=logging.INFO)

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Apply Enterprise Theme
    apply_stylesheet(app, theme='dark_teal.xml')  # Or similar dark theme
    
    # Initialize DB (Create tables)
    init_db()

    # Launch UI
    window = SAHelperWindow()
    window.show()

    # Start Institutional Data Feed
    from sahelper.services.market_data import MarketDataService
    market_service = MarketDataService()
    market_service.data_updated.connect(window.view_dashboard.update_macro_data)
    loop.create_task(market_service.run_live_feed())
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
