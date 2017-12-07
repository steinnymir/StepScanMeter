# -*- coding: utf-8 -*-
"""
Created on Nov 22 09:57:29 2017

@author: S.Y. Agustsson
"""

import numpy as np
import pandas as pd
import datetime
import os
import h5py

def main():

    pass


class Scan(object):
    """ Creates an object that contains data and metadata of a single time resolved scan.
    This is used to store all data and metadata while performing a pump-probe measurement.

    """

    def __init__(self):

        # data
        self.timeScale = []
        self.stagePositions = []
        self.data = {'avg':pd.DataFrame()}

        #scan settings
        self.dwellTime = 0.01

        self.saveDirectory = 'E:/data'
        self.dateTime = str(datetime.datetime.now()).split('.')[0].split(' ')

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
        # TODO: chanhge to different variables containing dictionaries, then write dict to par translator
        self.parameters = [
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

    def build_stage_position(self):
        for i in self.timeScale:
            self.stagePoisitions[i] = self.timeScale[i] * 299.792458

    def get_save_directory(self,dataType):
        saveDir = '{baseDir}/{material}/{dataType}/{date}/'.format(baseDir=self.saveDirectory,
                                                        material='RuCl3',
                                                        date=self.dateTime[0],
                                                        dataType=dataType,
                                                        )
        if not os.path.isdir(saveDir):
            os.makedirs(saveDir)
        return saveDir

    def save_to_HDF5(self):
        """ Saves data contained in scan to an HDF5 dataframe."""
        saveDir = self.get_save_directory('HDF5')
        print('Saving scan as .HDF5 under {}'.format(saveDir))
        saveName = saveDir + 'test'

        f = h5py.File(saveName,'w')
        dataGroup = f.create_group('data')
        metadataGroup = f.create_group('metadata')

        for key, value in self.data.items():
            dset = dataGroup.create_dataset(str(key),data=value)


    def save_to_csv(self):
        """ Saves data contained in scan to a .csv file."""

        saveDir = self.get_save_directory('CSV')
        print('Saving scan as .CSV under {}'.format(saveDir))
        saveName = saveDir + 'test/'
        for key, value in self.data.items():
            try:
                f = open('{0}{1}.csv'.format(saveName,key),'w')
            except FileNotFoundError:
                os.makedirs(saveName)
                f = open('{0}{1}.csv'.format(saveName,key),'w')

            value.to_csv(f,mode='w')
            f.close()





if __name__ == "__main__":
    main()
