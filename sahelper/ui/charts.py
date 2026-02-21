import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from .styles import AppColors

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
