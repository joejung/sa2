from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt

class DashboardWidget(QWidget):
    """Main overview panel for the application."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Summary Cards (Total Value, Daily Change, Gain/Loss)
        cards_layout = QGridLayout()
        
        # Example: Card 1 (Total Value)
        self.card_total = self._create_card("Total Portfolio Value", "$0.00", "0.00%")
        cards_layout.addWidget(self.card_total, 0, 0)

        # Example: Card 2 (Daily Gain)
        self.card_gain = self._create_card("Today's Gain", "$0.00", "+0.00%")
        cards_layout.addWidget(self.card_gain, 0, 1)

        layout.addLayout(cards_layout)

        # 2. Recent Activity / Alerts
        layout.addWidget(QLabel("<b>Recent Market Alerts</b>"))
        self.alerts_frame = QFrame()
        self.alerts_frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self.alerts_frame)

        # Spacer to push content up
        layout.addStretch()

    def _create_card(self, title: str, value: str, change: str) -> QFrame:
        """Helper to create a styled summary card."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLineWidth(1)
        
        v_layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-weight: bold; color: #888;")
        v_layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        v_layout.addWidget(lbl_value)

        lbl_change = QLabel(change)
        # Conditional styling based on '+' or '-' could go here
        lbl_change.setStyleSheet("color: green;" if "+" in change else "color: red;")
        v_layout.addWidget(lbl_change)

        return frame

    def update_data(self, portfolio_total: float, daily_change: float):
        """Update the displayed values."""
        # Implementation for updating labels
        pass
