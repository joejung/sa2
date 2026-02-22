from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from .styles import AppColors, AppStyles

class AlertsWidget(QWidget):
    """UI for managing price and technical alerts."""
    def __init__(self, alert_service):
        super().__init__()
        self.service = alert_service
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        lbl_title = QLabel("Price & Technical Alerts")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        layout.addWidget(lbl_title)

        # Add Alert Form
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {AppColors.BG_CARD}; border-radius: 8px; border: 1px solid {AppColors.BORDER};")
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)

        self.input_ticker = QLineEdit()
        self.input_ticker.setPlaceholderText("Ticker (e.g. AAPL)")
        self.input_ticker.setFixedWidth(120)
        self.input_ticker.setStyleSheet(AppStyles.INPUT)
        form_layout.addWidget(self.input_ticker)

        self.combo_cond = QComboBox()
        self.combo_cond.addItems([">", "<", "CROSS ABOVE", "CROSS BELOW"])
        self.combo_cond.setStyleSheet(AppStyles.INPUT)
        form_layout.addWidget(self.combo_cond)

        self.spin_value = QDoubleSpinBox()
        self.spin_value.setRange(0, 1000000)
        self.spin_value.setValue(100.0)
        self.spin_value.setStyleSheet(AppStyles.INPUT)
        form_layout.addWidget(self.spin_value)

        btn_add = QPushButton("ADD ALERT")
        btn_add.clicked.connect(self.on_add_clicked)
        btn_add.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        form_layout.addWidget(btn_add)

        form_layout.addStretch()
        layout.addWidget(form_frame)

        # Alerts Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ticker", "Condition", "Target Value", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(AppStyles.TABLE)
        layout.addWidget(self.table)

    def on_add_clicked(self):
        ticker = self.input_ticker.text().strip().upper()
        cond = self.combo_cond.currentText()
        val = self.spin_value.value()
        
        if ticker:
            self.service.add_alert(ticker, cond, val)
            self.refresh_table()
            self.input_ticker.clear()

    def refresh_table(self):
        self.table.setRowCount(len(self.service.alerts))
        for i, alert in enumerate(self.service.alerts):
            self.table.setItem(i, 0, QTableWidgetItem(alert['ticker']))
            self.table.setItem(i, 1, QTableWidgetItem(alert['condition']))
            self.table.setItem(i, 2, QTableWidgetItem(f"${alert['value']:,.2f}"))
            
            status = "TRIGGERED" if alert.get('triggered') else "ACTIVE"
            status_item = QTableWidgetItem(status)
            if status == "TRIGGERED":
                status_item.setForeground(QColor(AppColors.ACCENT_RED))
            else:
                status_item.setForeground(QColor(AppColors.ACCENT_GREEN))
            
            self.table.setItem(i, 3, status_item)
