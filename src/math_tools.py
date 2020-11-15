import numpy as np
import pandas as pd
import scipy as sp


def orientation_array(theta):
    _theta = np.radians(theta)
    return np.array([np.sin(_theta),np.cos(_theta)])