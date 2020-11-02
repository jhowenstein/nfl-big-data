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
            game = self.games[key]
            
            week_data = weeks[key]
            
            for i in game.play_data.index:
                play = game.play_data.loc[i]
                tracking_data = week_data[(week_data['gameId']==play['gameId'])&(week_data['playId']==play['playId'])]
                player_tracking = tracking_data[tracking_data['nflId'].notna()]
                fb_tracking = tracking_data[tracking_data['displayName']=='Football'].sort_values(by='frameId').reset_index(drop=True)
                
                game.plays.append(Play(play['playId'],play_data=play,player_tracking=player_tracking,
                                    fb_tracking=fb_tracking,defensive_team=game.location))