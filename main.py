import sys
import json
from datetime import date
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
)
from PySide6.QtCore import Qt, QRect, QPoint, QSize, QRectF
from PySide6.QtGui import (
    QPainter, QRegion, QFont, QColor, QMouseEvent, QPixmap, QPen, QBrush,
    QPainterPath, QFontDatabase
)

# --- Constants (remain the same) ---
APP_NAME = "ZynTracker"
WINDOW_SIZE = 400
CONTENT_PADDING = 5
BUTTON_SIZE = 45
BUTTON_RADIUS = BUTTON_SIZE // 2
EXIT_BUTTON_SIZE = 25
EXIT_BUTTON_RADIUS = EXIT_BUTTON_SIZE // 2
DATA_FILE = "zyn_data.json"
CUSTOM_FONT_FILE = "F_G Heavy.ttf"

# --- Colors (remain the same) ---
COLOR_ZYN_GREEN = QColor("#00693E")
COLOR_FLAVOR_DEFAULT = COLOR_ZYN_GREEN
COLOR_BACKGROUND_LIGHT = QColor("#F0F0F0")
COLOR_CUTOUT_BG = QColor("#F0F0F0") 
COLOR_OUTER_RIM = QColor("#FFFFFF")
COLOR_BUTTON_BG = QColor("#E0E0E0")
COLOR_BUTTON_HOVER_BG = QColor("#C8C8C8")
COLOR_BUTTON_PRESSED_BG = QColor("#BDBDBD")
COLOR_EXIT_BG = QColor("#A0A0A0")
COLOR_EXIT_HOVER_BG = QColor("#888888")
COLOR_EXIT_PRESSED_BG = QColor("#666666")
COLOR_TEXT_ON_GREEN = QColor("#FFFFFF")
COLOR_TEXT_ON_LIGHT = QColor("#212121") # Text color for counter/today
COLOR_EXIT_TEXT = QColor("#FFFFFF")

# --- Font Constants (remain the same) ---
ZYN_LOGO_FONT_SIZE = 75
FONT_SUB_LABEL = QFont("Arial Bold", 14)
FONT_COUNTER = QFont("Arial Bold", 60)
FONT_BUTTON = QFont("Arial Black", 20)
FONT_EXIT = QFont("Arial", 10, QFont.Weight.Bold)

# --- Rim & Cutout Geometry (remain the same) ---
RIM_THICKNESS = 20
CUTOUT_HEIGHT_FACTOR = .6
CUTOUT_WIDTH_FACTOR = 0.6

# Global variable for the loaded Zyn font (or fallback)
zyn_font = None

class RoundZynApp(QWidget):
    # __init__ and other methods remain the same as the previous version
    def __init__(self, logo_font: QFont):
        super().__init__()
        self.logo_font = logo_font
        self.data = {}
        self.today_str = date.today().isoformat()
        self.load_data()
        self.dragPos = None
        self.flavor_color = COLOR_FLAVOR_DEFAULT
        self.init_window()
        self.init_ui()
        self.update_ui()

    def init_window(self):
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )

    def init_ui(self):
        # UI Setup remains the same
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        padding = CONTENT_PADDING + RIM_THICKNESS
        main_layout.setContentsMargins(padding, padding, padding, padding)
        main_layout.setSpacing(5)

        self.zyn_label = QLabel("ZYN")
        self.zyn_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.zyn_label.setFont(self.logo_font)
        self.zyn_label.setStyleSheet(f"color: {COLOR_TEXT_ON_GREEN.name()}; background-color: transparent;")
        self.zyn_label.setFixedHeight(130)

        self.today_label = QLabel("Today")
        self.today_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.today_label.setFont(FONT_SUB_LABEL)
        self.today_label.setStyleSheet(f"color: {COLOR_TEXT_ON_LIGHT.name()}; background-color: transparent;")
        self.today_label.setFixedHeight(25)

        self.counter_label = QLabel("0")
        self.counter_label.setFont(FONT_COUNTER)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.counter_label.setStyleSheet(f"color: {COLOR_TEXT_ON_LIGHT.name()}; background-color: transparent;")
        self.counter_label.setMinimumHeight(80)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(50)
        minus_btn = QPushButton("–")
        plus_btn = QPushButton("+")
        button_style = f"""QPushButton {{ border: 1px solid #B0B0B0; border-radius: {BUTTON_RADIUS}px; background-color: {COLOR_BUTTON_BG.name()}; color: {COLOR_TEXT_ON_LIGHT.name()}; padding-bottom: 3px; }} QPushButton:hover {{ background-color: {COLOR_BUTTON_HOVER_BG.name()}; }} QPushButton:pressed {{ background-color: {COLOR_BUTTON_PRESSED_BG.name()}; border: 1px solid #909090; }} """
        for btn in (minus_btn, plus_btn):
            btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            btn.setFont(FONT_BUTTON)
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minus_btn.clicked.connect(self.decrease)
        plus_btn.clicked.connect(self.increase)
        btn_layout.addWidget(minus_btn)
        btn_layout.addWidget(plus_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pouches_label = QLabel("ZYN POUCHES")
        self.pouches_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.pouches_label.setFont(FONT_SUB_LABEL)
        self.pouches_label.setStyleSheet(f"color: {COLOR_TEXT_ON_LIGHT.name()}; background-color: transparent;")
        self.pouches_label.setFixedHeight(30)

        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(EXIT_BUTTON_SIZE, EXIT_BUTTON_SIZE)
        exit_btn.setFont(FONT_EXIT)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.setStyleSheet(f""" QPushButton {{ border: none; border-radius: {EXIT_BUTTON_RADIUS}px; background-color: {COLOR_EXIT_BG.name()}; color: {COLOR_EXIT_TEXT.name()}; }} QPushButton:hover {{ background-color: {COLOR_EXIT_HOVER_BG.name()}; }} QPushButton:pressed {{ background-color: {COLOR_EXIT_PRESSED_BG.name()}; }} """)
        exit_btn.clicked.connect(self.close)

        main_layout.addWidget(self.zyn_label)
        main_layout.addStretch(1)
        main_layout.addWidget(self.today_label)
        main_layout.addWidget(self.counter_label)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.pouches_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)


    # --- Data Handling ---
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f: self.data = json.load(f)
            else: self.data = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data file {DATA_FILE}: {e}")
            self.data = {}
        self.counter = self.data.get(self.today_str, 0)

    def save_data(self):
        try:
            with open(DATA_FILE, 'w') as f: json.dump(self.data, f, indent=4)
        except IOError as e: print(f"Error saving data file {DATA_FILE}: {e}")

    # --- Event Handling ---
    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # --- Calculate Geometry (remains the same) ---
            outer_rect = self.rect()
            content_rect = QRectF(outer_rect).adjusted(1, 1, -1, -1)
            rim_rect = QRectF(content_rect).adjusted(RIM_THICKNESS / 2, RIM_THICKNESS / 2,
                                                   -RIM_THICKNESS / 2, -RIM_THICKNESS / 2)
            inner_rect = QRectF(rim_rect).adjusted(RIM_THICKNESS / 2, RIM_THICKNESS / 2,
                                                 -RIM_THICKNESS / 2, -RIM_THICKNESS / 2)
            center_x = inner_rect.center().x()
            center_y = inner_rect.center().y()

            cutout_width = inner_rect.width() * CUTOUT_WIDTH_FACTOR
            cutout_height = inner_rect.height() * CUTOUT_HEIGHT_FACTOR
            cutout_top_y = center_y - (cutout_height / 4)
            cutout_rect = QRectF(center_x - cutout_width / 2, cutout_top_y,
                                 cutout_width, cutout_height)

            # --- Define Cutout Path (needed for drawing the grey shape) ---
            cutout_shape_path = QPainterPath()
            cutout_shape_path.moveTo(cutout_rect.right(), cutout_rect.center().y())
            cutout_shape_path.arcTo(cutout_rect, 0.0, 180.0)
            cutout_shape_path.closeSubpath()


            # --- Draw Background Sections (Revised Order) ---
            painter.setPen(Qt.PenStyle.NoPen)

            # 1. Draw the LIGHT GREY bottom semi-circle FIRST
            painter.setBrush(COLOR_BACKGROUND_LIGHT)
            painter.drawPie(inner_rect, 180 * 16, 180 * 16)

            # 2. Draw the GREEN top semi-circle SECOND
            painter.setBrush(self.flavor_color)
            painter.drawPie(inner_rect, 0 * 16, 180 * 16)

            # 3. Draw the DARK GREY cutout shape THIRD (on top of previous two)
            painter.setBrush(COLOR_CUTOUT_BG)
            painter.drawPath(cutout_shape_path) # Use the path we defined

            # 4. Draw Outer Rim LAST
            rim_pen = QPen(COLOR_OUTER_RIM)
            rim_pen.setWidth(RIM_THICKNESS)
            painter.setPen(rim_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rim_rect)

            # 5. Set Mask (remains the same)
            mask_path = QPainterPath()
            mask_path.addEllipse(content_rect)
            region = QRegion(mask_path.toFillPolygon().toPolygon())
            self.setMask(region)

        finally:
            painter.end()


    # --- Other methods remain the same ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragPos:
            self.move(event.globalPosition().toPoint() - self.dragPos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = None
            event.accept()

    def closeEvent(self, event):
        self.save_data()
        super().closeEvent(event)

    def increase(self): self.counter += 1; self.update_data_and_ui()
    def decrease(self): self.counter = max(0, self.counter - 1); self.update_data_and_ui()
    def update_data_and_ui(self): self.data[self.today_str] = self.counter; self.save_data(); self.update_ui()
    def update_ui(self): self.counter_label.setText(str(self.counter))

    def set_flavor_color(self, new_color: QColor): self.flavor_color = new_color; self.update()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    # --- Load Custom Font (remains the same) ---
    font_db = QFontDatabase()
    font_id = font_db.addApplicationFont(CUSTOM_FONT_FILE)
    logo_font_family = "Arial"
    logo_font_weight = QFont.Weight.Bold
    if font_id != -1:
        families = font_db.applicationFontFamilies(font_id)
        if families:
            logo_font_family = families[0]
            logo_font_weight = QFont.Weight.Bold # Or QFont.Weight.Black
            print(f"Successfully loaded custom font: '{logo_font_family}'")
        else: print(f"Warning: Loaded font '{CUSTOM_FONT_FILE}' but could not find family name. Falling back.")
    else: print(f"Warning: Failed to load custom font '{CUSTOM_FONT_FILE}'. Falling back to Arial Bold.")

    zyn_logo_font = QFont(logo_font_family, ZYN_LOGO_FONT_SIZE, logo_font_weight)
    zyn_logo_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.ForceOutline)

    # --- Create and Show Window ---
    window = RoundZynApp(logo_font=zyn_logo_font)
    window.show()
    sys.exit(app.exec())