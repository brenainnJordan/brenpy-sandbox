'''
Created on 14 Mar 2018

@author: Bren
'''

from __future__ import division, unicode_literals, print_function  # for compatibility with Python 2 and 3

import matplotlib as mpl
import matplotlib.pyplot as plt

# change the following to %matplotlib notebook for interactive plotting
# %matplotlib inline

# Optionally, tweak styles.
mpl.rc('figure',  figsize=(10, 6))
mpl.rc('image', cmap='gray')

import os

import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience

import pims
import trackpy as tp

import skimage

TRACKPY_EXAMPLES = r'E:\dev\python\clones\trackpy-examples'

frames_path = os.path.join(TRACKPY_EXAMPLES, r'sample_data\bulk_water\*.png')
print(frames_path)
frames = pims.ImageSequence(frames_path, as_grey=True)

print(frames)
