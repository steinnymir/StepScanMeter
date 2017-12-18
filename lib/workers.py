# -*- coding: utf-8 -*-
"""
Created on Nov 22 09:57:29 2017

@author: S.Y. Agustsson
"""
from PyQt5 import QtGui, QtWidgets, QtCore
import time
from lib.gfs import raise_Qerror

def main():

    # w = Worker()
    # w.work()
    pass


class Worker(QtCore.QObject):
    """Parent class for all workers"""

    finished = QtCore.pyqtSignal(dict)
    newData = QtCore.pyqtSignal(dict)
    status = QtCore.pyqtSignal(str)


    def __init__(self, workerSettings, instruments):
        super(Worker, self).__init__()
        self.settings = workerSettings
        self.instruments = instruments


        self.result = {'data':[]}
        self.result = {**self.result, **self.settings}

        # Flags
        self.shouldStop = False  # soft stop, for interrupting at end of cycle.
        self.statusFlag = 'none'

        self.requiredInstruments = []  # fill list with names of instruments required for (sub)class
        self.requiredSettings = []  # fill list with names of settings required for (sub)class


    def check_requirements(self):
        """ method that should check wheather all the required instruments are connected and available."""
        availableInstruments = []
        availableSettings = []
        for key,val in self.instruments.items():  # create list of available instruments
            availableInstruments.append(key)
        for key,val in self.instruments.items():  # create list of available settings
            availableSettings.append(key)
        for instrument in self.requiredInstruments:  # rise error for each missing instrument
            if instrument not in availableInstruments:
                raise NotImplementedError('Instrument {} not available.'.format(instrument))
        for setting in self.requiredSettings:  # rise error for each missing Setting
            if setting not in availableSettings:
                raise NotImplementedError('Setting {} not available.'.format(instrument))


    def work(self):
        """ method where to write procedure specific for this worker"""
        raise NotImplementedError("Method 'work' not implemented in worker (sub)class")

    def kill_worker(self):
        """ method to safely kill the thread by closing all insturments."""
        for instrument in self.requiredInstruments:
            try:
                getattr(self,instrument).close()
                print('closed connection to {}'.format(instrument))
            except AttributeError:
                pass
            except Exception as e:
                raise_Qerror('killing {}'.format(instrument), e, popup=False)

    def set_status(self,statusString):
        self.statusFlag = statusString
        self.status.emit(statusString)

    def get_status(self):
        self.status.emit(self.statusFlag)
        return self.stautsFlag

    @QtCore.pyqtSlot(bool)
    def hard_stop(self):
        """ Hard stop, for interrupting mid cycle."""
        raise NotImplementedError("Method 'hard_stop' not implemented in worker (sub)class")

    @QtCore.pyqtSlot(bool)
    def should_stop(self,flag):
        """ Soft stop, for interrupting at the end of the current cycle."""
        self.shouldStop = flag

class StepScanWorker(Worker):
    """ Subclass of Worker, designed to perform step scan measurements.

    """

    def __init__(self, stepScanSettings, instruments):
        super(StepScanWorker, self).__init__(stepScanSettings, instruments)
        self.status = 'loading'
        self.requiredInstruments = ['Lock-in', 'Stage']
        self.requiredSettings = ['stagePositions','lockinParametersToRead','dwelltime','numberOfScans']
        self.check_instruments()
        self.status = 'idle'

        for instrument, value in instruments.items():
            inst_str = str(instrument).lower().replace('-','')
            setattr(self, instrument, value)
        for setting, value in stepScanSettings.items():
            inst_str = str(instrument).lower().replace('-','')
            setattr(self, setting, value)

    def work(self):
        """ Step Scan specific work procedure.

        """
        print('worker scanning')
        self.status = 'scanning'

        for j in self.numberOfScans:
            self.result['data'][j] = {}

            for i in range(len(self.stagePositions)):

                pos = self.stagePositions[i]
                self.stage.moveTo(pos) # move stage to new position
                time.sleep(self.dwelltime)  # wait for the lockin value to saturate

                newDataDict = self.lockin.readSnap(self.lockinParameters)
                newDataDict['stagePosition'] = pos

                for key, val in newDataDict.items(): #append data to local results dataset
                    self.result['data'][j][key] = val

                newDataDict['scanNumber'] = j  # add lable for scan number in order to track it in emitted signal
                self.newData.emit(newDataDict)

                if self.shouldStopSoft:
                    self.kill_worker()

        self.finished.emit(self.result)
        self.status = 'complete'


if __name__ == "__main__":
    main()
