import numpy as np
import pandas as pd
import scipy as sp

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import os
import glob

from .math_tools import orientation_array

class Player:

    movement_to_zone_threshold = -0.5
    deep_zone_threshold = 10

    def __init__(self, nflId, player_data,tracking_data):
        self.nflId = nflId
        self.player_data = player_data
        self.tracking_data = tracking_data

        self.locks = []
        self.blitz_loc = None
        self.zone_loc = None

        self.safety_help = None    # Changed to true/false after processing

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

    @property
    def last_name(self):
        return self.name.split()[1]

    @property
    def hasLock(self):
        return len(self.locks) > 0

    @property
    def x(self):
        return self.tracking_data['x'].values

    @property
    def y(self):
        return self.tracking_data['y'].values

    @property
    def dx(self):
        x = self.tracking_data['x'].values
        N = len(x)
        dx = np.zeros(N)
        for i in range(1,N-1):
            dx[i] = (x[i+1] - x[i-1]) / 2
        return dx

    @property
    def dy(self):
        y = self.tracking_data['y'].values
        N = len(y)
        dy = np.zeros(N)
        for i in range(1,N-1):
            dy[i] = (y[i+1] - y[i-1]) / 2
        return dy

    @property
    def s(self):
        return self.tracking_data['s'].values

    @property
    def a(self):
        return self.tracking_data['a'].values

    @property
    def dir(self):
        return self.tracking_data['dir'].values

    @property
    def blitzing(self):
        if self.blitz_loc is not None:
            return True
        else:
            return False

    @property
    def man_coverage(self):
        return self.hasLock

    @property
    def zone_coverage(self):
        if self.zone_loc is not None:
            return True
        else:
            return False

    @property
    def coverage(self):
        _coverage = None

        if self.man_coverage:
            if _coverage is None:
                _coverage = 'man'
            else:
                print(f'Error! {self} has has more than one coverage type!')
        if self.zone_coverage:
            if _coverage is None:
                _coverage = 'zone'
            else:
                print(f'Error! {self} has has more than one coverage type!')
        if self.blitzing:
            if _coverage is None:
                _coverage = 'blitz'
            else:
                print(f'Error! {self} has has more than one coverage type!')
        return _coverage

    @property
    def zone_radius(self):
        if self.position in ('FS','SS','S'):
            radius = 7
        elif self.position == 'CB':
            radius = 5
        elif self.position in ('LB','MLB','ILB','OLB'):
            radius = 3
        return radius

    """
    def isDeepZone(self):
        if self.zone_loc is None:
            return False
    """

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

    def movement(self, frame):
        speed = self.tracking_data.loc[frame-1,'s']
        direction = self.tracking_data.loc[frame-1,'dir']
        target = orientation_array(direction) * speed
        return target

    def side(self, frame):
        d = self.distance_from_center(frame)
        if d > 0:
            return 'top'
        else:
            return 'bottom'

    def lock(self, other):
        if other not in self.locks:
            self.locks.append(other)

    def unlock(self, other=None):
        if other is None:
            self.locks = []
        else:
            if other in self.locks:
                self.locks.remove(other)

    def distance_to_player(self, other, frame):
        self_x, self_y = self.location(frame)
        other_x, other_y = other.location(frame)
        dx = self_x - other_x
        dy = self_y - other_y
        r = np.sqrt(dx**2 + dy**2)
        return dx, dy, r

    def distance_to_lock(self, frame):
        if not self.hasLock:
            return None

        other = self.locks[0]
        dx, dy, r = self.distance_to_player(other, frame)
        return dx, dy, r

    def draw_lock(self, ax, frame):
        if not self.hasLock:
            return

        box_buffer = 2
        self_x, self_y = self.location(frame)
        lock_x, lock_y = self.locks[0].location(frame)

        min_x = min(self_x, lock_x)
        min_y =  min(self_y, lock_y)

        bx = min_x - box_buffer
        by = min_y - box_buffer

        w = abs(self_x - lock_x) + box_buffer * 2
        h = abs(self_y - lock_y) + box_buffer * 2

        rect = mpatches.Rectangle((bx,by), width=w, height=h, ec='k',fc='none')
        ax.add_patch(rect)

    def draw_blitz(self, ax):
        if not self.blitzing:
            return

        init_pos = self.location(11)
        dx = self.blitz_loc[0] - init_pos[0]
        dy = self.blitz_loc[1] - init_pos[1]

        ax.arrow(init_pos[0], init_pos[1], dx, dy, head_width = 1.5,  head_length = 1.5, color='orange',alpha=.7, linewidth=2)

    def draw_zone(self, ax):
        if self.zone_loc is None:
            return

        radius=self.zone_radius

        init_pos = self.location(1)  #TODO: Change this to position at ball snap

        ax.plot([init_pos[0],self.zone_loc[0]],[init_pos[1],self.zone_loc[1]],color='yellow',alpha=.7)
        circle = mpatches.Circle(tuple(self.zone_loc), radius, ec='none',fc='yellow',alpha=.5)
        ax.add_patch(circle)

    def draw_coverage(self, ax):
        pass

        

    


