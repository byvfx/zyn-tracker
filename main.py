import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QRegion, QFont, QColor


class RoundZynApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 400)
        self.counter = 0

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Today label
        today_label = QLabel("Today")
        today_label.setAlignment(Qt.AlignCenter)
        today_label.setFont(QFont("Arial", 14))

        # Counter display
        self.counter_label = QLabel(str(self.counter))
        self.counter_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.counter_label.setAlignment(Qt.AlignCenter)

        # Buttons
        btn_layout = QHBoxLayout()
        minus_btn = QPushButton("–")
        plus_btn = QPushButton("+")
        for btn in (minus_btn, plus_btn):
            btn.setFixedSize(50, 50)
            btn.setFont(QFont("Arial", 20))
            btn.setStyleSheet("border-radius: 25px; background-color: #ddd;")

        minus_btn.clicked.connect(self.decrease)
        plus_btn.clicked.connect(self.increase)

        btn_layout.addWidget(minus_btn)
        btn_layout.addWidget(plus_btn)
        btn_layout.setAlignment(Qt.AlignCenter)

        # Add widgets
        main_layout.addWidget(today_label)
        main_layout.addWidget(self.counter_label)
        main_layout.addLayout(btn_layout)
        
        # Add exit button
        exit_btn = QPushButton("X")
        exit_btn.setFixedSize(40, 40)
        exit_btn.setFont(QFont("Arial", 12, QFont.Bold))
        exit_btn.setStyleSheet("border-radius: 20px; background-color: #ff6b6b; color: white;")
        exit_btn.clicked.connect(self.close)
        
        # Add some spacing before the exit button
        main_layout.addSpacing(20)
        main_layout.addWidget(exit_btn, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def paintEvent(self, event):
        # Make it a circle
        region = QRegion(QRect(0, 0, 400, 400), QRegion.Ellipse)
        self.setMask(region)

        # Paint background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#f2f2f2"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 400, 400)

    def increase(self):
        self.counter += 1
        self.update_ui()

    def decrease(self):
        self.counter = max(0, self.counter - 1)
        self.update_ui()

    def update_ui(self):
        self.counter_label.setText(str(self.counter))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoundZynApp()
    window.show()
    sys.exit(app.exec())
