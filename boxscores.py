from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.widget import Widget
from rich.text import Text
import sys
import statsapi
from datetime import datetime
import time 
import calendar
import random


# Unicode characters
OCCUPIED_BASE = '\u2b25'
EMPTY_BASE    = '\u2b26'
BOTTOM_INNING = '\u23f7'
TOP_INNING    = '\u23f6'

class BoxScore(Widget):


    def set_game_id(self, game_id, start_info):
        self.game_id = game_id
        self.start_info = start_info
        self.mytimer = self.set_interval(2, self.update_game )
        return self

    def update_game(self):

        team1 = self.query_one("#team1")
        team2 = self.query_one("#team2")
        info1 = self.query_one("#info1")
        info2 = self.query_one("#info2")
        info3 = self.query_one("#info3")
        info4 = self.query_one("#info4")
        info5 = self.query_one("#info5")

        away_team = Text(self.start_info['away_name'])
        away_team.set_length(21)

        home_team = Text(self.start_info['home_name'])
        home_team.set_length(21)

        if self.start_info['status'] == "Pre-Game" or self.start_info['status'] == "Scheduled":
            # Make sure the timer is only 90 seconds. no need to update this more 
            # regularly
            if self.mytimer._interval != 90:
                self.mytimer.stop()
                self.mytimer = self.set_interval(90, self.update_game )
            team1.update(away_team)
            team2.update(home_team)
            utc_time = time.strptime(self.start_info['game_datetime'], "%Y-%m-%dT%H:%M:%SZ")
            utc_seconds = calendar.timegm(utc_time)
            local_time = time.strftime("%I:%M %Z", time.localtime(utc_seconds))
            info1.update(self.start_info['status'])
            info2.update(local_time)
            info3.update("Starting Pitchers:")
            info4.update("Away: " + self.start_info['away_probable_pitcher'])
            info5.update("Home: " + self.start_info['home_probable_pitcher'])



        else:


            x =  statsapi.get('game', {'gamePk' : str(self.game_id)}) 

            r = str(x['liveData']['linescore']['teams']['away']['runs']).rjust(2)
            h = str(x['liveData']['linescore']['teams']['away']['hits']).rjust(2)
            e = str(x['liveData']['linescore']['teams']['away']['errors']).rjust(2)

            team1.update(away_team + Text(r + " " + h + " " + e , justify="right"))

            r = str(x['liveData']['linescore']['teams']['home']['runs']).rjust(2)
            h = str(x['liveData']['linescore']['teams']['home']['hits']).rjust(2)
            e = str(x['liveData']['linescore']['teams']['home']['errors']).rjust(2)

            team2.update(home_team + Text(r + " " + h + " " + e , justify="right"))
            
            if self.start_info['status'] == "Final":
                if self.mytimer._interval != 90:
                    self.mytimer.stop()
                    self.mytimer = self.set_interval(90, self.update_game )

                info1.update("Final")
                info2.update("")
                info3.update("WP: " + x['liveData']['decisions']['winner']['fullName'])
                info4.update("LP: " + x['liveData']['decisions']['loser']['fullName'])

            else:
                if self.mytimer._interval != 10:
                    self.mytimer.stop()
                    self.mytimer = self.set_interval(10, self.update_game  )
                first_occupied = False
                second_occupied = False
                third_occupied = False
                if 'first' in x['liveData']['linescore']['offense']:
                    first_occupied = True
                if 'second' in x['liveData']['linescore']['offense']:
                    second_occupied = True
                if 'third' in x['liveData']['linescore']['offense']:
                    third_occupied = True

                info1.update(str(x['liveData']['linescore']['balls']) + "-" + str(x['liveData']['linescore']['strikes']) + " " + str(x['liveData']['linescore']['outs']) + "o  " + (OCCUPIED_BASE if second_occupied else EMPTY_BASE))

                info2.update( (TOP_INNING if x['liveData']['linescore']['isTopInning'] else BOTTOM_INNING)  + " " + 
                            x['liveData']['linescore']['currentInningOrdinal'].rjust(4) + " " + 
                            (OCCUPIED_BASE if third_occupied else EMPTY_BASE) + " " + 
                            (OCCUPIED_BASE if first_occupied else EMPTY_BASE))

                info3.update("P:  " + x['liveData']['linescore']['defense']['pitcher']['fullName'])

                info4.update("AB: " + x['liveData']['linescore']['offense']['batter']['fullName'] )
        self.styles.visibility = "visible"


    def compose(self) -> ComposeResult:

        yield Static(id="team1")
        yield Static(id="team2")
        yield Static(id="info1")
        yield Static(id="info2")
        yield Static(id="info3")
        yield Static(id="info4")
        yield Static(id="info5")


class MLBApp(App):

    BINDINGS = [("q", "quit", "Quit")]

    CSS_PATH = "boxscores.css"


    def compose(self) -> ComposeResult:
        today = datetime.today().strftime('%m/%d/%Y')
        sched = statsapi.schedule(start_date=today,end_date=today)
        yield Header()

        for game in sched:
            yield BoxScore(classes="box", id="game_id_" + str(game['game_id'])).set_game_id(str(game['game_id']), game)

        yield Footer()

    def action_quit(self) -> None:
        sys.exit()


if __name__ == "__main__":
    app = MLBApp()
    app.run()
