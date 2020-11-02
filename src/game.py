import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

class Game:
    def __init__(self, gameId, opponent, game_info, play_data, location):
        self.gameId = gameId
        self.opponent = opponent
        self.location = location
        self.game_info = game_info

        self.play_data = play_data

        self.plays = []

    @property
    def nPlays(self):
        return len(self.plays)

    @property
    def info(self):
        return str(self)

    def __str__(self):
        week = self.game_info['week']
        home_team = self.game_info['homeTeamAbbr']
        away_team = self.game_info['visitorTeamAbbr']
        opponent = self.opponent
        date = self.game_info['gameDate'].replace('/','-')

        if opponent == home_team:
            return f'Week {week} - {away_team} at {home_team} ({date})'
        elif opponent == away_team:
            return f'Week {week} - {home_team} vs {away_team} ({date})'

    def list_plays(self):
        for i in range(len(self.plays)):
            print(f'Play {i+1}: {self.plays[i]}')