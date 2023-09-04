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
from gamestate import GameState

#OCCUPIED_BASE = '\u2b25'
OCCUPIED_BASE = '\u2662'
EMPTY_BASE    = '\u2b26'





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

        self.game_state.update()


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

    BINDINGS = [("q", "quit", "Quit")]

    CSS_PATH = "gameday.css"

    def on_mount(self) -> None:
        self.game_state = GameState()
        self.update_game_state()
        self.mytimer = self.set_interval(15, self.update_game_state )


        t = self.query_one(".gameday")

        SLASH = Text("/", style="white on brown")
        BACKSLASH = Text("\\", style="white on brown")
        SPACES = [
            Text(" ", style="green on green"),
            Text("     ", style="green on green"),
            Text("       ", style="green on green"),
            Text("         ", style="green on green"),
            Text("           ", style="green on green"),
            Text("             ", style="green on green")
        ]
        NL = Text("\n")

        text = Text("Cubs vs. Dodgers", justify="center") + NL
        text += Text(OCCUPIED_BASE) + NL

        for space in SPACES:
            text += SLASH + space + BACKSLASH + NL

        text += Text(OCCUPIED_BASE, justify="", style="white") + SPACES[-1] + Text(OCCUPIED_BASE, justify="", style="white") + Text("\n")

        #text += Text(OCCUPIED_BASE, justify="", style="white") + Text("         ", style="green on green") + Text(OCCUPIED_BASE, justify="", style="white") + Text("\n")
       
        for space in reversed(SPACES):
            text += BACKSLASH + space + SLASH + NL


        # text = Text("Cubs vs. Dodgers", justify="center")
        # text = text + NL
        # text += Text(OCCUPIED_BASE) + NL
        # text += SLASH + SPACE1 + BACKSLASH + NL
        # text += SLASH + Text("   ", style="green on green") + BACKSLASH + Text("\n")
        # text += SLASH + Text("     ", style="green on green") + BACKSLASH + Text("\n")
        # text += SLASH + Text("       ", style="green on green") + BACKSLASH + Text("\n")
        # text += Text(OCCUPIED_BASE, justify="", style="white") + Text("         ", style="green on green") + Text(OCCUPIED_BASE, justify="", style="white") + Text("\n")
        # text += BACKSLASH + Text("       ", style="green on green") + SLASH + Text("\n")
        # text += BACKSLASH + Text("     ", style="green on green") + SLASH + Text("\n")
        # text += BACKSLASH + Text("   ", style="green on green") + SLASH + Text("\n")
        # text += BACKSLASH + Text(" ", style="green on green") + SLASH + Text("\n")
        
 # ⟋

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
