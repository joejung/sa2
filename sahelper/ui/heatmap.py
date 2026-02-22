from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from .styles import AppColors

class HeatmapNode:
    def __init__(self, ticker, weight, change_pct, sector):
        self.ticker = ticker
        self.weight = weight
        self.change_pct = change_pct
        self.sector = sector
        self.rect = QRectF()

class PortfolioHeatmapWidget(QWidget):
    """Custom treemap visualization for portfolio holdings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._nodes = []
        self.setMinimumHeight(400)
        self.setMouseTracking(True)

    def set_data(self, holdings):
        """
        holdings: list of dicts {ticker, market_value, change_pct, sector}
        """
        total_value = sum(h['market_value'] for h in holdings)
        if total_value == 0:
            self._nodes = []
            self.update()
            return

        self._nodes = []
        for h in holdings:
            weight = h['market_value'] / total_value
            self._nodes.append(HeatmapNode(
                h['ticker'], 
                weight, 
                h['change_pct'],
                h.get('sector', 'N/A')
            ))
        
        # Sort by weight descending for better treemap layout
        self._nodes.sort(key=lambda x: x.weight, reverse=True)
        self.layout_nodes()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout_nodes()

    def layout_nodes(self):
        if not self._nodes:
            return
        
        # Simple recursive subdivision (Alternative to Squarified Treemap)
        self._subdivide(self._nodes, QRectF(0, 0, self.width(), self.height()))

    def _subdivide(self, nodes, rect):
        if not nodes:
            return
        if len(nodes) == 1:
            nodes[0].rect = rect
            return

        # Split nodes into two groups with roughly equal weight
        total_weight = sum(n.weight for n in nodes)
        half_weight = total_weight / 2
        
        current_weight = 0
        split_idx = 1
        for i, n in enumerate(nodes):
            current_weight += n.weight
            if current_weight >= half_weight:
                split_idx = i + 1
                break
        
        left_nodes = nodes[:split_idx]
        right_nodes = nodes[split_idx:]
        
        left_weight = sum(n.weight for n in left_nodes)
        
        # Determine split direction based on aspect ratio
        if rect.width() > rect.height():
            # Split vertically
            left_width = rect.width() * (left_weight / total_weight)
            left_rect = QRectF(rect.x(), rect.y(), left_width, rect.height())
            right_rect = QRectF(rect.x() + left_width, rect.y(), rect.width() - left_width, rect.height())
        else:
            # Split horizontally
            left_height = rect.height() * (left_weight / total_weight)
            left_rect = QRectF(rect.x(), rect.y(), rect.width(), left_height)
            right_rect = QRectF(rect.x(), rect.y() + left_height, rect.width(), rect.height() - left_height)
            
        self._subdivide(left_nodes, left_rect)
        self._subdivide(right_nodes, right_rect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for node in self._nodes:
            rect = node.rect
            # Padding
            rect = rect.adjusted(1, 1, -1, -1)
            
            # Determine color based on performance
            # Intensity based on change_pct (max at 5%)
            intensity = min(abs(node.change_pct) / 0.05, 1.0)
            
            if node.change_pct >= 0:
                # Green gradient
                base_color = QColor("#1b5e20") # Dark Green
                target_color = QColor(AppColors.ACCENT_GREEN)
            else:
                # Red gradient
                base_color = QColor("#b71c1c") # Dark Red
                target_color = QColor(AppColors.ACCENT_RED)
                
            color = self._interpolate_color(base_color, target_color, intensity)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(AppColors.BORDER), 1))
            painter.drawRect(rect)
            
            # Draw Text if enough space
            if rect.width() > 40 and rect.height() > 30:
                painter.setPen(QPen(Qt.GlobalColor.white))
                
                # Ticker
                font_ticker = QFont("Segoe UI", 10, QFont.Weight.Bold)
                painter.setFont(font_ticker)
                painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, node.ticker)
                
                # Percent
                font_pct = QFont("Segoe UI", 8)
                painter.setFont(font_pct)
                painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, f"{node.change_pct*100:+.2f}%")

    def _interpolate_color(self, c1, c2, factor):
        r = c1.red() + (c2.red() - c1.red()) * factor
        g = c1.green() + (c2.green() - c1.green()) * factor
        b = c1.blue() + (c2.blue() - c1.blue()) * factor
        return QColor(int(r), int(g), int(b))
