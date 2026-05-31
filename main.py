import sys
from PySide6.QtWidgets import QApplication
from app.window import MainWindow  # this grabs your actual ui from the app folder

if __name__ == "__main__":
    # 1. create the core qt environment
    app = QApplication(sys.argv)
    
    # 2. load up your custom window and show it on screen
    
    window = MainWindow()
    window.show()
    
    # 3. start the event loop (keeps the app open until you click the X)
    sys.exit(app.exec())