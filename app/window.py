from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow:
    def __init__(self):
        # point this to wherever you saved your .ui file
        ui_file = QFile("assets/design.ui")
        ui_file.open(QFile.ReadOnly)
        
        # create the actual window object from the file
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        
        # this is where you will hook up your buttons later.
        # if you named a button "search_btn" in qt designer, you'd do:
        # self.ui.search_btn.clicked.connect(self.fetch_stats)

    def show(self):
        # displays the loaded ui on the screen
        self.ui.show()