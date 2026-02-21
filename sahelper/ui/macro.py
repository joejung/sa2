from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt

class MacroWidget(QWidget):
    """Institutional Market Macro Dashboard."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def update_macro_data(self, data: list):
        """Update the UI with live market data."""
        # Clear the old indices layout or update existing cards
        # For simplicity in this iteration, we recreate the cards
        for i in reversed(range(self.indices_layout.count())): 
            self.indices_layout.itemAt(i).widget().setParent(None)

        for i, item in enumerate(data):
            row, col = i // 3, i % 3
            card = self._create_macro_card(item["name"], item["ticker"], item["value"], item["change"])
            self.indices_layout.addWidget(card, row, col)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Title & Market Status
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Market Macro Overview</h2>"))
        status_lbl = QLabel("<span style='color: #888;'>Live Feed: </span><span style='color: green;'>CONNECTED</span>")
        header.addStretch()
        header.addWidget(status_lbl)
        layout.addLayout(header)

        # 2. Key Indices Layout
        self.indices_layout = QGridLayout()
        layout.addLayout(self.indices_layout)
        
        # Initial call to populate with dummy
        initial_data = [
            {"name": "S&P 500", "ticker": "SPY", "value": "5,005.57", "change": "+0.45%"},
            # ...
        ]
        # (Rest of UI init stays the same)

        # 3. Macro Sector Heatmap (Placeholder)
        layout.addWidget(QLabel("<b>Sector Performance (Attribution)</b>"))
        heatmap_frame = QFrame()
        heatmap_frame.setMinimumHeight(200)
        heatmap_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")
        h_layout = QHBoxLayout(heatmap_frame)
        h_layout.addWidget(QLabel("Interactive Sector Map Placeholder"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heatmap_frame)

        layout.addStretch()

    def _create_macro_card(self, name, ticker, value, change) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        v_layout = QVBoxLayout(frame)
        v_layout.setSpacing(2)

        top_h = QHBoxLayout()
        top_h.addWidget(QLabel(f"<b>{name}</b>"))
        top_h.addStretch()
        top_h.addWidget(QLabel(f"<small>{ticker}</small>"))
        v_layout.addLayout(top_h)

        val_lbl = QLabel(f"<h3>{value}</h3>")
        v_layout.addWidget(val_lbl)

        change_color = "green" if "+" in change else "red"
        change_lbl = QLabel(f"<span style='color: {change_color};'>{change}</span>")
        v_layout.addWidget(change_lbl)

        return frame
