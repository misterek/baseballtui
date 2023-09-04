from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.widget import Widget
from textual.coordinate import Coordinate
from rich.text import Text
import sys
import statsapi
from datetime import datetime
import time 
from textual.reactive import reactive
import calendar
import random
from textual.containers import Horizontal, Vertical
OCCUPIED_BASE = '\u2b25'
EMPTY_BASE    = '\u2b26'

class GameState():
    def __init__(self):
        self.full_results = {}
        self.updated_at = datetime.now()
        self.home_team = ""
        self.away_team = ""
        self.home_team_abbreviation = ""
        self.away_team_abbreviation = ""
        self.home_innings = []
        self.away_innings = []
        self.home_runs = 0
        self.home_hits = 0
        self.home_errors = 0
        self.away_runs = 0
        self.away_hits = 0
        self.away_errors = 0



        # Lineups
        self.home_lineup = []
        self.away_lineup = []

    def get_player_name(self, id):
        return self.full_results['gameData']['players']['ID' + str(id)]['lastName']
    
    # gets their current position in this game, since that's all I care about. At least I think that's what this is.
    def get_player_position(self, id):
        if 'ID' + str(id) in self.full_results['liveData']['boxscore']['teams']['away']['players']:   
            return self.full_results['liveData']['boxscore']['teams']['away']['players']['ID' + str(id)]['position']['abbreviation']
        return self.full_results['liveData']['boxscore']['teams']['home']['players']['ID' + str(id)]['position']['abbreviation']
    
    def get_player_ab(self, id):
        if 'ID' + str(id) in self.full_results['liveData']['boxscore']['teams']['away']['players']:
            player = self.full_results['liveData']['boxscore']['teams']['away']['players']['ID' + str(id)]
        else:
            player = self.full_results['liveData']['boxscore']['teams']['home']['players']['ID' + str(id)]
        
        try:
            return str(player['stats']['batting']['hits']) + "-" + str(player['stats']['batting']['atBats'])
        except:
            return("")




    


class Lineup(Vertical):

    def on_mount(self) -> None:
        lineup_table = self.query_one(DataTable)
        lineup_table.add_column("", key="order")
        lineup_table.add_column("Pos", key="position")
        lineup_table.add_column("Player", key="player")
        lineup_table.add_column("Stats", key="stats")
        lineup_table.add_row("1", key="0")
        lineup_table.add_row("2", key="1")
        lineup_table.add_row("3", key="2")
        lineup_table.add_row("4", key="3")
        lineup_table.add_row("5", key="4")
        lineup_table.add_row("6", key="5")
        lineup_table.add_row("7", key="6")
        lineup_table.add_row("8", key="7")
        lineup_table.add_row("9", key="8")

    def compose(self) -> ComposeResult:
        yield Static("Chicago Cubs", id="teamname")
        yield DataTable()

    # Reactivity might be an option?
    def thing(self):
        a = reactive(self.gs)   
        self.styles.visibility = "hidden"
        a=1

class LineScore(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("", id="innings")
        yield Static("", id="away")
        yield Static("", id="home")
        yield Static("", id="pitchers")



class BoxScores(App):

    def update_game_state(self):
        game_state =  statsapi.get('game', {'gamePk' : "716732"}) 
        self.game_state.full_results = game_state

        # shortName also available
        # record available
        # weather available
        self.game_state.home_team = game_state['gameData']['teams']['home']['name']
        self.game_state.away_team = game_state['gameData']['teams']['away']['name']

        self.game_state.home_team_abbreviation = game_state['gameData']['teams']['home']['abbreviation']
        self.game_state.away_team_abbreviation = game_state['gameData']['teams']['away']['abbreviation']


        self.game_state.home_lineup = game_state['liveData']['boxscore']['teams']['home']['battingOrder']
        self.game_state.away_lineup = game_state['liveData']['boxscore']['teams']['away']['battingOrder']


        # Do this elsewhere eventually
        away_lineup = self.query_one("#awaylineup")
        away_lineup.query_one("#teamname").update(self.game_state.away_team)
        lineup_table = away_lineup.query_one(DataTable)

        for location, player_id in enumerate(self.game_state.away_lineup):
            lineup_table.update_cell(str(location), "player", self.game_state.get_player_name(player_id) )
            lineup_table.update_cell(str(location), "position", self.game_state.get_player_position(player_id) )
            lineup_table.update_cell(str(location), "stats", self.game_state.get_player_ab(player_id) )

        home_lineup = self.query_one("#homelineup")
        home_lineup.query_one("#teamname").update(self.game_state.home_team)
        lineup_table = home_lineup.query_one(DataTable)

        for location, player_id in enumerate(self.game_state.home_lineup):
            lineup_table.update_cell(str(location), "player", self.game_state.get_player_name(player_id) )
            lineup_table.update_cell(str(location), "position", self.game_state.get_player_position(player_id) )
            lineup_table.update_cell(str(location), "stats", self.game_state.get_player_ab(player_id) )
        

        self.game_state.away_innings = []
        self.game_state.home_innings = []

        # I have confused myself between updating the object and the display
        # should move lal of this over to the gamestate class
        for inning in game_state['liveData']['linescore']['innings']:
            if 'runs' in inning['away']:
                self.game_state.away_innings.append(str(inning['away']['runs']))
            if 'runs' in inning['home']:
                self.game_state.home_innings.append(str(inning['home']['runs']))


        self.game_state.away_runs = game_state['liveData']['linescore']['teams']['away']['runs']
        self.game_state.home_runs = game_state['liveData']['linescore']['teams']['home']['runs']
        self.game_state.away_hits = game_state['liveData']['linescore']['teams']['away']['hits']
        self.game_state.home_hits = game_state['liveData']['linescore']['teams']['home']['hits']      
        self.game_state.away_errors = game_state['liveData']['linescore']['teams']['away']['errors']
        self.game_state.home_errors = game_state['liveData']['linescore']['teams']['home']['errors']   


        # Spacing
        # 10 for team
        # 3 for each inning
        # 2 spaces
        # 3 for R, H, E
        # WTF do I do with extra innings?
        # 10 + 27 + 9 == 46

        # Don't really need to worry about updating this often

        innings = self.query_one("#innings")
        innings.update(Text("            1  2  3  4  5  6  7  8  9    R  H  E", justify="center"))
        away_lineup = self.query_one("#away")
        home_lineup = self.query_one("#home")

        away_text = Text((self.game_state.away_team_abbreviation +  "          ")[0:10], justify="center")
        home_text = Text((self.game_state.home_team_abbreviation +  "          ")[0:10], justify="center")

        for inning in self.game_state.away_innings:
            away_text = away_text + Text(("    " + inning)[-3:])

        for inning in self.game_state.home_innings:
            home_text = home_text + Text(("    " + inning)[-3:])

        # Spaces between 9 and R
        away_text = away_text + Text("  ") 
        home_text = home_text + Text("  ")

        # Add R, H, E
        away_text = away_text + Text( ("    " + str(self.game_state.away_runs))[-3:])
        away_text = away_text + Text( ("    " + str(self.game_state.away_hits))[-3:])
        away_text = away_text + Text( ("    " + str(self.game_state.away_errors))[-3:])
        home_text = home_text + Text( ("    " + str(self.game_state.home_runs))[-3:])
        home_text = home_text + Text( ("    " + str(self.game_state.home_hits))[-3:])
        home_text = home_text + Text( ("    " + str(self.game_state.home_errors))[-3:])

        away_lineup.update(away_text)
        home_lineup.update(home_text)

        pitchers_line = self.query_one("#pitchers")

        pitchers_text = Text("P:  " + self.game_state.full_results['liveData']['linescore']['defense']['pitcher']['fullName'] + "    " + "AB: " + self.game_state.full_results['liveData']['linescore']['offense']['batter']['fullName'] , justify="center")

        pitchers_line.update(pitchers_text)
        self.game_state.updated_at = datetime.now()




    BINDINGS = [("q", "quit", "Quit")]

    CSS_PATH = "gameday.css"

    def on_mount(self) -> None:
        self.game_state = GameState()
        self.update_game_state()
        self.mytimer = self.set_interval(15, self.update_game_state )


        t = self.query_one(".gameday")

        text = Text("CenterMe", justify="center")
        text = text + Text("\n") 
        text = text + Text(OCCUPIED_BASE) + Text("\n")
        text = text + Text("/", justify="", style="white") + Text(" ", style="green on green") + Text("\\", justify="right" ,style="white") + Text("\n")
        text = text + Text("/", justify="", style="white") + Text("   ", style="green on green") + Text("\\", justify="right" ,style="white") + Text("\n")
        text = text + Text("/", justify="", style="white") + Text("     ", style="green on green") + Text("\\", justify="right" ,style="white") + Text("\n")
        text = text + Text("/", justify="", style="white") + Text("       ", style="green on green") + Text("\\", justify="right" ,style="white") 
        t.update(text)


    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="horizontal"):
               yield Lineup(classes="lineup", id="awaylineup")
               yield Static("H2", classes="gameday")
               yield Lineup(classes="lineup", id="homelineup")

            yield LineScore(classes="linescore")

    def action_quit(self) -> None:
        sys.exit()


if __name__ == "__main__":
    app = BoxScores()
    app.run()
