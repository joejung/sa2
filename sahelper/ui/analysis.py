from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt

from .charts import StockChartWidget
from .styles import AppColors, AppStyles

class StockDetailWidget(QWidget):
    """Detailed view for a single stock ticker with metrics and charts."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Ticker Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border-radius: 10px; border: 1px solid {AppColors.BORDER};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_ticker = QLabel("AAPL")
        self.lbl_ticker.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {AppColors.TEXT_PRIMARY};")
        
        self.lbl_name = QLabel("Apple Inc.")
        self.lbl_name.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 18px; margin-left: 10px; font-weight: 400;")
        
        header_layout.addWidget(self.lbl_ticker)
        header_layout.addWidget(self.lbl_name)
        header_layout.addStretch()
        
        self.lbl_price = QLabel("$185.20")
        self.lbl_price.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        
        self.lbl_change = QLabel("+1.20%")
        self.lbl_change.setStyleSheet(f"color: {AppColors.ACCENT_GREEN}; font-size: 18px; font-weight: 600; margin-left: 10px;")
        
        header_layout.addWidget(self.lbl_price)
        header_layout.addWidget(self.lbl_change)
        
        layout.addWidget(header_frame)

        # 2. Middle Section: Price Chart
        chart_frame = QFrame()
        chart_frame.setMinimumHeight(400)
        chart_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border: 1px solid {AppColors.BORDER}; border-radius: 10px;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        
        self.price_chart = StockChartWidget(title="Performance History", background=AppColors.BG_CARD)
        chart_layout.addWidget(self.price_chart)
        layout.addWidget(chart_frame)

        # 3. Bottom Section: Fundamental Metrics
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(15)
        
        metrics = [
            ("Market Cap", "2.85T"), ("P/E Ratio", "30.5"),
            ("Div Yield", "0.52%"), ("EPS", "6.13"),
            ("52W High", "$199.62"), ("52W Low", "$143.90")
        ]

        for i, (label, value) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {AppColors.BG_CARD};
                    border: 1px solid {AppColors.BORDER};
                    border-radius: 8px;
                }}
            """)
            m_vbox = QVBoxLayout(metric_frame)
            m_vbox.setContentsMargins(15, 15, 15, 15)
            
            lbl_key = QLabel(label)
            lbl_key.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; text-transform: uppercase;")
            
            lbl_val = QLabel(value)
            lbl_val.setStyleSheet(f"color: {AppColors.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; margin-top: 5px;")
            
            m_vbox.addWidget(lbl_key)
            m_vbox.addWidget(lbl_val)
            
            metrics_layout.addWidget(metric_frame, row, col)

        layout.addLayout(metrics_layout)
        layout.addStretch()

    def set_ticker(self, ticker: str):
        self.lbl_ticker.setText(ticker)
        # In a real app, trigger data fetch here
        self.price_chart.update_chart([]) # Reset chart for new ticker

    def update_data(self, price: str, change: str, history: list):
        """Update the widget with live data."""
        self.lbl_price.setText(price)
        color = AppColors.ACCENT_GREEN if "+" in change else AppColors.ACCENT_RED
        self.lbl_change.setText(change)
        self.lbl_change.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 600; margin-left: 10px;")
        self.price_chart.update_chart(history)
