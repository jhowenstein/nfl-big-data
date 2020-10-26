import numpy as np
import pandas as pd
import scipy as sp

import os
import glob

class Team:
    def __init__(self, abbr):
        self.abbr = abbr

        self.games = {}

class Game:
    def __init__(self, gameId, opponent, game_info, play_data, location):
        self.gameId = gameId
        self.opponent = opponent
        self.location = location
        self.game_info = game_info

        self.play_data = play_data

        self.plays = []

    def __str__(self):
        week = self.game_info['week']
        home_team = self.game_info['homeTeamAbbr']
        away_team = self.game_info['visitorTeamAbbr']
        date = self.game_info['gameDate']

        return f'Week {week}: {away_team} at {home_team} ({date})'

class Play:
    def __init__(self, playId, play_data, player_tracking, fb_tracking, defensive_team):
        self.playId = playId
        self.play_data = play_data
        self.fb_tracking = fb_tracking
        self.player_tracking = player_tracking
        self.defensive_team = defensive_team

        self.players = {}

    def __str__(self):
        return self.play_data['playDescription']

class Player:
    def __init__(self, nflId, player_data,tracking_data):
        self.nflId = nflId
        self.player_data = player_data
        self.tracking_data = tracking_data
