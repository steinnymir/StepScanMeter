# -*- coding: utf-8 -*-
"""
Created on Nov 22 09:57:29 2017

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
    scanning = QtCore.pyqtSignal(bool)
    status = QtCore.pyqtSignal(str)

    def __init__(self):
        super(StepScan, self).__init__()

        # data
        self.timeScale = []
        self.stagePositions = []
        self.data = {'avg':pd.DataFrame()}


        self.instruments = None
        #scan settings
        self.settings_delayStage = {
            'zero': 0.0,
            'afterMovedDelay': 0.01
                                }
        self.settings_lockIn = {
                                'dwellTime': 0.01,
                                'measureParameters': ['X', 'Y'],
                                }
        # self.dwellTime = 0.01
        # self.lockinParameters = ['X', 'Y', 'Aux in 1']
        for parameter in self.settings_lockIn['measureParameters']:
            self.data[parameter] = []

        self.saveDirectory = 'E:/data'
        self.dateTime = str(datetime.datetime.now()).split('.')[0].split(' ')


        # metadata parmeters

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

    def build_stage_positions(self):
        """ Convert picosecond time scale to mm steps for the stage"""
        for i in self.timeScale:
            self.stagePoisitions[i] = self.timeScale[i] * 299.792458 *2

    def get_save_directory(self,dataType):
        """ returns the standard directory where to save data."""
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

    def measure_scan(self):
        """ starts a scan measurement."""
        print('worker scanning')
        for i in range(len(self.stagePositions)):
            self.status.emit('moving stage')
            self.move_stage_to(self.stagePositions[i])
            time.sleep(self.settings_delayStage['afterMovedDelay'])
            self.status.emit('dwelling')
            time.sleep(self.settings_lockIn['dwellTime'])  # wait after acquiring data
            newdataDict = self.read_lockin()

            self.newData.emit(i, newdataDict)
            self.status.emit('storing data')

            for parameter, value in newdataDict.items():
                self.data[parameter].append(value)

        self.finished.emit(self.data)


    def move_stage_to(self,pos):
        try:
            self.instruments['stage'].MoveTo(pos)
        except Exception as error:
            self.rise_error('moving stage', error)

    def read_lockin(self):
        """ read values declared in lockinParameters from the lock-in and outputs them in dict format."""
        self.status.emit('reading LockIn')
        try:
            snapVals = self.instruments['lockin'].readSnap()
        except Exception as exception:
            if testMode:
                snapVals = {}
                for i in range(len(self.lockinParameters)):
                    snapVals[self.lockinParameters[i]] = np.random.rand(1)[0]
            else:
                self.rise_error('reading Lock-in', exception)
        return snapVals

    @QtCore.pyqtSlot(str,str)
    def rise_error(self, doingWhat, errorHandle, type='Warning', popup=True):
        """ opens a dialog window showing the error"""
        errorMessage = 'Thread Error while {0}:\n{1}'.format(doingWhat,errorHandle)
        print(errorMessage)
        if popup:
            errorDialog = QtWidgets.QMessageBox()
            errorDialog.setText(errorMessage)
            if type == 'Warning':
                errorDialog.setIcon(QtWidgets.QMessageBox.Warning)
            elif type == 'Critical':
                errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
            errorDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorDialog.exec_()



if __name__ == "__main__":
    main()
