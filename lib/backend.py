from PyQt5 import QtGui, QtWidgets, QtCore
import sys

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

    def on_mainClock(self):
        print('running')

    def stop_mainClock(self):
        pass

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