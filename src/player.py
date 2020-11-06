import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

class Player:
    def __init__(self, nflId, player_data,tracking_data):
        self.nflId = nflId
        self.player_data = player_data
        self.tracking_data = tracking_data

        #self.cover = []
        self.locks = []
        # coupled, bound, cover

    @property
    def name(self):
        return self.player_data['displayName']

    @property
    def position(self):
        return self.player_data['position']
        #return self.tracking_data.loc[0,'position']

    @property
    def number(self):
        return int(self.tracking_data.loc[0,'jerseyNumber'])

    @property
    def height(self):
        return self.player_data['height']

    @property
    def weight(self):
        return self.player_data['weight']

    @property
    def birthDate(self):
        return self.player_data['birthDate']

    def __str__(self):
        return self.name

    def distance_from_center(self, frame):
        return self.tracking_data.loc[frame-1,'distance from center']

    def distance_from_line(self, frame):
        return self.tracking_data.loc[frame-1,'distance from line']

    def location(self, frame):
        x = self.tracking_data.loc[frame-1,'x']
        y = self.tracking_data.loc[frame-1,'y']
        return np.array([x,y])

