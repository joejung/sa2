from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtCore import Qt

class SAHelperWindow(QMainWindow):
    """The main application shell."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAHelper - Enterprise Edition")
        self.setMinimumSize(1000, 700)

        self.init_ui()

    def init_ui(self):
        # 1. Main Layout: Sidebar + Content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 2. Sidebar (Navigation)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                border-right: 1px solid #444;
                font-size: 14px;
                padding-top: 20px;
                background-color: #2b2b2b;
            }
            QListWidget::item {
                padding: 10px;
                color: #ccc;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
        """)
        self.sidebar.addItems(["Dashboard", "My Portfolios", "Analysis", "Automation", "Settings"])
        self.sidebar.currentRowChanged.connect(self.on_nav_changed)

        main_layout.addWidget(self.sidebar)

        # 3. Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # 4. Load Views
        self.setup_views()

    def setup_views(self):
        # Dashboard View (Macro Overview)
        from .macro import MacroWidget
        self.view_dashboard = MacroWidget()
        self.content_stack.addWidget(self.view_dashboard)

        # Portfolio View
        from .portfolio import PortfolioWidget
        self.view_portfolios = PortfolioWidget()
        self.content_stack.addWidget(self.view_portfolios)

        # Analysis View
        from .analysis import StockDetailWidget
        self.view_analysis = StockDetailWidget()
        self.content_stack.addWidget(self.view_analysis)

        self.view_automation = QWidget()
        self.content_stack.addWidget(self.view_automation)

        self.view_settings = QWidget()
        self.content_stack.addWidget(self.view_settings)
        
        # Set default view
        self.content_stack.setCurrentIndex(0)

    def on_nav_changed(self, index: int):
        """Switch the main content view based on sidebar selection."""
        self.content_stack.setCurrentIndex(index)
