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

OCCUPIED_BASE = '\u2662'
EMPTY_BASE    = '\u2b26'

class BoxScores(App):

    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "gameday.css"


    def on_mount(self) -> None:

        t = self.query_one(".firstthing")
        t.update(Text("" + OCCUPIED_BASE, justify="center"))
        t = self.query_one(".secondthing")
        t.update(Text("A", justify="center"))

    def compose(self) -> ComposeResult:
        yield Static("H2", classes="firstthing")
        yield Static("H2", classes="secondthing")


        #yield Static("H2", classes="gameday")


    def action_quit(self) -> None:
        sys.exit()


if __name__ == "__main__":
    app = BoxScores()
    app.run()
