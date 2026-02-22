import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
import yfinance as yf
from .styles import AppColors, AppStyles

class ScreenerWidget(QWidget):
    """Stock Screener based on fundamental criteria."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        lbl_title = QLabel("Stock Screener")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        layout.addWidget(lbl_title)

        # Filters Area
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border-radius: 8px; border: 1px solid {AppColors.BORDER};")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)

        # Sector Filter
        self.combo_sector = QComboBox()
        self.combo_sector.addItems(["All Sectors", "Technology", "Healthcare", "Financial", "Energy", "Consumer Cyclical"])
        self.combo_sector.setStyleSheet(AppStyles.INPUT)
        filter_layout.addWidget(QLabel("Sector:"))
        filter_layout.addWidget(self.combo_sector)

        # PE Ratio Max
        self.spin_pe = QDoubleSpinBox()
        self.spin_pe.setRange(0, 200)
        self.spin_pe.setValue(30)
        self.spin_pe.setStyleSheet(AppStyles.INPUT)
        filter_layout.addWidget(QLabel("Max P/E:"))
        filter_layout.addWidget(self.spin_pe)

        # Div Yield Min
        self.spin_yield = QDoubleSpinBox()
        self.spin_yield.setRange(0, 20)
        self.spin_yield.setValue(0.0)
        self.spin_yield.setSuffix("%")
        self.spin_yield.setStyleSheet(AppStyles.INPUT)
        filter_layout.addWidget(QLabel("Min Yield:"))
        filter_layout.addWidget(self.spin_yield)

        # Technical Signal
        self.combo_signal = QComboBox()
        self.combo_signal.addItems(["No Signal", "Golden Cross", "RSI Oversold", "Price > SMA50"])
        self.combo_signal.setStyleSheet(AppStyles.INPUT)
        filter_layout.addWidget(QLabel("Signal:"))
        filter_layout.addWidget(self.combo_signal)

        # Run Button
        self.btn_run = QPushButton("Run Screen")
        self.btn_run.clicked.connect(self.run_screener)
        self.btn_run.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        filter_layout.addWidget(self.btn_run)
        
        # Export Button
        self.btn_export = QPushButton("Export Excel")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        self.btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_GREEN};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #00893b;
            }}
        """)
        filter_layout.addWidget(self.btn_export)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Ticker", "Name", "Price", "P/E", "Yield"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(AppStyles.TABLE)
        layout.addWidget(self.table)

    def export_results(self):
        """Export the current table to an Excel file using openpyxl."""
        import openpyxl
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Screener Results"
            
            # Header
            headers = ["Ticker", "Name", "Price", "P/E", "Yield"]
            ws.append(headers)
            
            # Rows
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    row_data.append(self.table.item(row, col).text())
                ws.append(row_data)
                
            wb.save("screener_results.xlsx")
            QMessageBox.information(self, "Export Successful", "Results saved to 'screener_results.xlsx'")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    def run_screener(self):
        """Execute the screen (Simulated on a subset of stocks for performance)."""
        self.btn_run.setEnabled(False)
        self.btn_run.setText("Scanning...")
        self.btn_export.setEnabled(False)
        self.table.setRowCount(0)
        
        # Async call
        asyncio.create_task(self._scan_stocks())

    async def _scan_stocks(self):
        try:
            # Universe of stocks to scan
            universe = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "JNJ",
                "WMT", "PG", "XOM", "MA", "UNH", "HD", "CVX", "KO", "MRK", "PEP",
                "T", "VZ", "INTC", "CSCO", "PFE", "BAC", "AMD", "NFLX", "ADBE", "CRM"
            ]
            
            loop = asyncio.get_event_loop()
            target_signal = self.combo_signal.currentText()
            
            # Fetch data efficiently
            def fetch_all():
                data = {}
                # yf.download is faster for multiple tickers history
                # We need enough history for SMA200 (approx 1 year)
                hist = yf.download(universe, period="1y", group_by='ticker', silent=True)
                
                # Also fetch info for fundamentals
                # Info is slow, so we only fetch it for tickers that pass technical filter?
                # For this demo, let's just fetch all info in one go if possible
                tickers_obj = yf.Tickers(" ".join(universe))
                return hist, tickers_obj.tickers

            hist_data, tickers_dict = await loop.run_in_executor(None, fetch_all)
            
            results = []
            target_sector = self.combo_sector.currentText()
            max_pe = self.spin_pe.value()
            min_yield = self.spin_yield.value() / 100.0
            
            for symbol in universe:
                try:
                    # 1. Technical Filter
                    df = hist_data[symbol]
                    if df.empty: continue
                    
                    passed_tech = True
                    if target_signal == "Golden Cross":
                        sma50 = df['Close'].rolling(window=50).mean()
                        sma200 = df['Close'].rolling(window=200).mean()
                        # Cross today or yesterday
                        if not (sma50.iloc[-1] > sma200.iloc[-1] and sma50.iloc[-2] <= sma200.iloc[-2]):
                            passed_tech = False
                    elif target_signal == "RSI Oversold":
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        if rsi.iloc[-1] >= 30:
                            passed_tech = False
                    elif target_signal == "Price > SMA50":
                        sma50 = df['Close'].rolling(window=50).mean()
                        if df['Close'].iloc[-1] <= sma50.iloc[-1]:
                            passed_tech = False
                    
                    if not passed_tech: continue

                    # 2. Fundamental Filter
                    info = tickers_dict[symbol].info
                    sector = info.get('sector', 'Unknown')
                    pe = info.get('trailingPE', 999)
                    div_yield = info.get('dividendYield', 0) or 0
                    
                    if target_sector != "All Sectors" and sector != target_sector:
                        continue
                    if pe > max_pe:
                        continue
                    if div_yield < min_yield:
                        continue
                        
                    results.append({
                        "Ticker": symbol,
                        "Name": info.get('shortName', ''),
                        "Price": f"${info.get('currentPrice', 0):.2f}",
                        "P/E": f"{pe:.2f}",
                        "Yield": f"{div_yield*100:.2f}%"
                    })
                except Exception as e:
                    print(f"Error scanning {symbol}: {e}")
                    continue
            
            # Update UI
            self.table.setRowCount(len(results))
            for i, res in enumerate(results):
                self.table.setItem(i, 0, QTableWidgetItem(res["Ticker"]))
                self.table.setItem(i, 1, QTableWidgetItem(res["Name"]))
                self.table.setItem(i, 2, QTableWidgetItem(res["Price"]))
                self.table.setItem(i, 3, QTableWidgetItem(res["P/E"]))
                self.table.setItem(i, 4, QTableWidgetItem(res["Yield"]))
            
            if results:
                self.btn_export.setEnabled(True)
                
        except Exception as e:
            print(f"Screener error: {e}")
        finally:
            self.btn_run.setEnabled(True)
            self.btn_run.setText("Run Screen")
