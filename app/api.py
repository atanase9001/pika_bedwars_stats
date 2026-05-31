import json
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import QUrl

class PikaAPI:
    def __init__(self):
        self.manager = QNetworkAccessManager()

    def fetch_everything(self, username, window_callback):
        # 1. list every single endpoint you want to hit
        # 1. list every single endpoint
        endpoints = {
            "profile": f"https://stats.pika-network.net/api/profile/{username}",
            
            # total intervals
            "lb_total_all": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=total&mode=ALL_MODES",
            "lb_total_solo": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=total&mode=SOLO",
            "lb_total_doubles": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=total&mode=DOUBLES",
            "lb_total_quad": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=total&mode=QUAD",
            
            # monthly intervals
            "lb_monthly_all": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=monthly&mode=ALL_MODES",
            "lb_monthly_solo": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=monthly&mode=SOLO",
            "lb_monthly_doubles": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=monthly&mode=DOUBLES",
            "lb_monthly_quad": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=monthly&mode=QUAD",
            
            # weekly intervals
            "lb_weekly_all": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=weekly&mode=ALL_MODES",
            "lb_weekly_solo": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=weekly&mode=SOLO",
            "lb_weekly_doubles": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=weekly&mode=DOUBLES",
            "lb_weekly_quad": f"https://stats.pika-network.net/api/profile/{username}/leaderboard?type=bedwars&interval=weekly&mode=QUAD"
        }

        # 2. this dictionary will hold all combined data
        big_ass_json = {}
        
        # 3. track how many requests are currently running
        pending_requests = len(endpoints)

        # 4. this internal function runs whenever ANY of the requests finish
        def handle_reply(reply, key):
            nonlocal pending_requests
            
            raw_data = reply.readAll().data()
            try:
                # parse the json and throw it into our main dictionary under its specific key
                big_ass_json[key] = json.loads(raw_data.decode("utf-8"))
            except Exception:
                big_ass_json[key] = {"error": "failed to parse or empty response"}
            
            reply.deleteLater()
            pending_requests -= 1

            # 5. once the counter hits 0, everything is done. send it back to window.py
            if pending_requests == 0:
                window_callback(big_ass_json)

        # 6. loop through your endpoints and fire them all at once
        for key, url_str in endpoints.items():
            request = QNetworkRequest(QUrl(url_str))
            reply = self.manager.get(request)
            
            # python loop trick: r=reply and k=key freeze the current values 
            # so the lambda doesn't get confused by the loop
            reply.finished.connect(lambda r=reply, k=key: handle_reply(r, k))