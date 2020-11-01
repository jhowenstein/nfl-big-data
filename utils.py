import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

from nfl import Team, Game

def process_games(games, plays):
    team_names = games['homeTeamAbbr'].unique()

    teams = {}
    for name in team_names:
        teams[name] = Team(abbr=name)

    for i in range(games.shape[0]):
        _game_info = games.loc[i]
        gameId = _game_info['gameId']
        #print(gameId)
        homeTeamAbbr = _game_info['homeTeamAbbr']
        visitorTeamAbbr = _game_info['visitorTeamAbbr']
        week = _game_info['week']
        
        #print(plays.keys())
        game_plays = plays[plays['gameId'] == gameId]
        home_game_plays = game_plays[game_plays['possessionTeam']==homeTeamAbbr].sort_values(by=['playId']).reset_index(drop=True)
        away_game_plays = game_plays[game_plays['possessionTeam']==visitorTeamAbbr].sort_values(by=['playId']).reset_index(drop=True)
        
        teams[homeTeamAbbr].games[f'week{week}'] = Game(gameId,opponent=visitorTeamAbbr,game_info=_game_info,
                                                        play_data=away_game_plays,location='home')
        teams[visitorTeamAbbr].games[f'week{week}'] = Game(gameId,opponent=homeTeamAbbr,game_info=_game_info,
                                                        play_data=home_game_plays,location='away')

    return teams