import numpy as np
import pandas as pd
import scipy as sp

import os
import glob

from .team import Team
from .game import Game

def aggregate_coverages(coverages=[], game_count=True):
    combined_coverages = {}
    for coverage in coverages:
        for key in coverage.keys():
            if key not in combined_coverages:
                combined_coverages[key] = coverage[key]
                combined_coverages[key]['games played'] = 1
            else:
                for subkey in coverage[key].keys():
                    combined_coverages[key][subkey] += coverage[key][subkey]
                combined_coverages[key]['games played'] += 1
    
    return combined_coverages

def sort_plays_by_result(plays):
    completed = []
    incompleted = []
    intercepted = []
    other = []
    
    for play in plays:
        if play.play_data['passResult'] == 'C':
            completed.append(play)
        elif play.play_data['passResult'] == 'I':
            incompleted.append(play)
        elif play.play_data['passResult'] == 'IN':
            intercepted.append(play)
        else:
            other.append(play)
            
    sorted_plays = {}
    sorted_plays['completed'] = completed
    sorted_plays['incompleted'] = incompleted
    sorted_plays['intercepted'] = intercepted
    sorted_plays['other'] = other
            
    return sorted_plays

class Analysis:
    def __init__(self, basepath=''):
        self.basepath = basepath

        # Data to be loaded in
        self.games = None
        self.players = None
        self.plays = None
        self.weeks = {}

    def load_data(self, data_folder='data', weeks=None):
        self.games = pd.read_csv(os.path.join(self.basepath,data_folder,'games.csv'))
        self.players = pd.read_csv(os.path.join(self.basepath,data_folder,'players.csv')).set_index('nflId')
        self.plays = pd.read_csv(os.path.join(self.basepath,data_folder,'plays.csv'))

        self.load_weeks(weeks=weeks, data_folder=data_folder)

    def load_weeks(self, weeks='All', data_folder='data'):
        if weeks is None:
            return

        if isinstance(weeks, int):
            for i in range(weeks):
                name = f'week{i+1}'
                self.weeks[name] = pd.read_csv(os.path.join(self.basepath,data_folder,name+'-processed.csv'))
        elif isinstance(weeks, list):
            for i in weeks:
                name = f'week{i}'
                self.weeks[name] = pd.read_csv(os.path.join(self.basepath,data_folder,name+'-processed.csv'))
        elif weeks == 'All':
            for i in range(17):
                name = f'week{i+1}'
                self.weeks[name] = pd.read_csv(os.path.join(self.basepath,data_folder,name+'-processed.csv'))

    def process_games(self):
        games = self.games
        plays = self.plays
        team_names = games['homeTeamAbbr'].unique()

        teams = {}
        for name in team_names:
            teams[name] = Team(abbr=name)

        for i in range(games.shape[0]):
            _game_info = games.loc[i]
            gameId = _game_info['gameId']
            homeTeamAbbr = _game_info['homeTeamAbbr']
            visitorTeamAbbr = _game_info['visitorTeamAbbr']
            week = _game_info['week']
            
            game_plays = plays[plays['gameId'] == gameId]
            home_game_plays = game_plays[game_plays['possessionTeam']==homeTeamAbbr].sort_values(by=['playId']).reset_index(drop=True)
            away_game_plays = game_plays[game_plays['possessionTeam']==visitorTeamAbbr].sort_values(by=['playId']).reset_index(drop=True)
            
            teams[homeTeamAbbr].games[f'week{week}'] = Game(gameId,opponent=visitorTeamAbbr,game_info=_game_info,
                                                            play_data=away_game_plays,location='home')
            teams[visitorTeamAbbr].games[f'week{week}'] = Game(gameId,opponent=homeTeamAbbr,game_info=_game_info,
                                                            play_data=home_game_plays,location='away')

        self.teams = teams

    def process_teams(self, teams=None):
        if teams is None:
            teams = self.teams.keys()

        for key in teams:
            team = self.teams[key]

            team.process_weeks(self.weeks)
            team.process_game_plays(self.players)
            team.process_game_player_coverages()
            team.aggregate_coverages()

    def return_plays(self, teams=None, weeks=None, defensive_coverage=None, target_coverage=None):
        if teams is None:
            teams = self.teams.values()
            
        if weeks is None:
            weeks = np.arange(1,18)
        
        _plays = []
        for team in teams:
            for week in weeks:
                week_key = f'week{week}'
                if week_key in team.games:
                    game = team.games[week_key]
                    for play in game.plays:
                        
                        if not play.hasForwardPass:
                            continue
                            
                        try:
                            if play.target is None:
                                continue
                        except:
                            print(play)
                            continue
                                
                        if defensive_coverage is None and target_coverage is None:
                            _plays.append(play)
                            continue
                            
                        if defensive_coverage is not None:
                            if play.defensive_coverage_shell == defensive_coverage:
                                _plays.append(play)
                                continue
                                
                        if target_coverage is not None:    
                            if len(play.target_coverage) == 1 and play.target_coverage[0] == target_coverage:
                                _plays.append(play)
                                continue
                    
        return _plays

    def calculate_offensive_production(self, useId=False):
        metric_keys = ['snaps','targets','epa','games played']
        offensive_production = {}
        for team in self.teams.values():
            print(team.abbr)
            opponent_production = team.calculate_opponent_offensive_production(useId=useId)

            for key in opponent_production.keys():
                if key not in offensive_production:
                    offensive_production[key] = opponent_production[key]
                else:
                    for subkey in metric_keys:
                        offensive_production[key][subkey] += opponent_production[key][subkey]

        df = pd.DataFrame.from_dict(offensive_production,orient='index')    
        return df
        
        

        
