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

    def process_plays(self, players):
        for play in self.plays:
            play.process_players(players)
            if play.hasForwardPass:
                play.find_dropback_events()
                play.process_coverage()

    def classify_defensive_coverage_shells(self):
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

    def classify_defensive_back_coverages(self, percentage=False, positions=['CB','LB','S']):
        coverage_counts = {}
        coverage_names = ('zone','zone-deep','zone-over','man','man-over','blitz')
        
        for play in self.plays:
            
            dbacks = []
            if 'CB' in positions:
                dbacks += play.return_players_by_position('CB')
            if 'LB' in positions:
                dbacks += play.return_linebackers()
            if 'S' in positions:
                dbacks += play.return_safeties()
            
            for dback in dbacks:
                #print(f'Defensive Player Name: {dback.name}')
                if dback.name is None:
                    continue

                if not dback.name in coverage_counts:
                    coverage_options = {}
                    coverage_options['snaps'] = 0
                    for coverage_name in coverage_names:
                        coverage_options[coverage_name] = 0

                    coverage_counts[dback.name] = coverage_options

                _coverage = dback.coverage

                if _coverage is None:    # No coverage currently calculated on sacks
                    continue

                if _coverage == 'zone':
                    if dback.safety_help is None:
                        _coverage += '-deep'
                    elif dback.safety_help == True:
                        _coverage += '-over'
                    
                if _coverage == 'man':
                    if dback.safety_help == 'True':
                        _coverage += '-over'

                coverage_counts[dback.name][_coverage] += 1
                coverage_counts[dback.name]['snaps'] += 1

        if percentage:
            for counts in coverage_counts.values():
                N = counts['snaps']
                for coverage_name in coverage_names:
                    counts[coverage_name] = round(counts[coverage_name] / N,2)

        return coverage_counts


        