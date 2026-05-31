from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QButtonGroup
from app.api import PikaAPI  # import your new api class

import json

class MainWindow:
    def __init__(self):
        ui_file = QFile("assets/design.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        
        self.current_interval = "total"
        self.current_mode = "All Modes"

        # initialize the api handler
        self.api = PikaAPI()
        
        # 1. create the group FIRST
        
        self.modeGroup = QButtonGroup(self.ui)
        self.modeGroup.addButton(self.ui.weekly_btn)
        self.modeGroup.addButton(self.ui.monthly_btn)
        self.modeGroup.addButton(self.ui.total_btn)

        # 2. connect it AFTER it exists
        self.modeGroup.buttonClicked.connect(self.update_interval_var)
        self.ui.mode_dropdown.currentTextChanged.connect(self.update_mode_var)
        
        self.ui.search_button.clicked.connect(self.fetch_stats)
        
    def update_interval_var(self, button):
        # updates whenever a button is clicked
        self.current_interval = button.objectName().replace("_btn", "")
        print(f"interval variable changed to: {self.current_interval}")

    def update_mode_var(self, text):
        # updates whenever the dropdown changes
        self.current_mode = text
        print(f"mode variable changed to: {self.current_mode}")


    def fetch_stats(self):
        username = self.ui.username_input.text()
        if not username:
            return
        
        self.ui.loadingLabel.setText("Getting data...")
        self.ui.search_button.setEnabled(False)
        self.api.fetch_everything(username, self.handle_ui_update)

    def handle_ui_update(self, compiled_data):
        self.ui.search_button.setEnabled(True)
        self.ui.loadingLabel.setText("")
        
        # save the whole thing into cache
        self.cached_stats = compiled_data
        
        # now you can easily read whatever you need
        print(json.dumps(self.cached_stats.get("lb_total_all")))

    def show(self):
        self.ui.show()