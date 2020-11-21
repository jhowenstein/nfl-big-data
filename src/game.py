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

    @property
    def numberForwardPassPlays(self):
        count = 0
        for play in self.plays:
            if play.hasForwardPass:
                count += 1

        return count

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

    def defense_coverage_shells(self):
        defensive_shells = {}
        defensive_shells['cover 1'] = 0
        defensive_shells['cover 2'] = 0
        defensive_shells['cover 3'] = 0
        defensive_shells['cover 4'] = 0
        defensive_shells['cover 6'] = 0

        for play in self.plays:
            if play.hasForwardPass:
                coverage_shell = play.defensive_coverage_shell
                defensive_shells[coverage_shell] += 1

        return defensive_shells