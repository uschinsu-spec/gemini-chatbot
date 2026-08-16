import sys, os, subprocess, time
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView

def get_res(rel):
    return os.path.join(sys._MEIPASS, rel) if hasattr(sys, '_MEIPASS') else os.path.join(os.path.abspath("."), rel)

def main():
    cmd = [sys.executable, "-m", "streamlit", "run", get_res("app.py"), "--server.headless=true", "--server.port=8501"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("Gemini AI Studio")
    win.setGeometry(100, 100, 1200, 800)
    web = QWebEngineView()
    web.setUrl(QUrl("http://localhost:8501"))
    win.setCentralWidget(web)
    win.show()
    ret = app.exec()
    proc.kill()
    sys.exit(ret)

if __name__ == "__main__":
    main()
