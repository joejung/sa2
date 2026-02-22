from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from .styles import AppColors, AppStyles
import asyncio

class AttributionWidget(QWidget):
    """Performance attribution dashboard."""
    def __init__(self, attribution_service):
        super().__init__()
        self.service = attribution_service
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("Performance Attribution")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        header.addWidget(lbl_title)
        
        header.addStretch()
        
        self.btn_refresh = QPushButton("Recalculate")
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
        self.btn_refresh.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        header.addWidget(self.btn_refresh)
        
        layout.addLayout(header)

        # Top Summary Metrics
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        self.card_total = self._create_metric_card("Total Alpha Contribution", "$0.00")
        summary_layout.addWidget(self.card_total)
        
        # Space for more summary cards
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Attribution Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ticker", "Realized P&L", "Unrealized P&L", "Total Contribution"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(AppStyles.TABLE)
        
        layout.addWidget(self.table)

    def _create_metric_card(self, title, value) -> QFrame:
        frame = QFrame()
        frame.setFixedWidth(250)
        frame.setObjectName("metric_card")
        frame.setStyleSheet(f"""
            QFrame#metric_card {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 8px;
            }}
        """)
        vbox = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: white;")
        frame.val_lbl = val_lbl # Store for updates
        
        vbox.addWidget(lbl_title)
        vbox.addWidget(val_lbl)
        return frame

    def on_refresh_clicked(self):
        asyncio.create_task(self.service.calculate_attribution())

    @pyqtSlot(list)
    def update_attribution(self, data):
        self.table.setRowCount(len(data))
        total_contrib = 0
        
        for i, item in enumerate(data):
            # Ticker
            self.table.setItem(i, 0, QTableWidgetItem(item['ticker']))
            
            # Realized
            self.table.setItem(i, 1, self._create_pl_item(item['realized_pl']))
            
            # Unrealized
            self.table.setItem(i, 2, self._create_pl_item(item['unrealized_pl']))
            
            # Total
            contrib = item['total_contribution']
            self.table.setItem(i, 3, self._create_pl_item(contrib))
            total_contrib += contrib
            
        self.card_total.val_lbl.setText(f"${total_contrib:,.2f}")
        color = AppColors.ACCENT_GREEN if total_contrib >= 0 else AppColors.ACCENT_RED
        self.card_total.val_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {color};")

    def _create_pl_item(self, value) -> QTableWidgetItem:
        item = QTableWidgetItem(f"${value:,.2f}")
        color = AppColors.ACCENT_GREEN if value >= 0 else AppColors.ACCENT_RED
        item.setForeground(QColor(color))
        return item
