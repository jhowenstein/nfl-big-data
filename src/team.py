import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

from .play import Play

class Team:
    def __init__(self, abbr):
        self.abbr = abbr

        self.games = {}

    def __str__(self):
        return self.abbr

    def process_weeks(self, weeks):
        for key in weeks.keys():
            print(f'{self.abbr} - {key}')
            try:
                game = self.games[key]
            except:
                continue
            
            week_data = weeks[key]
            
            for i in game.play_data.index:
                play = game.play_data.loc[i]
                tracking_data = week_data[(week_data['gameId']==play['gameId'])&(week_data['playId']==play['playId'])]
                player_tracking = tracking_data[tracking_data['nflId'].notna()]
                fb_tracking = tracking_data[tracking_data['displayName']=='Football'].sort_values(by='frameId').reset_index(drop=True)
                
                game.plays.append(Play(play['playId'],play_data=play,player_tracking=player_tracking,
                                    fb_tracking=fb_tracking,defensive_team=game.location))

    def process_game_plays(self, players):
        for game in self.games.values():
            game.process_plays(players)

    def process_game_player_coverages(self, positions=['CB','LB','S'], useId=True):
        game_coverages = {}

        for key, game in self.games.items():
            _coverage = game.classify_defensive_back_coverages(positions=positions,useId=useId)
            game_coverages[key] = _coverage

        self.game_coverages = game_coverages

    def process_game_coverage_shells(self):
        pass

    def aggregate_coverages(self, game_count=True):
        combined_coverages = {}
        for game_coverage in self.game_coverages.values():
            for key in game_coverage.keys():
                if key not in combined_coverages:
                    combined_coverages[key] = game_coverage[key]
                    combined_coverages[key]['games played'] = 1
                else:
                    for subkey in game_coverage[key].keys():
                        combined_coverages[key][subkey] += game_coverage[key][subkey]
                    combined_coverages[key]['games played'] += 1
        
        self.aggregated_coverages = combined_coverages

    def calculate_opponent_offensive_production(self, useId=False):
        metric_keys = ['snaps','targets','epa']
        offensive_production = {}
        for game in self.games.values():
            game_production = game.calculate_offensive_production(useId=useId)

            for key in game_production.keys():
                if key not in offensive_production:
                    offensive_production[key] = game_production[key]
                    offensive_production[key]['games played'] = 1
                    offensive_production[key]['team'] = game.opponent
                else:
                    for subkey in metric_keys:
                        offensive_production[key][subkey] += game_production[key][subkey]
                    offensive_production[key]['games played'] += 1

        return offensive_production  

    