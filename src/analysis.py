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

def aggregate_coverages(coverages=[]):
    combined_coverages = {}
    for coverage in coverages:
        for key in coverage.keys():
            if key not in combined_coverages:
                combined_coverages[key] = coverage[key]
            else:
                for subkey in coverage[key].keys():
                    combined_coverages[key][subkey] += coverage[key][subkey]
    
    return combined_coverages
