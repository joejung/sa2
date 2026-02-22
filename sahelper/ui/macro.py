from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from .charts import MiniSparkline
from .styles import AppColors, AppStyles

class MacroWidget(QWidget):
    """Institutional Market Macro Dashboard."""
    def __init__(self):
        super().__init__()
        self.charts = {}
        self.init_ui()

    def update_macro_data(self, data: list):
        """Update the UI with live market data."""
        # Check if we need to initialize the grid
        if self.indices_layout.count() == 0:
            for i, item in enumerate(data):
                row, col = i // 3, i % 3
                card = self._create_macro_card(item["name"], item["ticker"], item["value"], item["change"])
                self.indices_layout.addWidget(card, row, col)
                # Store reference for updates
                self.charts[item["ticker"]] = card

        # Efficiently update existing cards
        for item in data:
            ticker = item["ticker"]
            if ticker in self.charts:
                card = self.charts[ticker]
                card.update_values(item["value"], item["change"], item["history"])

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Title & Market Status
        header = QHBoxLayout()
        title_lbl = QLabel("Market Macro Overview")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 700; color: #fff;")
        header.addWidget(title_lbl)
        
        status_lbl = QLabel("⚫ LIVE FEED")
        status_lbl.setStyleSheet(f"color: {AppColors.ACCENT_GREEN}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        header.addStretch()
        header.addWidget(status_lbl)
        layout.addLayout(header)

        # 2. Key Indices Layout
        self.indices_layout = QGridLayout()
        self.indices_layout.setSpacing(15)
        layout.addLayout(self.indices_layout)
        
        # 3. Bottom Sections: News and Calendar
        bottom_h = QHBoxLayout()
        bottom_h.setSpacing(20)

        # Global News Feed
        from .news_feed import GlobalNewsWidget
        self.news_feed = GlobalNewsWidget()
        bottom_h.addWidget(self.news_feed, 1)

        # Economic Calendar
        from .calendar import MacroCalendarWidget
        self.calendar = MacroCalendarWidget()
        bottom_h.addWidget(self.calendar, 1)

        layout.addLayout(bottom_h)

    def update_news(self, news):
        self.news_feed.update_news(news)

    def update_calendar(self, events):
        self.calendar.update_events(events)

    def _create_macro_card(self, name, ticker, value, change) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 8px;
            }}
        """)
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(15, 15, 15, 15)
        v_layout.setSpacing(5)

        # Header: Name + Ticker
        top_h = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-weight: 600; font-size: 13px;")
        top_h.addWidget(name_lbl)
        top_h.addStretch()
        ticker_lbl = QLabel(ticker)
        ticker_lbl.setStyleSheet(f"color: {AppColors.TEXT_MUTED}; font-size: 11px; background: #333; padding: 2px 4px; border-radius: 4px;")
        top_h.addWidget(ticker_lbl)
        v_layout.addLayout(top_h)

        # Value + Change + Sparkline
        middle_h = QHBoxLayout()
        val_container = QVBoxLayout()
        
        frame.val_lbl = QLabel(value)
        frame.val_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: white;")
        val_container.addWidget(frame.val_lbl)

        change_color = AppColors.ACCENT_GREEN if "+" in change else AppColors.ACCENT_RED
        frame.change_lbl = QLabel(change)
        frame.change_lbl.setStyleSheet(f"color: {change_color}; font-weight: 600; font-size: 14px;")
        val_container.addWidget(frame.change_lbl)
        
        middle_h.addLayout(val_container)
        middle_h.addStretch()
        
        # Add Mini Sparkline
        frame.sparkline = MiniSparkline()
        # Ensure sparkline matches card background
        frame.sparkline.plot_widget.setBackground(AppColors.BG_CARD) 
        middle_h.addWidget(frame.sparkline)
        v_layout.addLayout(middle_h)

        def update_values(val, chg, hist):
            frame.val_lbl.setText(val)
            color = AppColors.ACCENT_GREEN if "+" in chg else AppColors.ACCENT_RED
            frame.change_lbl.setText(chg)
            frame.change_lbl.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 14px;")
            frame.sparkline.update_chart(hist)

        frame.update_values = update_values
        return frame
