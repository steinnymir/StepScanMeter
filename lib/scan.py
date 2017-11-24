# -*- coding: utf-8 -*-
"""
Created on Nov 22 09:57:29 2017

@author: S.Y. Agustsson
"""

# from lib import genericfunctions as gfs
import numpy as np
import pandas as pd


def main():

    pass


class Scan(object):
    """ Creates an object(OBJ) that contains data and metadata of a single time resolved scan.
    This is used to store all data and metadata while performing a pump-probe measurement.


    Data is contained in:
    - raw_time: raw measured time scale
    - raw_trace: measured data points
    - time: time trace modified by analysis functions applied on this object
    - trace: data modified by analysis functions applied on this object.

    Metadata entries are described in __init__


    """

    def __init__(self):
        """
        """
        self.timeScale = [],
        self.stagePositions = []
        self.data = {},
        self.dwellTime = 200

        self.currentScan = None
        self.reset_currentScan()


        self.metadata = {
            'date': None,
            'notes': None,
            'sample':{ # information about sample under examination
                'name': None,
                'material': None,
                'notes' : None,
            },
            'pump':{ # parameters of pump beam
                'power': None,
                'spotDiameter': None,
                'energyDensity': None,
                'frequency': None,
                'polarization': None,
            },
            'probe': { # parameters of probe beam
                'power': None,
                'spotDiameter': None,
                'energyDensity': None,
                'frequency': None,
                'polarization': None,
            },
            'destructionPulse': { # parameters of destruction beam
                'power': None,
                'spotDiameter': None,
                'energyDensity': None,
                'frequency': None,
                'polarization': None,
                'delay': None,
            },
            'temperature': None,
            'Notes': None,
        }

        self.parameters = [ # TODO: chanhge to different variables containing dictionaries, then write dict to par translator
            {'name': 'General', 'type': 'group', 'children': [
                {'name': 'Date', 'type': 'str', 'value': 'today'},
                {'name': 'Notes', 'type': 'str', 'value': ''},
            ]},
            {'name': 'Pump beam', 'type': 'group', 'children': [
                {'name': 'Power', 'type': 'float', 'value': 1.2e-6, 'step': 1e-3, 'siPrefix': True,
                 'suffix': 'W'},
                {'name': 'Spot Diameter', 'type': 'float', 'value': 1.2e-6, 'step': 1e-6, 'siPrefix': True,
                 'suffix': 'm'},
                {'name': 'Wavelenght', 'type': 'float', 'value': 1.2e-6, 'step': 1e-9, 'siPrefix': True,
                 'suffix': 'm'},
                {'name': 'Polarization', 'type': 'float', 'value': 1.2e-6, 'step': 1e-3, 'siPrefix': True,
                 'suffix': 'deg'},
            ]},
            {'name': 'Probe beam', 'type': 'group', 'children': [
                {'name': 'Power', 'type': 'float', 'value': 1.2e-6, 'step': 1e-3, 'siPrefix': True,
                 'suffix': 'W'},
                {'name': 'Spot Diameter', 'type': 'float', 'value': 1.2e-6, 'step': 1e-6, 'siPrefix': True,
                 'suffix': 'm'},
                {'name': 'Wavelenght', 'type': 'float', 'value': 1.2e-6, 'step': 1e-9, 'siPrefix': True,
                 'suffix': 'm'},
                {'name': 'Polarization', 'type': 'float', 'value': 1.2e-6, 'step': 1e-3, 'siPrefix': True,
                 'suffix': 'deg'},
            ]},
            {'name': 'Sample', 'type': 'group', 'children': [
                {'name': 'Material', 'type': 'str', 'value': 'RuCl3'},
                {'name': 'Sample ID', 'type': 'str', 'value': '-'},
                {'name': 'Orientation', 'type': 'str', 'value': '-'},
                {'name': 'Other info', 'type': 'str', 'value': 'sample looks good'},
            ]}
        ]

    def init_scan(self):
        self.currentScan['stagePosition']

    def build_stage_position(self):
        for i in self.timeScale:
            self.stagePoisitions[i] = self.timeScale[i] * 299.792458

    def store_scan(self, name):

        self.data[name] = self.currentScan


    def reset_currentScan(self):
        self.currentScan = {
                'time': [],
                'currentStagePosition': None,
                'X':[],
                'Y': [],
                'Theta': None,
                'r': None,
                'aux1': None,
                'aux2': None,
                'temperature': None
            }


    def save_scan(self, filename):
        pass




if __name__ == "__main__":
    main()
