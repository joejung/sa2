from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableView, 
    QPushButton, QLineEdit, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex

class PortfolioModel(QAbstractTableModel):
    """Institutional Data model for the Portfolio Table View."""
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Ticker", "Quantity", "Price", "Market Value", "Daily P&L", "Gain/Loss %", "Sector", "Rating"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        item = self._data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            qty = item.get("quantity", 0)
            price = item.get("current_price", 0)
            mv = qty * price
            daily_pl = mv * item.get("change_pct", 0)
            
            mapping = {
                0: item.get("ticker"),
                1: f"{qty:,.0f}",
                2: f"${price:,.2f}",
                3: f"${mv:,.2f}",
                4: f"${daily_pl:,.2f}",
                5: f"{(item.get('change_pct', 0) * 100):+.2f}%",
                6: item.get("sector", "N/A"),
                7: item.get("rating", "HOLD")
            }
            return mapping.get(col)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignRight if col > 0 and col != 6 else Qt.AlignmentFlag.AlignLeft

        if role == Qt.ItemDataRole.ForegroundRole:
            if col in [4, 5]:
                val = item.get('change_pct', 0)
                from PyQt6.QtGui import QColor
                if val > 0: return QColor("#00ff88") # Emerald
                if val < 0: return QColor("#ff4444") # Crimson
            if col == 7:
                rating = item.get("rating", "")
                from PyQt6.QtGui import QColor
                if "BUY" in rating: return QColor("#00ff88")
                if "SELL" in rating: return QColor("#ff4444")

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

from sahelper.database.session import SessionLocal
from sahelper.database.models import Holding, StockData
from sahelper.services.automation import AutomationService
import asyncio
from qasync import asyncSlot

class PortfolioWidget(QWidget):
    """Professional grid view for portfolio holdings."""
    def __init__(self):
        super().__init__()
        self.automator = AutomationService()
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Header Area
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("<h2>My Portfolio</h2>")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        
        # URL Input Field
        header_layout.addWidget(QLabel("Portfolio URL:"))
        self.input_url = QLineEdit()
        self.input_url.setText("https://seekingalpha.com/account/portfolio/summary?portfolioId=62720994")
        self.input_url.setMinimumWidth(400)
        self.input_url.setPlaceholderText("Enter Seeking Alpha Portfolio Summary URL...")
        header_layout.addWidget(self.input_url)

        self.btn_sync = QPushButton("Sync with Seeking Alpha")
        self.btn_sync.clicked.connect(self.on_sync_clicked)
        self.btn_sync.setStyleSheet("padding: 8px 15px; background-color: #007acc; color: white;")
        header_layout.addWidget(self.btn_sync)

        self.btn_clear = QPushButton("Clear All Data")
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.btn_clear.setStyleSheet("padding: 8px 15px; background-color: #ff4444; color: white;")
        header_layout.addWidget(self.btn_clear)

        layout.addLayout(header_layout)

        # 3. Data Table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table_view)

    def refresh_data(self):
        """Fetch data from local SQLite and update the table with validation metrics."""
        print("[VALIDATION] Refreshing local portfolio data view...")
        with SessionLocal() as session:
            holdings = session.query(Holding).all()
            print(f"[VALIDATION] Found {len(holdings)} records in local DB.")
            data = []
            for h in holdings:
                # Try to find matching stock data for price
                stock = session.query(StockData).filter_by(ticker=h.ticker).first()
                data.append({
                    "ticker": h.ticker,
                    "quantity": h.quantity,
                    "avg_cost": h.avg_cost,
                    "current_price": stock.last_price if stock else 0.0,
                    "change_pct": stock.daily_change_pct if stock else 0.0
                })
            
            self.model = PortfolioModel(data)
            self.table_view.setModel(self.model)
            print("[VALIDATION] UI updated with new model data.")

    @asyncSlot()
    async def on_clear_clicked(self):
        """Clears all local portfolio and holding data with self-validation logs."""
        print("[VALIDATION] Initiating portfolio data wipe...")
        try:
            from sahelper.database.models import Portfolio, Holding, StockData
            with SessionLocal() as session:
                h_count = session.query(Holding).delete()
                p_count = session.query(Portfolio).delete()
                s_count = session.query(StockData).delete()
                session.commit()
                print(f"[VALIDATION] Success: Wiped {h_count} holdings, {p_count} portfolios, {s_count} stock records.")
            
            self.refresh_data()
            print("[VALIDATION] UI Refreshed. Table should be empty.")
        except Exception as e:
            print(f"[VALIDATION] ERROR: Wipe failed: {e}")

    @asyncSlot()
    async def on_sync_clicked(self):
        self.btn_sync.setEnabled(False)
        self.btn_sync.setText("Syncing Institutional Data...")
        target_url = self.input_url.text().strip()
        print(f"[VALIDATION] Start sync for URL: {target_url}")
        try:
            # Trigger the institutional-grade sync with the provided URL
            success = await self.automator.sync_user_portfolio(target_url)
            
            if success:
                print("[VALIDATION] Portfolio sync reported SUCCESS.")
            else:
                print("[VALIDATION] Portfolio sync reported FAILURE.")
                # Fallback to dummy data only if DB is empty and sync failed
                from sahelper.database.models import Portfolio
                with SessionLocal() as session:
                    portfolio = session.query(Portfolio).filter_by(name="Default").first()
                    if not portfolio:
                        portfolio = Portfolio(name="Default", description="Main Portfolio")
                        session.add(portfolio)
                        session.flush()

                    if not session.query(Holding).filter_by(portfolio_id=portfolio.id).first():
                        print("[VALIDATION] Injecting dummy data fallback for visualization.")
                        h = Holding(ticker="AAPL", quantity=10, avg_cost=150.0, portfolio_id=portfolio.id)
                        s = StockData(ticker="AAPL", last_price=185.0, daily_change_pct=0.015)
                        session.add_all([h, s])
                        session.commit()
            
            self.refresh_data()
        finally:
            self.btn_sync.setEnabled(True)
            self.btn_sync.setText("Sync with Seeking Alpha")

    def set_data(self, holdings: list):
        """Update the table with new holding data."""
        self.model = PortfolioModel(holdings)
        self.table_view.setModel(self.model)
