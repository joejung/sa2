import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSlot

from .charts import AdvancedChartWidget
from .styles import AppColors
from sahelper.services.analysis_service import AnalysisService

class StockDetailWidget(QWidget):
    """Detailed view for a single stock ticker with metrics and charts."""
    def __init__(self):
        super().__init__()
        self.service = AnalysisService()
        self.service.chart_data_ready.connect(self.on_chart_data)
        self.service.indicators_ready.connect(self.on_indicators)
        self.service.fundamentals_ready.connect(self.on_fundamentals)
        self.service.news_ready.connect(self.on_news)
        
        self.init_ui()
        self.current_indicators = {}

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Ticker Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border-radius: 10px; border: 1px solid {AppColors.BORDER};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_ticker = QLabel("LOADING...")
        self.lbl_ticker.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {AppColors.TEXT_PRIMARY};")
        
        self.lbl_name = QLabel("")
        self.lbl_name.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 18px; margin-left: 10px; font-weight: 400;")
        
        header_layout.addWidget(self.lbl_ticker)
        header_layout.addWidget(self.lbl_name)
        header_layout.addStretch()
        
        # Current Price
        self.lbl_price = QLabel("---")
        self.lbl_price.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        
        header_layout.addWidget(self.lbl_price)
        
        layout.addWidget(header_frame)

        # 2. Middle Section: Advanced Chart
        chart_frame = QFrame()
        chart_frame.setMinimumHeight(400)
        chart_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border: 1px solid {AppColors.BORDER}; border-radius: 10px;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        
        # Indicator Toggles (Quick)
        toggles_layout = QHBoxLayout()
        self.lbl_indicators = QLabel("Technical Indicators: ")
        self.lbl_indicators.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px;")
        toggles_layout.addWidget(self.lbl_indicators)
        
        # We can add actual checkboxes here later if needed
        chart_layout.addLayout(toggles_layout)

        self.price_chart = AdvancedChartWidget(title="Performance History")
        chart_layout.addWidget(self.price_chart)
        layout.addWidget(chart_frame)

        # 3. Bottom Section: Fundamental Metrics
        self.metrics_container = QFrame()
        self.metrics_layout = QGridLayout(self.metrics_container)
        self.metrics_layout.setSpacing(15)
        layout.addWidget(self.metrics_container)

        # 4. News Section
        news_label = QLabel("Recent News & Sentiment")
        news_label.setStyleSheet(f"color: {AppColors.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; margin-top: 10px;")
        layout.addWidget(news_label)

        self.news_list = QListWidget()
        self.news_list.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border: 1px solid {AppColors.BORDER}; border-radius: 8px;")
        self.news_list.setMaximumHeight(300)
        layout.addWidget(self.news_list)

    def set_ticker(self, ticker: str):
        """Trigger analysis for a new ticker."""
        self.lbl_ticker.setText(ticker)
        self.lbl_name.setText("Fetching Data...")
        self.lbl_price.setText("...")
        self.news_list.clear()
        self.current_indicators = {}
        
        # Clear old metrics
        for i in reversed(range(self.metrics_layout.count())): 
            self.metrics_layout.itemAt(i).widget().setParent(None)

        # Async fetch
        asyncio.create_task(self.service.fetch_analysis_data(ticker))

    @pyqtSlot(list, list)
    def on_chart_data(self, ohlc, dates):
        self.price_chart.set_data(ohlc)
        if ohlc:
            last_close = ohlc[-1][2]
            self.lbl_price.setText(f"${last_close:.2f}")

    @pyqtSlot(dict)
    def on_indicators(self, indicators):
        self.current_indicators = indicators
        # Auto-plot SMA50 and SMA200 for professional look
        if "SMA50" in indicators:
            self.price_chart.add_indicator("SMA50", indicators["SMA50"], color="#ff9800") # Amber
        if "SMA200" in indicators:
            self.price_chart.add_indicator("SMA200", indicators["SMA200"], color="#f44336") # Deep Red

    @pyqtSlot(dict)
    def on_fundamentals(self, data):
        # Update header info
        self.lbl_name.setText(f"{data.get('Sector', '')} | {data.get('Industry', '')}")

        # Populate Grid
        metrics = [
            ("Market Cap", data.get("Market Cap", "N/A")),
            ("P/E Ratio", data.get("P/E Ratio", "N/A")),
            ("Div Yield", data.get("Div Yield", "N/A")),
            ("EPS", data.get("EPS", "N/A")),
            ("52W High", data.get("52W High", "N/A")),
            ("52W Low", data.get("52W Low", "N/A")),
            ("Beta", data.get("Beta", "N/A"))
        ]

        for i, (label, value) in enumerate(metrics):
            row = i // 4
            col = i % 4
            
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border: 1px solid {AppColors.BORDER}; border-radius: 8px;")
            m_vbox = QVBoxLayout(metric_frame)
            m_vbox.setContentsMargins(10, 10, 10, 10)
            
            lbl_key = QLabel(label)
            lbl_key.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; text-transform: uppercase;")
            
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet(f"color: {AppColors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; margin-top: 5px;")
            
            m_vbox.addWidget(lbl_key)
            m_vbox.addWidget(lbl_val)
            
            self.metrics_layout.addWidget(metric_frame, row, col)

    @pyqtSlot(list)
    def on_news(self, news_items):
        self.news_list.clear()
        for item in news_items:
            title = item.get('title', 'No Title')
            source = item.get('publisher', 'Unknown')
            sentiment = item.get('sentiment', 'Neutral')
            
            # Color coding for sentiment
            color = "#888888" # Neutral
            if sentiment == "Bullish": color = AppColors.ACCENT_GREEN
            elif sentiment == "Bearish": color = AppColors.ACCENT_RED
            
            display_text = f"[{sentiment}] {title} ({source})"
            list_item = QListWidgetItem(display_text)
            from PyQt6.QtGui import QColor
            list_item.setForeground(QColor(color))
            self.news_list.addItem(list_item)
