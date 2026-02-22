from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableView, 
    QPushButton, QLineEdit, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSlot
from PyQt6.QtGui import QColor

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
                if val > 0: return QColor("#00ff88") # Emerald
                if val < 0: return QColor("#ff4444") # Crimson
            if col == 7:
                rating = item.get("rating", "")
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
from sahelper.services.risk_service import RiskService
import asyncio
from qasync import asyncSlot

from .styles import AppColors, AppStyles

class PortfolioWidget(QWidget):
    """Professional grid view for portfolio holdings."""
    def __init__(self):
        super().__init__()
        self.automator = AutomationService()
        self.risk_service = RiskService()
        self.risk_service.metrics_ready.connect(self.on_risk_metrics_ready)
        self.risk_service.error_occurred.connect(self.on_risk_error)
        
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Header Area
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("My Portfolio")
        self.lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        
        # URL Input Field
        header_layout.addWidget(QLabel("Portfolio URL:"))
        self.input_url = QLineEdit()
        self.input_url.setText("https://seekingalpha.com/account/portfolio/summary?portfolioId=62720994")
        self.input_url.setMinimumWidth(400)
        self.input_url.setPlaceholderText("Enter Seeking Alpha Portfolio Summary URL...")
        self.input_url.setStyleSheet(AppStyles.INPUT)
        header_layout.addWidget(self.input_url)

        self.btn_sync = QPushButton("Sync with Seeking Alpha")
        self.btn_sync.clicked.connect(self.on_sync_clicked)
        self.btn_sync.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        header_layout.addWidget(self.btn_sync)

        self.btn_risk = QPushButton("Run Risk Analysis")
        self.btn_risk.clicked.connect(self.on_risk_clicked)
        self.btn_risk.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #005a9e;
            }}
        """)
        header_layout.addWidget(self.btn_risk)

        self.btn_heatmap = QPushButton("Toggle Heatmap")
        self.btn_heatmap.clicked.connect(self.on_toggle_heatmap)
        self.btn_heatmap.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.BG_CARD};
                color: {AppColors.TEXT_PRIMARY};
                border: 1px solid {AppColors.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BG_INPUT};
            }}
        """)
        header_layout.addWidget(self.btn_heatmap)

        self.btn_clear = QPushButton("Clear All Data")
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        # Custom red style for clear button
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_RED};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #d50000;
            }}
        """)
        header_layout.addWidget(self.btn_clear)

        layout.addLayout(header_layout)

        # 1.5 Heatmap Area (Togglable)
        from .heatmap import PortfolioHeatmapWidget
        self.heatmap = PortfolioHeatmapWidget()
        self.heatmap.setVisible(False)
        layout.addWidget(self.heatmap)

        # 2. Main Content: Table + Side Detail
        content_h = QHBoxLayout()
        content_h.setSpacing(20)
        
        # 3. Data Table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(False) # Cleaner look
        self.table_view.setStyleSheet(AppStyles.TABLE)
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.clicked.connect(self.on_row_selected)
        
        content_h.addWidget(self.table_view, 7) # 70% width

        # 4. Side Detail Panel
        self.detail_panel = QFrame()
        self.detail_panel.setFixedWidth(320)
        self.detail_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BG_SIDEBAR};
                border-left: 1px solid {AppColors.BORDER};
            }}
        """)
        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_detail_ticker = QLabel("Select a Ticker")
        self.lbl_detail_ticker.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        detail_layout.addWidget(self.lbl_detail_ticker)
        
        from .charts import StockChartWidget
        self.detail_chart = StockChartWidget(title="Price Trend", background=AppColors.BG_SIDEBAR)
        detail_layout.addWidget(self.detail_chart)
        
        self.lbl_detail_stats = QLabel("Performance details will appear here.")
        self.lbl_detail_stats.setWordWrap(True)
        self.lbl_detail_stats.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; line-height: 1.4; font-size: 13px;")
        detail_layout.addWidget(self.lbl_detail_stats)
        
        detail_layout.addStretch()
        content_h.addWidget(self.detail_panel, 3) # 30% width

        layout.addLayout(content_h)

    def on_row_selected(self, index: QModelIndex):
        """Update detail panel when a portfolio row is clicked."""
        row = index.row()
        item = self.model._data[row]
        ticker = item.get("ticker")
        
        self.lbl_detail_ticker.setText(ticker)
        
        # Mock history for the detail chart
        import random
        base = item.get("current_price", 100)
        mock_history = [base * (1 + (random.random() - 0.5) * 0.1) for _ in range(50)]
        self.detail_chart.update_chart(mock_history)
        
        stats_text = (
            f"<p><b>Quantity:</b> <span style='color: white;'>{item.get('quantity')}</span></p>"
            f"<p><b>Avg Cost:</b> <span style='color: white;'>${item.get('avg_cost'):.2f}</span></p>"
            f"<p><b>Current Price:</b> <span style='color: white;'>${item.get('current_price'):.2f}</span></p>"
            f"<p><b>Change:</b> <span style='color: {AppColors.ACCENT_GREEN if item.get('change_pct',0) > 0 else AppColors.ACCENT_RED};'>{item.get('change_pct')*100:+.2f}%</span></p>"
        )
        self.lbl_detail_stats.setText(stats_text)

    def on_toggle_heatmap(self):
        is_visible = not self.heatmap.isVisible()
        self.heatmap.setVisible(is_visible)
        if is_visible:
            self.update_heatmap_data()

    def update_heatmap_data(self):
        if not hasattr(self, 'model'): return
        
        heatmap_data = []
        for item in self.model._data:
            heatmap_data.append({
                "ticker": item["ticker"],
                "market_value": item["quantity"] * item["current_price"],
                "change_pct": item["change_pct"],
                "sector": item["sector"]
            })
        self.heatmap.set_data(heatmap_data)

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
                    "change_pct": stock.daily_change_pct if stock else 0.0,
                    "sector": stock.sector if stock and stock.sector else "N/A",
                    "rating": stock.rating if stock and stock.rating else "HOLD"
                })
            
            self.model = PortfolioModel(data)
            self.table_view.setModel(self.model)
            self.update_heatmap_data()
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

    def on_risk_clicked(self):
        """Gather holdings and trigger risk calculation."""
        self.btn_risk.setEnabled(False)
        self.btn_risk.setText("Calculating Risk...")
        
        # Gather holdings from the model data
        holdings = []
        for item in self.model._data:
            holdings.append({
                "ticker": item["ticker"],
                "value": item["quantity"] * item["current_price"]
            })
        
        # Async call
        asyncio.create_task(self.risk_service.calculate_risk(holdings))

    @pyqtSlot(dict)
    def on_risk_metrics_ready(self, metrics):
        self.btn_risk.setEnabled(True)
        self.btn_risk.setText("Run Risk Analysis")
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Portfolio Risk Analysis")
        msg.setText("<h3>Portfolio Risk Metrics (vs S&P 500)</h3>")
        
        details = (
            f"<b>Total Value:</b> {metrics.get('Total Value')}<br>"
            f"<b>Beta:</b> {metrics.get('Beta')} (Market Volatility)<br>"
            f"<b>Sharpe Ratio:</b> {metrics.get('Sharpe Ratio')} (Risk-Adjusted Return)<br>"
            f"<b>Max Drawdown:</b> {metrics.get('Max Drawdown')} (1Y Worst Loss)<br>"
            f"<b>Volatility:</b> {metrics.get('Volatility')} (Annualized)<br>"
        )
        msg.setInformativeText(details)
        msg.exec()

    @pyqtSlot(str)
    def on_risk_error(self, error):
        self.btn_risk.setEnabled(True)
        self.btn_risk.setText("Run Risk Analysis")
        QMessageBox.critical(self, "Risk Analysis Error", f"Failed to calculate metrics: {error}")
