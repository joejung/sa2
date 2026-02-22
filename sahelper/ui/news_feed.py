from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from .styles import AppColors

class GlobalNewsWidget(QWidget):
    """Aggregated global market news feed with sentiment analysis."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header
        header = QLabel("GLOBAL NEWS AGGREGATOR")
        header.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        layout.addWidget(header)

        # News List
        self.news_list = QListWidget()
        self.news_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: 8px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {AppColors.BORDER};
            }}
            QListWidget::item:hover {{
                background-color: {AppColors.BG_INPUT};
            }}
        """)
        self.news_list.setWordWrap(True)
        layout.addWidget(self.news_list)

    @pyqtSlot(list)
    def update_news(self, news_items):
        self.news_list.clear()
        for item in news_items:
            # Create a custom widget for each news item for better layout
            widget = QWidget()
            w_layout = QVBoxLayout(widget)
            w_layout.setContentsMargins(5, 5, 5, 5)
            w_layout.setSpacing(4)

            # Title
            title_lbl = QLabel(item['title'])
            title_lbl.setWordWrap(True)
            title_lbl.setStyleSheet(f"color: {AppColors.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;")
            w_layout.addWidget(title_lbl)

            # Meta: Source + Sentiment
            meta_h = QHBoxLayout()
            source_lbl = QLabel(item['publisher'])
            source_lbl.setStyleSheet(f"color: {AppColors.TEXT_MUTED}; font-size: 11px;")
            meta_h.addWidget(source_lbl)
            
            meta_h.addStretch()

            sentiment = item['sentiment']
            sentiment_lbl = QLabel(sentiment.upper())
            color = "#888888"
            if sentiment == "Bullish": color = AppColors.ACCENT_GREEN
            elif sentiment == "Bearish": color = AppColors.ACCENT_RED
            
            sentiment_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 800; border: 1px solid {color}; border-radius: 3px; padding: 1px 4px;")
            meta_h.addWidget(sentiment_lbl)
            
            w_layout.addLayout(meta_h)

            # Add to list
            list_item = QListWidgetItem(self.news_list)
            list_item.setSizeHint(widget.sizeHint())
            self.news_list.addItem(list_item)
            self.news_list.setItemWidget(list_item, widget)
