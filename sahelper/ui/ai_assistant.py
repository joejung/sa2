import asyncio
import logging
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextBrowser, 
    QPushButton, QSplitter, QFrame, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QObject
from .styles import AppColors, AppStyles

logger = logging.getLogger(__name__)

class AIService(QObject):
    """Simulated AI service that processes natural language commands."""
    response_ready = pyqtSignal(str, str) # (request_id, response_markdown)

    def __init__(self):
        super().__init__()

    async def process_query(self, query, request_id):
        """Mock AI logic: Analyze query and provide a professional financial response."""
        logger.info(f"AI processing query [{request_id}]: {query}")
        await asyncio.sleep(1.5) # Simulate LLM latency
        
        query_lower = query.lower()
        
        if "portfolio" in query_lower or "risk" in query_lower:
            response = (
                "### Portfolio Risk Assessment\n"
                "Your portfolio has a **Beta of 1.15**, suggesting it's slightly more volatile than the market. "
                "The **Sharpe Ratio (0.20)** indicates a moderate risk-adjusted return. "
                "Consider hedging with VIX calls if you expect further volatility."
            )
        elif "spy" in query_lower or "market" in query_lower:
            response = (
                "### Market Outlook (SPY)\n"
                "The S&P 500 is currently testing a key resistance level. "
                "Technical indicators (SMA 50/200) show a bullish cross on the daily chart. "
                "**Sentiment Score: 0.65 (Bullish)** based on recent headlines."
            )
        elif "screener" in query_lower or "undervalued" in query_lower:
            response = (
                "### Screener Recommendation\n"
                "I recommend running a screen for **Tech stocks with P/E < 20 and Dividend Yield > 1%**. "
                "Candidates like **INTC** and **VZ** fit these criteria currently."
            )
        else:
            response = (
                "### Financial Assistant\n"
                "I'm monitoring the markets. You can ask me to:\n"
                "- *'Analyze my portfolio risk'*\n"
                "- *'What's the outlook for SPY?'*\n"
                "- *'Find undervalued tech stocks'*\n"
                "\nI can also execute commands like `/chart {ticker}` or `/screen {filter}`."
            )
            
        self.response_ready.emit(request_id, response)

class AIChatPanel(QFrame):
    """A single chat panel for LLM interaction."""
    def __init__(self, service, panel_id):
        super().__init__()
        self.service = service
        self.panel_id = panel_id
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QHBoxLayout()
        lbl_id = QLabel(f"AI AGENT Split #{self.panel_id}")
        lbl_id.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {AppColors.TEXT_SECONDARY}; text-transform: uppercase;")
        header.addWidget(lbl_id)
        header.addStretch()
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(20, 20)
        btn_close.setStyleSheet("background: transparent; border: none; font-size: 16px; color: #888;")
        btn_close.clicked.connect(self.close_panel)
        header.addWidget(btn_close)
        layout.addLayout(header)

        # Chat History
        self.history = QTextBrowser()
        self.history.setOpenExternalLinks(True)
        self.history.setStyleSheet(f"background-color: {AppColors.BG_MAIN}; border: none; color: {AppColors.TEXT_PRIMARY};")
        layout.addWidget(self.history)

        # Input Area
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command or question (e.g. '/analyze SPY')...")
        self.input.setStyleSheet(AppStyles.INPUT)
        self.input.returnPressed.connect(self.send_query)
        layout.addWidget(self.input)

    def close_panel(self):
        self.setParent(None)
        self.deleteLater()

    def send_query(self):
        query = self.input.text().strip()
        if not query: return
        
        self.history.append(f"<p style='color: {AppColors.PRIMARY};'><b>User:</b> {query}</p>")
        self.input.clear()
        self.input.setEnabled(False)
        
        # Unique ID for this specific panel's query
        request_id = f"{self.panel_id}_{random.randint(1000, 9999)}"
        # Use a lambda to check if the response belongs to this panel
        self.service.response_ready.connect(lambda rid, resp: self.on_response(rid, resp, request_id))
        
        asyncio.create_task(self.service.process_query(query, request_id))

    def on_response(self, rid, response, target_id):
        if rid == target_id:
            self.history.append(f"<div style='color: white; margin-top: 10px;'>{response}</div>")
            self.history.append("<hr style='border: 0; border-top: 1px solid #333;'>")
            self.input.setEnabled(True)
            self.input.setFocus()
            # Scroll to bottom
            self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

class AICommandWorkspace(QWidget):
    """Workspace that manages multiple split AI chat panels."""
    def __init__(self):
        super().__init__()
        self.service = AIService()
        self.panel_counter = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top Bar
        top_bar = QHBoxLayout()
        lbl_title = QLabel("AI Analysis Terminal")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {AppColors.TEXT_PRIMARY};")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch()

        self.btn_add_split = QPushButton("+ NEW SPLIT")
        self.btn_add_split.clicked.connect(self.add_split)
        self.btn_add_split.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #005a9e;
            }}
        """)
        top_bar.addWidget(self.btn_add_split)
        layout.addLayout(top_bar)

        # Splitter Area
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {AppColors.BORDER}; }}")
        
        layout.addWidget(self.splitter)
        
        # Add initial split
        self.add_split()

    def add_split(self):
        self.panel_counter += 1
        panel = AIChatPanel(self.service, self.panel_counter)
        self.splitter.addWidget(panel)
        # Focus input of new panel
        panel.input.setFocus()
