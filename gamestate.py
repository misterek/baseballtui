from datetime import datetime
import statsapi

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


    def update(self):

        # Don't hardcode game eventually
        game_state =  statsapi.get('game', {'gamePk' : "716732"}) 
        self.full_results = game_state

        # shortName also available
        # record available
        # weather available
        self.home_team = game_state['gameData']['teams']['home']['name']
        self.away_team = game_state['gameData']['teams']['away']['name']

        self.home_team_abbreviation = game_state['gameData']['teams']['home']['abbreviation']
        self.away_team_abbreviation = game_state['gameData']['teams']['away']['abbreviation']


        self.home_lineup = game_state['liveData']['boxscore']['teams']['home']['battingOrder']
        self.away_lineup = game_state['liveData']['boxscore']['teams']['away']['battingOrder']

        self.away_innings = []
        self.home_innings = []

        # I have confused myself between updating the object and the display
        # should move lal of this over to the gamestate class
        for inning in game_state['liveData']['linescore']['innings']:
            if 'runs' in inning['away']:
                self.away_innings.append(str(inning['away']['runs']))
            if 'runs' in inning['home']:
                self.home_innings.append(str(inning['home']['runs']))


        self.away_runs = game_state['liveData']['linescore']['teams']['away']['runs']
        self.home_runs = game_state['liveData']['linescore']['teams']['home']['runs']
        self.away_hits = game_state['liveData']['linescore']['teams']['away']['hits']
        self.home_hits = game_state['liveData']['linescore']['teams']['home']['hits']      
        self.away_errors = game_state['liveData']['linescore']['teams']['away']['errors']
        self.home_errors = game_state['liveData']['linescore']['teams']['home']['errors']   


        self.updated_at = datetime.now()
