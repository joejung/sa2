import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QRectF
import numpy as np
from .styles import AppColors

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        super().__init__()
        self.data = data  # List of (time, open, close, low, high)
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = from_qpicture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen(AppColors.BORDER))
        
        w = 0.4  # Width of the candle
        
        for (t, open, close, low, high) in self.data:
            if close > open:
                p.setBrush(pg.mkBrush(AppColors.ACCENT_GREEN))
                p.setPen(pg.mkPen(AppColors.ACCENT_GREEN))
            else:
                p.setBrush(pg.mkBrush(AppColors.ACCENT_RED))
                p.setPen(pg.mkPen(AppColors.ACCENT_RED))
                
            # Draw the vertical line (High to Low)
            p.drawLine(pg.QtCore.QPointF(t, low), pg.QtCore.QPointF(t, high))
            
            # Draw the body (Open to Close)
            p.drawRect(pg.QtCore.QRectF(t - w, open, w * 2, close - open))
            
        p.end()

    def paint(self, p, *args):
        if self.picture:
            self.picture.play(p)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.picture.boundingRect())

class AdvancedChartWidget(QWidget):
    """Professional interactive chart with Candlesticks, Volume, and Indicators."""
    def __init__(self, title=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.setBackground(AppColors.BG_CARD)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
        
        # Axis styling
        self.plot_widget.getAxis('left').setPen(AppColors.TEXT_MUTED)
        self.plot_widget.getAxis('bottom').setPen(AppColors.TEXT_MUTED)
        
        self.candle_item = None
        self.indicators = {} # { name: { 'data': [], 'item': PlotDataItem, 'color': str } }
        
        layout.addWidget(self.plot_widget)
        
    def set_data(self, ohlc_data):
        """
        ohlc_data: List of tuples (index, open, close, low, high)
        """
        # We don't want to clear EVERYTHING because we might want to keep indicators
        # But for now, simple clear is safer
        self.plot_widget.clear()
        self.indicators = {}
        
        if not ohlc_data:
            return

        self.candle_item = CandlestickItem(ohlc_data)
        self.plot_widget.addItem(self.candle_item)

    def add_indicator(self, name, data, color=AppColors.PRIMARY):
        """Add or update a line indicator (e.g. SMA)."""
        if name in self.indicators:
            self.plot_widget.removeItem(self.indicators[name]['item'])
        
        x = range(len(data))
        item = self.plot_widget.plot(x, data, pen=pg.mkPen(color=color, width=1.5), name=name)
        self.indicators[name] = {'data': data, 'item': item, 'color': color}

    def remove_indicator(self, name):
        if name in self.indicators:
            self.plot_widget.removeItem(self.indicators[name]['item'])
            del self.indicators[name]

class StockChartWidget(QWidget):
    """Reusable stock chart component using pyqtgraph."""
    def __init__(self, title=None, show_axes=True, interactive=True, background=AppColors.BG_CARD):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Plot setup
        self.plot_widget = pg.PlotWidget(title=title)
        if background:
            self.plot_widget.setBackground(background)
        else:
            self.plot_widget.setBackground(None)
        
        # Professional styling
        if not show_axes:
            self.plot_widget.getAxis('left').hide()
            self.plot_widget.getAxis('bottom').hide()
            self.plot_widget.getPlotItem().setMenuEnabled(False)
        else:
            self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
            self.plot_widget.getAxis('left').setPen(AppColors.TEXT_MUTED)
            self.plot_widget.getAxis('bottom').setPen(AppColors.TEXT_MUTED)

        if not interactive:
            self.plot_widget.setMouseEnabled(x=False, y=False)
            self.plot_widget.hideButtons()

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color=AppColors.PRIMARY, width=2))
        
        # Gradient Fill
        # Create a fill between the curve and zero (or min value)
        # Note: pyqtgraph's FillBetweenItem is simple, for gradient we might need Brush
        self.fill = pg.FillBetweenItem(
            self.curve, 
            pg.PlotDataItem([0, 1], [0, 0]), 
            brush=pg.mkBrush(color=(0, 122, 204, 40)) # Translucent Blue
        )
        self.plot_widget.addItem(self.fill)

        layout.addWidget(self.plot_widget)

    def update_chart(self, data):
        """Update chart with new price history data."""
        if not data:
            self.curve.setData([])
            return
        
        # Color based on change
        color = AppColors.ACCENT_GREEN if data[-1] >= data[0] else AppColors.ACCENT_RED
        
        # Convert hex to RGB for brush
        c = pg.mkColor(color)
        brush_color = (c.red(), c.green(), c.blue(), 40)
        
        self.curve.setPen(pg.mkPen(color=color, width=2))
        self.curve.setData(data)
        
        # Update fill
        # We create a baseline at the minimum value to avoid filling to 0 if price is ~100
        y_min = min(data) * 0.999
        # Baseline must match x-axis length of data
        x_vals = range(len(data))
        baseline_curve = pg.PlotDataItem(x_vals, [y_min] * len(data))
        
        self.fill.setCurves(self.curve, baseline_curve)
        self.fill.setBrush(pg.mkBrush(color=brush_color))

class MiniSparkline(StockChartWidget):
    """Compact chart for index cards or tables."""
    def __init__(self):
        super().__init__(show_axes=False, interactive=False, background=AppColors.BG_CARD)
        self.setMinimumHeight(40)
        self.setMaximumHeight(60)
        self.setMinimumWidth(100)
