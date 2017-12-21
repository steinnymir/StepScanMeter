from PyQt5 import QtGui, QtWidgets, QtCore
import numpy as np
import sys

class Instrument(QtCore.QObject):
    """ Instrument object to interface to a physical lab instrument.

    """

    def __init__(self,name):
        super(Instrument, self).__init__()

        self.clock = QtCore.QTimer
        self.clock.start(100)
        self.clock.connect(self.on_clock)
        self.name = name
        # self.type = type
        self.status = None # status: None - not initialized, True - Active, False - deactivated

        self.data = {}

        self.data_changed = QtCore.pyqtSignal([dict])
        self.data_changed.emit()

    @QtCore.pyqtSlot()
    def on_clock(self):
        self.data['X'] = np.random.rand(1)
        self.data['Y'] = np.random.rand(1)
        self.connect_and_emit_data()

    def connect_and_emit_data(self):
        self.data_changed.emit(self.data)


    def initialize(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def write(self,what,where):
        raise NotImplementedError




class Backend(QtCore.QObject):

    def __init__(self):
        super(Backend, self).__init__()

        self.data = {}
        self.instruments = {}


        self.mainClock = QtCore.QTimer()
        self.mainClock.timeout.connect(self.on_mainClock)



        # self.start_mainClock(500)

    def start_mainClock(self, clockTime):
        if self.mainClock.isActive:
            self.mainClock.stop()
        self.mainClock.start(clockTime)

    def stop_mainClock(self):
        pass

    def add_instrument(self, name, type):
        self.instruments[name] = Instrument(name)
        self.instrument.initialize()


if __name__ == '__main__':


    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    # Create handle prg for the Graphic Interface
    prg = Backend()
    prg.start_mainClock(500)

    try:
        app.exec_()
    except:
        print('app.exec_() failed: exiting')