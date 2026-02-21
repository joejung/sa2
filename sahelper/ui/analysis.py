from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt

class StockDetailWidget(QWidget):
    """Detailed view for a single stock ticker with metrics and charts."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Ticker Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        
        self.lbl_ticker = QLabel("<h2>AAPL</h2>")
        self.lbl_name = QLabel("Apple Inc.")
        self.lbl_name.setStyleSheet("color: #888; margin-left: 10px;")
        
        header_layout.addWidget(self.lbl_ticker)
        header_layout.addWidget(self.lbl_name)
        header_layout.addStretch()
        
        self.lbl_price = QLabel("<h3>$185.20</h3>")
        self.lbl_change = QLabel("<span style='color: green;'>+1.20%</span>")
        header_layout.addWidget(self.lbl_price)
        header_layout.addWidget(self.lbl_change)
        
        layout.addWidget(header_frame)

        # 2. Middle Section: Chart Placeholder
        chart_frame = QFrame()
        chart_frame.setMinimumHeight(300)
        chart_frame.setStyleSheet("background-color: #252525; border: 1px dashed #444;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(QLabel("Price Chart Placeholder (Integrating pyqtgraph...)"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(chart_frame)

        # 3. Bottom Section: Fundamental Metrics
        metrics_layout = QGridLayout()
        
        metrics = [
            ("Market Cap", "2.85T"), ("P/E Ratio", "30.5"),
            ("Div Yield", "0.52%"), ("EPS", "6.13"),
            ("52W High", "$199.62"), ("52W Low", "$143.90")
        ]

        for i, (label, value) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            metric_frame = QFrame()
            metric_frame.setStyleSheet("background-color: #2b2b2b; padding: 10px;")
            m_vbox = QVBoxLayout(metric_frame)
            m_vbox.addWidget(QLabel(f"<small>{label}</small>"))
            m_vbox.addWidget(QLabel(f"<b>{value}</b>"))
            
            metrics_layout.addWidget(metric_frame, row, col)

        layout.addLayout(metrics_layout)
        layout.addStretch()

    def set_ticker(self, ticker: str):
        self.lbl_ticker.setText(f"<h2>{ticker}</h2>")
        # In a real app, trigger data fetch here
