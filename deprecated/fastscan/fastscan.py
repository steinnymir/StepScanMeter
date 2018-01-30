# -*- coding: utf-8 -*-
"""
Created on Jan 09 15:53:29 2018

@author: S.Y. Agustsson
"""
from PyQt5 import QtGui, QtWidgets, QtCore
import numpy as np
import pandas as pd
import datetime
import time
import os
import h5py

def main():

    pass


class StepScan(QtCore.QObject):
    """ Creates an object that contains data and metadata of a single time resolved scan.
    This is used to store all data and metadata while performing a pump-probe measurement.

    """
    # signals:

    finished = QtCore.pyqtSignal(dict)
    newData = QtCore.pyqtSignal(int, dict)
    status = QtCore.pyqtSignal(str)

    def __init__(self):
        super(StepScan, self).__init__()
        pass