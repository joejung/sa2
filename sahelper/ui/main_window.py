from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtCore import Qt
from .styles import AppStyles

class SAHelperWindow(QMainWindow):
    """The main application shell."""
    def __init__(self, alert_service=None, attribution_service=None):
        super().__init__()
        self.alert_service = alert_service
        self.attribution_service = attribution_service
        self.setWindowTitle("SAHelper - Enterprise Edition")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(AppStyles.MAIN_WINDOW) # Apply global styles

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
        self.sidebar.setFixedWidth(240) # Slightly wider for better text flow
        self.sidebar.setStyleSheet(AppStyles.SIDEBAR)
        
        # Add items with icons
        items = [
            "📊 Overview", 
            "🌍 Market", 
            "💼 Portfolios", 
            "🏆 Performance",
            "📈 Analysis", 
            "🔍 Screener",
            "🤖 Assistant",
            "🔔 Alerts",
            "🤖 Automation", 
            "⚙️ Settings"
        ]
        self.sidebar.addItems(items)
        main_layout.addWidget(self.sidebar)

        # 3. Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # 4. Load Views
        self.setup_views()
        
        # 5. Connect Navigation & Set Default (After Stack is Ready)
        self.sidebar.currentRowChanged.connect(self.on_nav_changed)
        self.sidebar.setCurrentRow(0) 

    def setup_views(self):
        # 0. Overview (Dashboard)
        from .dashboard import DashboardWidget
        self.view_overview = DashboardWidget()
        self.content_stack.addWidget(self.view_overview)

        # 1. Market (Macro Overview)
        from .macro import MacroWidget
        self.view_market = MacroWidget()
        self.content_stack.addWidget(self.view_market)

        # 2. Portfolio View
        from .portfolio import PortfolioWidget
        self.view_portfolios = PortfolioWidget()
        self.content_stack.addWidget(self.view_portfolios)

        # 3. Performance View
        from .performance import AttributionWidget
        self.view_performance = AttributionWidget(self.attribution_service)
        self.content_stack.addWidget(self.view_performance)
        self.view_performance.service.attribution_ready.connect(self.view_performance.update_attribution)

        # 4. Analysis View
        from .analysis import StockDetailWidget
        self.view_analysis = StockDetailWidget()
        self.content_stack.addWidget(self.view_analysis)

        # 5. Screener View
        from .screener import ScreenerWidget
        self.view_screener = ScreenerWidget()
        self.content_stack.addWidget(self.view_screener)

        # 6. AI Assistant View
        from .ai_assistant import AICommandWorkspace
        self.view_assistant = AICommandWorkspace()
        self.content_stack.addWidget(self.view_assistant)
        
        # Connect AI Commands to UI Actions
        self.view_assistant.service.command_detected.connect(self.on_ai_command)

        # 7. Alerts View
        from .alerts import AlertsWidget
        self.view_alerts = AlertsWidget(self.alert_service)
        self.content_stack.addWidget(self.view_alerts)

        # 8. Automation
        self.view_automation = QWidget()
        self.content_stack.addWidget(self.view_automation)

        # 9. Settings
        self.view_settings = QWidget()
        self.content_stack.addWidget(self.view_settings)
        
        # Set default view
        self.content_stack.setCurrentIndex(0)

    def on_nav_changed(self, index: int):
        """Switch the main content view based on sidebar selection."""
        self.content_stack.setCurrentIndex(index)

    def on_ai_command(self, command, arg):
        """Handle agentic commands from the AI Assistant."""
        if command == "chart":
            # Switch to Analysis tab (now index 4)
            self.sidebar.setCurrentRow(4)
            self.view_analysis.set_ticker(arg)
        elif command == "risk":
            # Switch to Portfolio tab (index 2)
            self.sidebar.setCurrentRow(2)
            # Trigger risk analysis if possible
            if hasattr(self.view_portfolios, 'on_risk_clicked'):
                self.view_portfolios.on_risk_clicked()
        elif command == "screen":
            # Switch to Screener (index 5)
            self.sidebar.setCurrentRow(5)
            # We could automate filter setting here too
