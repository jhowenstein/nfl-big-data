import numpy as np
import pandas as pd
import scipy as sp

import os
import glob

from .team import Team
from .game import Game

def load_data(basepath):
    pass
    #return games, players, plays

def load_weeks(weeks):
    pass
    #return weeks

def select_team(teams, abbr):
    return

def process_games(games, plays):
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

    return teams

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

    def load_weeks(self, weeks, data_folder='data'):
        if weeks is None:
            return

        if isinstance(weeks, int):
            for i in range(weeks):
                name = f'week{i+1}'
                self.weeks[name] = pd.read_csv(os.path.join(self.basepath,data_folder,name+'-processed.csv'))
        elif isinstance(weeks, list):
            for i in weeks:
                name = f'week{i+1}'
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
        
        

        
