import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt

import os
import glob

from .player import Player

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
        self.process_tracking()
        

    def __str__(self):
        return self.play_data['playDescription']

    @property
    def nFrames(self):
        return self.fb_tracking.shape[0]

    @property
    def line_of_scrimmage(self):
        return self.fb_tracking.loc[0]['x']

    @property
    def outcome_event(self):
        for event in self.events:
            if 'outcome' in event:
                return event
        return None    # If no outcome event is found

    @property
    def hasForwardPass(self):
        if 'pass_forward' in self.events:
            return True
        else:
            return False

    def process_events(self):
        play_events = self.fb_tracking['event'].values

        for k, event in enumerate(play_events):
            if event != 'None':
                self.events[event] = k + 1

    def process_tracking(self):
        self.player_tracking['distance from line'] = self.player_tracking['x'] - self.line_of_scrimmage
        self.player_tracking['distance to sideline'] = [min((160/3) - y,y) for y in self.player_tracking['y'].values]
        self.player_tracking['distance from center'] = self.player_tracking['y'] - (80/3)

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

    def find_dropback_events(self):
        for key, value in self.players['offense'].items():
            if value.position == 'QB':
                qb_key = key

        dt = .1

        x = self.players['offense'][qb_key].tracking_data['x'].values
        y = self.players['offense'][qb_key].tracking_data['y'].values

        dx = np.zeros(len(x))
        dy = np.zeros(len(y))

        ddx = np.zeros(len(x))
        ddy = np.zeros(len(y))

        for i in range(1,len(x)-1):
            dx[i] = (x[i+1] - x[i-1]) / (2 * dt)
            dy[i] = (y[i+1] - y[i-1]) / (2 * dt)
            
        for i in range(2,len(x)-2):
            ddx[i] = (dx[i+1] - dx[i-1]) / (2 * dt)
            ddy[i] = (dy[i+1] - dy[i-1]) / (2 * dt)
            
        filt_dx = np.zeros(len(x))
        filt_dy = np.zeros(len(y))

        filt_ddx = np.zeros(len(x))
        filt_ddy = np.zeros(len(y))
            
        order = 3

        w = order // 2
        for i in range(w,len(x)-2):
            filt_dx[i] = sum(dx[i-w:i+w+1]) / order
            filt_dy[i] = sum(dy[i-w:i+w+1]) / order
            
        for i in range(w,len(x)-2):
            filt_ddx[i] = sum(ddx[i-w:i+w+1]) / order
            filt_ddy[i] = sum(ddy[i-w:i+w+1]) / order

        # Peak Dropback Event
        start = self.events['ball_snap'] - 1
        end = self.events['pass_forward']

        peak_dropback = np.argmin(filt_dx[start:end]) + start

        start = peak_dropback

        end_dropback = np.argmax(filt_ddx[start:end]) + start

        self.events['peak_dropback'] = peak_dropback + 1
        self.events['end_dropback'] = end_dropback + 1

    def return_players_by_position(self, position):
        result = []
        for side in ('offense','defense'):
            for player in self.players[side].values():
                if player.position == position:
                    result.append(player)
        return result

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

    def set_player_marker(self, player, markers, scale):
        if markers == 'number':
            marker = f'${player.number}$'
            s = 150 * scale
        elif markers == 'position':
            marker = f'${player.position}$'
            s = 150 * scale
        else:
            marker = 'o'
            s = 50 * scale

        return marker, s

    def plot_play(self, scale=1, markers=None):
        fig,ax = self.build_field(scale=scale)

        ax.axvline(self.line_of_scrimmage,color='y',alpha=.5,zorder=3)
        
        for player in self.players['offense'].values():
            marker, s = self.set_player_marker(player, markers, scale)

            init_pos = player.tracking_data.loc[0]
            ax.scatter(init_pos['x'],init_pos['y'],color='r',marker=marker,zorder=3,s=s)
            
            x = player.tracking_data['x'].values
            y = player.tracking_data['y'].values
            ax.plot(x,y,color='r',alpha=.3,linestyle='--',zorder=3)

        for player in self.players['defense'].values():
            marker, s = self.set_player_marker(player, markers, scale)

            init_pos = player.tracking_data.loc[0]
            ax.scatter(init_pos['x'],init_pos['y'],color='b',marker=marker,zorder=3,s=s)
            
            x = player.tracking_data['x'].values
            y = player.tracking_data['y'].values
            ax.plot(x,y,color='b',alpha=.3,linestyle='--',zorder=3)

        try:
            start = self.events['pass_forward'] - 1
        except:
            start = 0
        try:
            end = self.events['pass_arrived']
        except:
            end = -1

        ax.plot(self.fb_tracking['x'].values[start:end],
                self.fb_tracking['y'].values[start:end],
                color='brown',alpha=.7,zorder=3)

        plt.show()

    def create_gif(self,scale=1,markers=None,show=False,output=True,target_directory='play-viz',fps=5,name='play'):
        import moviepy.editor as mpy

        image_folder = os.path.join(target_directory,'images')
        self.plot_play_frames(scale=scale,markers=markers,show=show,output=output,target_directory=image_folder)
        file_list = []
        for i in range(self.nFrames):
            file_list.append(os.path.join(image_folder,f'Play Frame - {i+1}.png'))
        clip = mpy.ImageSequenceClip(file_list, fps=fps)
        dst = os.path.join(target_directory,f'{name}.gif')
        clip.write_gif(dst, fps=fps)

    def create_video(self,scale=1,markers=None,show=False,output=True,target_directory='play-viz',fps=10,name='play'):
        import moviepy.editor as mpy

        image_folder = os.path.join(target_directory,'images')
        self.plot_play_frames(scale=scale,markers=markers,show=show,output=output,target_directory=image_folder)
        file_list = []
        for i in range(self.nFrames):
            file_list.append(os.path.join(image_folder,f'Play Frame - {i+1}.png'))
        clip = mpy.ImageSequenceClip(file_list, fps=fps)
        dst = os.path.join(target_directory,f'{name}.mp4')
        clip.write_videofile(dst,fps=fps)

    def plot_play_frames(self, scale=1, markers=None, show=False, output=True, target_directory=''):
        for i in range(self.nFrames):
            self.plot_play_frame(index=i,scale=scale,markers=markers,show=show,output=output,target_directory=target_directory)

    def plot_play_frame(self, index, scale=1, markers=None, show=True, output=False, target_directory=''):
        if isinstance(index,str):
            index = self.events[index] - 1

        fig,ax = self.build_field(scale=scale)

        ax.axvline(self.line_of_scrimmage,color='y',alpha=.5,zorder=3)

        for player in self.players['offense'].values():
            marker, s = self.set_player_marker(player, markers, scale)

            pos = player.tracking_data.loc[index]
            ax.scatter(pos['x'],pos['y'],color='r',marker=marker,zorder=3,s=s)
            
        for player in self.players['defense'].values():
            marker, s = self.set_player_marker(player, markers, scale)

            pos = player.tracking_data.loc[index]
            ax.scatter(pos['x'],pos['y'],color='b',marker=marker,zorder=3,s=s)

        ax.scatter(self.fb_tracking['x'].values[index],
                   self.fb_tracking['y'].values[index],
                   color='brown',marker='d',zorder=3)

        title = f'Play Frame - {index+1}'
        ax.set_title(title,fontsize=18)

        play_events = self.fb_tracking['event'].values
        _event = play_events[index]
        if play_events[index] != 'None':
            ax.set_xlabel(f'Event: {_event.replace("_"," ").title()}',fontsize=16)

        if output:
            if target_directory != '' and not os.path.exists(target_directory):
                os.makedirs(target_directory)
            dst = os.path.join(target_directory,title + '.png')
            plt.savefig(dst)
        elif show:
            plt.show()

        plt.close(fig)