# sahelper/ui/styles.py

class AppColors:
    # Backgrounds
    BG_MAIN = "#121212"       # Deepest background
    BG_SIDEBAR = "#1e1e1e"    # Sidebar / Panels
    BG_CARD = "#252525"       # Cards / Content blocks
    BG_INPUT = "#2d2d2d"      # Input fields
    
    # Accents
    PRIMARY = "#007acc"       # VS Code Blue / Main Action
    ACCENT_GREEN = "#00c853"  # Success / Gain
    ACCENT_RED = "#ff3d00"    # Error / Loss
    ACCENT_BLUE = "#2979ff"   # Info / Action
    ACCENT_YELLOW = "#ffd600" # Warning
    
    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#666666"
    
    # Borders
    BORDER = "#333333"

class AppStyles:
    """Centralized QSS Stylesheets for the application."""
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {AppColors.BG_MAIN};
        }}
        QWidget {{
            color: {AppColors.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 14px;
        }}
    """
    
    SIDEBAR = f"""
        QListWidget {{
            background-color: {AppColors.BG_SIDEBAR};
            border: none;
            border-right: 1px solid {AppColors.BORDER};
            outline: none;
        }}
        QListWidget::item {{
            padding: 12px 20px;
            margin: 4px 8px;
            border-radius: 6px;
            color: {AppColors.TEXT_SECONDARY};
            font-weight: 500;
        }}
        QListWidget::item:hover {{
            background-color: #2a2a2a;
            color: {AppColors.TEXT_PRIMARY};
        }}
        QListWidget::item:selected {{
            background-color: {AppColors.PRIMARY};
            color: white;
            border: none;
        }}
    """
    
    CARD = f"""
        QFrame.Card {{
            background-color: {AppColors.BG_CARD};
            border: 1px solid {AppColors.BORDER};
            border-radius: 10px;
        }}
        QLabel.CardTitle {{
            color: {AppColors.TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QLabel.CardValue {{
            color: {AppColors.TEXT_PRIMARY};
            font-size: 26px;
            font-weight: 700;
        }}
    """

    INPUT = f"""
        QLineEdit {{
            background-color: {AppColors.BG_INPUT};
            border: 1px solid {AppColors.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            color: {AppColors.TEXT_PRIMARY};
            selection-background-color: {AppColors.PRIMARY};
        }}
        QLineEdit:focus {{
            border: 1px solid {AppColors.PRIMARY};
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {AppColors.PRIMARY};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #008be6;
        }}
        QPushButton:pressed {{
            background-color: #005f9e;
        }}
    """
    
    TABLE = f"""
        QTableView {{
            background-color: {AppColors.BG_MAIN};
            gridline-color: {AppColors.BORDER};
            border: none;
            selection-background-color: #2a2a2a;
            selection-color: {AppColors.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background-color: {AppColors.BG_SIDEBAR};
            padding: 8px;
            border: none;
            border-bottom: 2px solid {AppColors.BORDER};
            font-weight: 600;
            color: {AppColors.TEXT_SECONDARY};
        }}
    """
