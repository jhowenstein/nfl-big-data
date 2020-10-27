import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

class Team:
    def __init__(self, abbr):
        self.abbr = abbr

        self.games = {}

    def __str__(self):
        return self.abbr

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

        self.events = {}
        self.players = {}

        self.process_events()
        

    def __str__(self):
        return self.play_data['playDescription']

    @property
    def line_of_scrimmage(self):
        return self.fb_tracking.loc[0]['x']

    @property
    def outcome_event(self):
        for event in self.events:
            if 'outcome' in event:
                return event
        return None    # If no outcome event is found

    def process_events(self):
        play_events = self.fb_tracking['event'].values

        for k, event in enumerate(play_events):
            if event != 'None':
                self.events[event] = k + 1

    def process_players(self, nfl_player_data):
        offensive_players = {}
        defensive_players = {}

        offensive_player_tracking = self.player_tracking[self.player_tracking['team'] != self.defensive_team]
        defensive_player_tracking = self.player_tracking[self.player_tracking['team'] == self.defensive_team]

        for nflId in offensive_player_tracking['nflId'].unique():
            nflId = int(nflId)
            _player_data = nfl_player_data.loc[nflId]
            _player_tracking = offensive_player_tracking[offensive_player_tracking['nflId']==nflId]
            _player_tracking = _player_tracking.sort_values(by='frameId').reset_index(drop=True)
            offensive_players[nflId] = Player(nflId, player_data=_player_data, tracking_data=_player_tracking)

        for nflId in defensive_player_tracking['nflId'].unique():
            nflId = int(nflId)
            _player_data = nfl_player_data.loc[nflId]
            _player_tracking = defensive_player_tracking[defensive_player_tracking['nflId']==nflId]
            _player_tracking = _player_tracking.sort_values(by='frameId').reset_index(drop=True)
            defensive_players[nflId] = Player(nflId, player_data=_player_data, tracking_data=_player_tracking)

        self.players['offense'] = offensive_players
        self.players['defense'] = defensive_players

    def calc_player_start_position(self, event='ball_snap'):
        pass


    def build_field(self, scale=1):
        sideline_to_hash = 68.75    # In feet
        hash_width = 2    # In feet
        between_hashes = 18.5    # In feet
        field_width = 160    # In feet

        btm_hash_ymin = sideline_to_hash / field_width
        btm_hash_ymax = (sideline_to_hash + hash_width) / field_width
        top_hash_ymin = (sideline_to_hash + hash_width + between_hashes) / field_width
        top_hash_ymax = (sideline_to_hash + hash_width + between_hashes + hash_width) / field_width

        figsize=(12*scale,5.33*scale)
        
        fig,ax = plt.subplots(figsize=figsize)
        
        ax.axvspan(0,10,color='b',alpha=.3,zorder=1)
        ax.axvspan(110,120,color='r',alpha=.3,zorder=1)
        ax.axvspan(10,110,color='g',alpha=.3,zorder=1)
        
        ax.set_xlim(0,120)
        ax.set_ylim(0,53.3)
        
        ax.set_xticks(np.arange(0,121,10))

        for tick in np.arange(11,110):
            # Bottom Hash
            ax.axvline(tick,ymin=btm_hash_ymin,ymax=btm_hash_ymax,color='w',zorder=2)
            # Top Has
            ax.axvline(tick,ymin=top_hash_ymin,ymax=top_hash_ymax,color='w',zorder=2)
        
        return fig, ax

    def plot_play(self, scale=1):
        fig,ax = self.build_field(scale=scale)

        ax.axvline(self.line_of_scrimmage,color='y',alpha=.5,zorder=3)
        
        for player in self.players['offense'].values():
            init_pos = player.tracking_data.loc[0]
            ax.scatter(init_pos['x'],init_pos['y'],color='r',marker='x',zorder=3)
            
            x = player.tracking_data['x'].values
            y = player.tracking_data['y'].values
            ax.plot(x,y,color='r',alpha=.3,linestyle='--',zorder=3)

        for player in self.players['defense'].values():
            init_pos = player.tracking_data.loc[0]
            ax.scatter(init_pos['x'],init_pos['y'],color='b',marker='o',zorder=3)
            
            x = player.tracking_data['x'].values
            y = player.tracking_data['y'].values
            ax.plot(x,y,color='b',alpha=.3,linestyle='--',zorder=3)

        ax.plot(self.fb_tracking['x'].values[self.events['pass_forward']:self.events['pass_arrived']],
                self.fb_tracking['y'].values[self.events['pass_forward']:self.events['pass_arrived']],
                color='brown',alpha=.7,zorder=3)

        plt.show()


class Player:
    def __init__(self, nflId, player_data,tracking_data):
        self.nflId = nflId
        self.player_data = player_data
        self.tracking_data = tracking_data

    @property
    def name(self):
        return self.player_data['displayName']

    @property
    def position(self):
        return self.player_data['position']

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
