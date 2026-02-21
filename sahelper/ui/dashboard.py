from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt
from .charts import StockChartWidget
from .styles import AppColors, AppStyles

class DashboardWidget(QWidget):
    """Main overview panel for the application."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Summary Cards (Total Value, Daily Change, Gain/Loss)
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Example: Card 1 (Total Value)
        self.card_total = self._create_card("TOTAL PORTFOLIO VALUE", "$124,500.00", "+2.5%")
        cards_layout.addWidget(self.card_total, 0, 0)

        # Example: Card 2 (Daily Gain)
        self.card_gain = self._create_card("TODAY'S GAIN", "$3,112.50", "+2.5%")
        cards_layout.addWidget(self.card_gain, 0, 1)

        layout.addLayout(cards_layout)

        # 2. Portfolio Performance Chart
        chart_frame = QFrame()
        chart_frame.setMinimumHeight(400)
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 10px;
            }}
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        
        title_lbl = QLabel("PORTFOLIO PERFORMANCE (LTM)")
        title_lbl.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-weight: 600; font-size: 14px; margin-bottom: 10px;")
        chart_layout.addWidget(title_lbl)
        
        self.perf_chart = StockChartWidget(background=AppColors.BG_CARD)
        chart_layout.addWidget(self.perf_chart)
        layout.addWidget(chart_frame)

        # 3. Recent Activity / Alerts
        layout.addWidget(QLabel("RECENT MARKET ALERTS"))
        self.alerts_frame = QFrame()
        self.alerts_frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.alerts_frame)

        # Spacer to push content up
        layout.addStretch()

    def update_performance(self, history: list):
        """Update the performance chart."""
        self.perf_chart.update_chart(history)

    def _create_card(self, title: str, value: str, change: str) -> QFrame:
        """Helper to create a styled summary card."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 10px;
            }}
        """)
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-weight: 600; color: {AppColors.TEXT_SECONDARY}; font-size: 12px; letter-spacing: 0.5px;")
        v_layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {AppColors.TEXT_PRIMARY}; margin-top: 5px;")
        v_layout.addWidget(lbl_value)

        color = AppColors.ACCENT_GREEN if "+" in change else AppColors.ACCENT_RED
        lbl_change = QLabel(change)
        lbl_change.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 16px; margin-top: 2px;")
        v_layout.addWidget(lbl_change)

        return frame

    def update_data(self, portfolio_total: float, daily_change: float):
        """Update the displayed values."""
        # Implementation for updating labels
        pass
