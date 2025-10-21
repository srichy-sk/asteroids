import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buttons")
        self.setGeometry(250, 300, 600, 600)
        self.initUI()

    def initUI(self):
        self.button = QPushButton("Click Me!", self)
        self.button.setGeometry(150, 200, 200, 200)
        self.button.setStyleSheet("font-size: 30px;")
        self.button.clicked.connect(self.on_click)  # Connects the button's clicked signal to on_click

    def on_click(self):
        self.button.setText("Clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())