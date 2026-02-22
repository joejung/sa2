from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from .styles import AppColors, AppStyles

class MacroCalendarWidget(QWidget):
    """Institutional economic calendar display."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header
        header = QLabel("ECONOMIC EVENT CALENDAR")
        header.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        layout.addWidget(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Time", "Event", "Impact", "Forecast/Prev"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(AppStyles.TABLE)
        
        layout.addWidget(self.table)

    @pyqtSlot(list)
    def update_events(self, events):
        self.table.setRowCount(len(events))
        for i, ev in enumerate(events):
            # Date
            item_date = QTableWidgetItem(ev['date'])
            item_date.setForeground(QColor(AppColors.TEXT_SECONDARY))
            self.table.setItem(i, 0, item_date)
            
            # Time
            self.table.setItem(i, 1, QTableWidgetItem(ev['time']))
            
            # Event
            item_event = QTableWidgetItem(ev['event'])
            from PyQt6.QtGui import QFont
            font = QFont()
            font.setBold(True)
            item_event.setFont(font)
            self.table.setItem(i, 2, item_event)
            
            # Impact
            impact = ev['impact']
            impact_item = QTableWidgetItem(impact)
            
            # Color coding for impact
            color = AppColors.TEXT_SECONDARY
            if impact == "CRITICAL": color = "#ff1744" # Bright Red
            elif impact == "HIGH": color = AppColors.ACCENT_RED
            elif impact == "MEDIUM": color = AppColors.ACCENT_YELLOW
            
            impact_item.setForeground(QColor(color))
            self.table.setItem(i, 3, impact_item)
            
            # Forecast / Prev
            fp = f"{ev['forecast']} / {ev['previous']}"
            self.table.setItem(i, 4, QTableWidgetItem(fp))
