import sys
import os
import multiprocessing
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini AI Studio")
        self.setGeometry(100, 100, 1200, 800)

        # Khởi tạo giao diện Web Engine
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://gemini.google.com"))
        self.setCentralWidget(self.browser)

def main():
    # Bắt buộc dùng freeze_support() để tránh lỗi spam cửa sổ liên tục khi đóng gói EXE
    multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
