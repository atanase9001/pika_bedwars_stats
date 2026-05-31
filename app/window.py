from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QButtonGroup, QLabel
from app.api import PikaAPI

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
        name = button.objectName().lower()
        
        # force it to perfectly match our api keys
        if "week" in name:
            self.current_interval = "weekly"
        elif "month" in name:
            self.current_interval = "monthly"
        else:
            self.current_interval = "total"
            
        print(f"interval variable changed to: {self.current_interval}")
        
        # trigger the UI update
        self.refresh_displayed_stats()

    def update_mode_var(self, text):
        self.current_mode = text
        print(f"mode variable changed to: {self.current_mode}")
        
        # trigger the UI update
        self.refresh_displayed_stats()


    def fetch_stats(self):
        username = self.ui.username_input.text()
        if not username:
            return
        
        self.ui.loadingLabel.setText("Getting data...")
        self.ui.search_button.setEnabled(False)
        self.api.fetch_everything(username, self.handle_ui_update)

    def refresh_displayed_stats(self):
        # 1. if they haven't clicked search yet, do nothing so it doesn't crash
        if not hasattr(self, 'cached_stats') or not self.cached_stats:
            return
            
        # 2. the interval is already formatted nicely (total, monthly, weekly)
        interval = self.current_interval
        
        # 3. map the exact dropdown text to the api suffixes you made
        mode_text = self.current_mode
        if "All" in mode_text:
            mode = "all"
        elif "Solo" in mode_text:
            mode = "solo"
        elif "Double" in mode_text:
            mode = "doubles"
        elif "Quad" in mode_text: # matches Quad, Quadruples, etc.
            mode = "quad"
        else:
            mode = "all" # fallback just in case
            
        # 4. glue them together to match your api.py keys perfectly
        target_key = f"lb_{interval}_{mode}"
        print(f"swapping UI to: {target_key}")
        
        # 5. pull that specific chunk from the cache and update the screen
        dataset = self.cached_stats.get(target_key, {})
        self.populate_ui(dataset)

    def handle_ui_update(self, compiled_data):
        self.ui.search_button.setEnabled(True)
        self.ui.loadingLabel.setText("")
        
        # save the whole thing into cache
        self.cached_stats = compiled_data
        
        # now you can easily read whatever you need
        default_dataset = self.cached_stats.get("lb_total_all", {})
        self.populate_ui(default_dataset)

    def update_card(self, frame, big_number):
        labels = frame.findChildren(QLabel)

        labels[1].setText(str(big_number))

    def populate_ui(self, dataset):
        # 1. grab all the raw numbers safely using our new helper
        wins = self.get_stat(dataset, "Wins")
        losses = self.get_stat(dataset, "Losses")
        final_kills = self.get_stat(dataset, "Final kills")
        final_deaths = self.get_stat(dataset, "Final deaths")
        highest_ws = self.get_stat(dataset, "Highest winstreak reached")
        beds_destroyed = self.get_stat(dataset, "Beds destroyed")
        total_kills = self.get_stat(dataset, "Kills")
        total_deaths = self.get_stat(dataset, "Deaths")
        
        # 2. calculate ratios safely (the if statements prevent "divide by zero" crashes)
        fkdr = round(final_kills / final_deaths, 2) if final_deaths > 0 else final_kills
        wlr = round(wins / losses, 2) if losses > 0 else wins
        kdr = round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills

        # 3. push the data straight into your UI frames
        # format: self.update_card(frame_object, big_number, sub_text)
        self.update_card(self.ui.fkdrFrame, fkdr)
        self.update_card(self.ui.kdrFrame, kdr)
        self.update_card(self.ui.wlrFrame, wlr) 
        self.update_card(self.ui.finalKillsFrame, f"{final_kills:,}")
        self.update_card(self.ui.finalDeathsFrame, f"{final_deaths:,}")
        self.update_card(self.ui.winsFrame, f"{wins:,}")
        self.update_card(self.ui.lossesFrame, f"{losses:,}")
        self.update_card(self.ui.totalKillsFrame, f"{total_kills:,}")
        self.update_card(self.ui.highestWsFrame, f"{highest_ws:,}")
        self.update_card(self.ui.bedsDestroyedFrame, f"{beds_destroyed:,}")

    def get_stat(self, dataset, key_name):
        try:
            # tries to dig through the messy json path
            return int(dataset[key_name]["entries"][0]["value"])
        except (KeyError, IndexError, TypeError):
            # if they aren't ranked or the data is missing, just return 0
            return 0

    def show(self):
        self.ui.show()