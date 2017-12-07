import pyqtgraph as PG
import qdarkstyle
from PyQt5 import QtGui, QtWidgets, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from lib import gfs
import numpy as np
from lib import scan
import pandas as pd

testMode = False

import sys
sys.path.append("U:\Dokumente\program\demsarlabprojects\TR-MOKE soft\Soft-for-TR-MOKE-setup")
try:
    import NewPortStagelib
    import USBGPIBlib
except ImportError:
    print('Couldnt import instruments: Test mode activated')
    testMode = True
import time

class StepScanMainWindow(QtWidgets.QMainWindow):
    """ Main application window """

    def __init__(self):
        """Initialize by setting window title, size and graphic options"""
        super().__init__()

        self.title = 'Step Scan Meter'
        self.left = 300
        self.top = 100
        self.width = 1200
        self.height = 700
        self.initUI()

        # set the cool dark theme and other plotting settings
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        PG.setConfigOption('background', 0.1)
        PG.setConfigOption('foreground', 0.7)
        PG.setConfigOptions(antialias=True)


    def initUI(self):
        """Create the layout, adding central widget, layout style and status bar. """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QtGui.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)


        self.centralWidget = StepScanCentralWidget()
        layout.addWidget(self.centralWidget, 0, 0)
        self.setCentralWidget(self.centralWidget)
        self.statusBar().showMessage('Message in statusbar.')

        self.show()



class StepScanCentralWidget(QtWidgets.QWidget):
    """ Main widget for the step scan measuring software """

    def __init__(self):
        super().__init__()
        self.title = 'centralWidget'
        self.scan = scan.Scan() # this will contain all data!

        self.parameters = Parameter.create(name='params', type='group', children=self.scan.parameters)
        # self.scan_thread = QtCore.QThread()

        self.n_of_averages = 5
        self.scanning = False
        self.lockinParameters = ['X','Y']
        self.plotParameters = self.lockinParameters
        self.plotData = {}
        for key in self.plotParameters:
            self.plotData[key]= {0: []}


        """ Generate GUI layout """
        self.setup_font_styles()
        self.make_layout()
        self.show()

        self.scansLeft = self.n_of_averages

        self.monitor_timer = QtCore.QTimer()
        self.monitor_timer.timeout.connect(self.on_monitor_timer)
        self.monitor_timer.start(400)


        self.instruments = {}
        if not testMode:
            self.instruments['lockin'] = USBGPIBlib.USBGPIB()
            self.instruments['lockin'].connect()
            self.instruments['stage'] = NewPortStagelib.NewPortStage()
            self.instruments['stage'].Initilize()
            self.instruments['stage'].Initilize()
            self.instruments['stage'].Initilize()

    def make_layout(self):
        """ Generate the GUI layout """

        # ------- DEFINE LEFT PANEL -------
        layoutLeftPanel = QtWidgets.QVBoxLayout()
        layoutLeftPanel.setSpacing(10)

        self.parameterTree = ParameterTree()
        self.parameterTree.setParameters(self.parameters)

        layoutLeftPanel.addWidget(QtGui.QLabel('Scan Parameters:'))
        layoutLeftPanel.addWidget(self.parameterTree,stretch=1)

        self.printTreeButton = QtWidgets.QPushButton('print tree')
        self.printTreeButton.clicked.connect(self.print_parameters)
        layoutLeftPanel.addWidget(self.printTreeButton)

        # ------- DEFINE CENTRAL PANEL -------
        layoutCentralPanel = QtWidgets.QGridLayout()
        layoutCentralPanel.setSpacing(10)

        self.mainPlot = PG.PlotWidget()
        layoutCentralPanel.addWidget(self.mainPlot,0,0,2,1)
        self.scanStatusBox = QtWidgets.QGroupBox('Scan Status:')
        layoutCentralPanel.addWidget(self.scanStatusBox,2,0,1,1)
        scanStatusLayout = QtWidgets.QGridLayout()
        self.scanStatusBox.setLayout(scanStatusLayout)
        self.startstop_button = QtWidgets.QPushButton('Start Scan')
        self.startstop_button.clicked.connect(self.startstop_scan)
        scanStatusLayout.addWidget(self.startstop_button, 0, 2, 1, 2)

        self.save_button = QtWidgets.QPushButton('save')
        scanStatusLayout.addWidget(self.save_button,1,3,1,1)
        self.save_button.clicked.connect(self.save_to_HDF5)
        self.n_of_averages_box = QtWidgets.QSpinBox()
        # self.n_of_averages_box.valueChanged.connect(self.set_n_of_averages)
        self.n_of_averages_box.setValue(self.n_of_averages)
        scanStatusLayout.addWidget(self.n_of_averages_box,1,2,2,2)


        self.moveStageToButton = QtWidgets.QPushButton('Move stage')
        self.moveStageToSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveStageToSpinBox.setSuffix(' mm')
        self.moveStageToSpinBox.setRange(-150, 150)
        self.moveStageToSpinBox.setValue(0)
        self.moveStageToSpinBox.setSingleStep(0.01)
        self.moveStageToButton.clicked.connect(self.move_stage_to_spinbox_value)


        scanStatusLayout.addWidget(QtWidgets.QLabel("Position:"), 0, 0)
        scanStatusLayout.addWidget(self.moveStageToSpinBox,0,1)
        scanStatusLayout.addWidget(self.moveStageToButton,1,0,1,2)

        # ------- DEFINE RIGHT PANEL -------
        layoutRightPanel = QtWidgets.QVBoxLayout()
        layoutRightPanel.setSpacing(10)

        self.monitorGroup = QtWidgets.QGroupBox('Instrument Monitor')
        layoutRightPanel.addWidget(self.monitorGroup)
        monitorGroupLayout = QtWidgets.QGridLayout()
        self.monitorGroup.setLayout(monitorGroupLayout)

        self.lockin_X_monitor = QtWidgets.QLabel('1,00')
        self.lockin_X_monitor.setFont(self.monitor_number_font)
        lockin_X_monitor_box = QtWidgets.QLabel('Lockin X:')
        monitorGroupLayout.addWidget(lockin_X_monitor_box, 0, 0)
        monitorGroupLayout.addWidget(self.lockin_X_monitor, 1, 0, 1, 3)

        self.lockin_Y_monitor = QtWidgets.QLabel('1,00')
        self.lockin_Y_monitor.setFont(self.monitor_number_font)

        monitorGroupLayout.addWidget(QtWidgets.QLabel('Lockin Y:'), 2, 0)
        monitorGroupLayout.addWidget(self.lockin_Y_monitor, 3, 0, 1, 3)

        self.temperature_monitor = QtWidgets.QLabel('1,00')
        self.temperature_monitor.setFont(self.monitor_number_font)
        monitorGroupLayout.addWidget(QtWidgets.QLabel('Temperature:'), 4, 0)
        monitorGroupLayout.addWidget(self.temperature_monitor, 5, 0, 1, 3)

        self.setTimeAxisGroup = QtWidgets.QGroupBox('Set Time Axis')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setTimeAxisGroup.setSizePolicy(sizePolicy)
        layoutRightPanel.addWidget(self.setTimeAxisGroup)
        setTimeAxisGroupLayout = QtWidgets.QGridLayout()
        self.setTimeAxisGroup.setLayout(setTimeAxisGroupLayout)

        setTimeAxisGroupLayout.addWidget(QtWidgets.QLabel('from:'), 0, 0)
        setTimeAxisGroupLayout.addWidget(QtWidgets.QLabel('Step size:'), 0, 1)

        v_position = 0
        self.timeRanges = 2
        init_steps = [0.2, 0.2, 0.05, 0.2, 0.5, 2, 5, 10]
        init_ranges = [-1, 0, 1, 3, 10, 50, 100, 200, 500]
        for i in range(self.timeRanges):
            v_position = i+1
            name_from = 'timeRange' + str(i) + '_from'
            value = QtWidgets.QDoubleSpinBox()
            setattr(self, name_from, QtWidgets.QDoubleSpinBox())
            getattr(self, name_from).setRange(-1000, 1000)
            getattr(self, name_from).setSuffix(' ps')
            getattr(self, name_from).setSingleStep(0.01)
            getattr(self, name_from).setValue(init_ranges[i])
            setTimeAxisGroupLayout.addWidget(getattr(self, name_from), v_position, 0)
            name_step = 'timeRange' + str(i) + '_step'
            setattr(self, name_step, QtWidgets.QDoubleSpinBox())
            getattr(self, name_step).setRange(0, 100)
            getattr(self, name_step).setSuffix(' ps')
            getattr(self, name_step).setSingleStep(0.01)
            getattr(self, name_step).setValue(init_steps[i])

            setTimeAxisGroupLayout.addWidget(getattr(self, name_step), v_position, 1)

        self.setTimeAxisApply = QtWidgets.QPushButton('Apply')
        self.setTimeAxisApply.clicked.connect(self.set_time_axis)
        setTimeAxisGroupLayout.addWidget(self.setTimeAxisApply, v_position+1, 0, 1, 2)



        mainLayout = QtWidgets.QHBoxLayout()  # create a grid for subWidgets
        mainLayout.setSpacing(10)
        mainLayout.addLayout(layoutLeftPanel)
        mainLayout.addLayout(layoutCentralPanel)
        mainLayout.addLayout(layoutRightPanel)

        self.setLayout(mainLayout)


    def setup_font_styles(self):
        """ Give settings for fonts to use in widget"""
        self.title_font = QtGui.QFont()
        self.title_font.setBold(True)
        self.title_font.setPixelSize(15)

        self.subtitle_font = QtGui.QFont()
        self.subtitle_font.setPixelSize(12)
        self.subtitle_font.setBold(True)

        self.text_font = QtGui.QFont()
        self.text_font.setPixelSize(10)

        self.monitor_number_font = QtGui.QFont()
        self.monitor_number_font.setPixelSize(14)
        self.monitor_number_font.setBold(True)

    @QtCore.pyqtSlot()
    def set_n_of_averages(self,nAvg):
        self.n_of_averages = nAvg

    @QtCore.pyqtSlot()
    def set_time_axis(self):
        """ Uses the values given for the time ranges to define the time scale and corresponding stage positions for the scan."""
        startPoints = []
        steps = []
        for i in range(self.timeRanges):
            varName_from = 'timeRange' + str(i) + '_from'
            startPoints.append(np.float64(getattr(self, varName_from).cleanText()))
            varName_step = 'timeRange' + str(i) + '_step'
            steps.append(np.float64(getattr(self, varName_step).cleanText()))
        timescale = []
        stagePositions = []
        for i in range(len(startPoints)-1):
            start = startPoints[i]
            stop = startPoints[i+1]
            step = steps[i]
            range_points = np.arange(start,stop,step)
            for j in range_points:
                timescale.append(j)
                stagePositions.append(j*299.792458)
        if gfs.monotonically_increasing(timescale):
            self.scan.timeScale = timescale
            self.scan.stagePositions = stagePositions

        else:
            print('time scale defined is not monotonous! check again!!')
        print('Scan contains {0} points, ranging from {1} to {2} ps.'.format(len(self.scan.timeScale),self.scan.timeScale[0],self.scan.timeScale[-1]))

    @QtCore.pyqtSlot()
    def on_monitor_timer(self):
        if testMode:
            self.X = np.random.rand(1)[0]*0.001
            self.Y = np.random.rand(1)[0]*0.001
        else:
            self.X = self.instruments['lockin'].ReadValue('X')
            self.Y = self.instruments['lockin'].ReadValue('Y')
        self.lockin_X_monitor.setText('{:.3E} V'.format(self.X))
        self.lockin_Y_monitor.setText('{:.3E} V'.format(self.Y))

    @QtCore.pyqtSlot()
    def move_stage_to_spinbox_value(self):
        newPos = self.moveStageToSpinBox.value()
        if testMode:
            print('Stage moved to: {}'.format(newPos))
        else:
            self.instruments['stage'].MoveTo(newPos)

    @QtCore.pyqtSlot()
    def startstop_scan(self):
        if self.scanning:
            self.stop_scan_after_current()
            self.scanning = False
        else:
            print('scan started')
            for parameter in self.lockinParameters:
                self.scan.data[parameter] = pd.DataFrame(np.zeros(len(self.scan.timeScale)),columns=['avg'], index = self.scan.timeScale)
            self.scanNumber = 0
            self.make_single_scan()
            self.scanning = True

    @QtCore.pyqtSlot()
    def make_single_scan(self):
        """ performs a single scan with the given stagePositions"""
        self.scan_thread = QtCore.QThread()
        print('scanning for {0} with {1} dwelltime'.format(self.lockinParameters,self.scan.dwellTime))
        self.w = StepScanWorker(self.scan.stagePositions, self.lockinParameters, self.scan.dwellTime)
        self.w.finished[pd.DataFrame].connect(self.on_finished)
        self.w.newData.connect(self.append_new_data)
        self.w.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.w.work)
        self.scan_thread.start()

    @QtCore.pyqtSlot(dict)
    def on_finished(self,dict):
        """ Prints the threads's output and starts a new one until total number of averages is reached"""
        print(dict)
        for key, item in dict.items():
            self.scan.data[key][self.scanNumber] = item
            self.scan.data['avg'][key] = self.scan.data[key].mean(axis=1)

        self.scanNumber += 1
        for key in self.plotParameters:
            self.plotData[key][self.scanNumber] = []
        if self.scanNumber >= self.n_of_averages:
            print('done scanning')
            for key, value in self.scan.data.items():
                print(key)
                print(value)
        else:
            self.make_single_scan()

    @QtCore.pyqtSlot()
    def stop_scan_after_current(self):
        print('scan will stop after current run.')
        self.n_of_averages = self.scanNumber
        self.n_of_averages_box.setValue(self.scanNumber)

    def append_new_data(self,index,value):
        for key in self.plotParameters:
            self.plotData[key][self.scanNumber].append(value[key])
        self.plot_parameters()

    def save_to_HDF5(self):
        self.scan.save_to_HDF5()
        self.scan.save_to_csv()

    def plot_parameters(self):

        for key in self.plotParameters:
            y = self.plotData[key][self.scanNumber]
            x = self.scan.timeScale[0:len(y)]
            self.mainPlot.plot(x, y , pen=(125, 0, 0))


    def clear_plot(self):
        self.mainPlot.clear()

    @QtCore.pyqtSlot()
    def print_parameters(self):
        print(self.scan.parameters)



class StepScanWorker(QtCore.QObject):
    """ Object that performs a single scan. It is intended to be transfered to a new thread."""

    # Signals:
    finished = QtCore.pyqtSignal(dict)
    newData = QtCore.pyqtSignal(int, dict)
    scanning = QtCore.pyqtSignal(bool)

    def __init__(self, stagePositions, lockinParameters, dwelltime):
        super().__init__()
        self.stagePositions = stagePositions
        self.dwelltime = dwelltime
        self.lockinParameters = lockinParameters
        self.data = {}
        for parameter in self.lockinParameters:
            self.data[parameter] = []

    def work(self):
        print('worker scanning')
        for i in range(len(self.stagePositions)):

            # self.move_stage_to_spinbox_value(self.stagePositions[i])

            newdataDict = self.read_lockin()
            # print(newdataDict)
            self.newData.emit(i, newdataDict)
            for parameter, value in newdataDict.items():
                self.data[parameter].append(value)
            print(self.dwelltime)
            time.sleep(self.dwelltime)
        self.finished.emit(self.data)


    def move_stage_to(self,pos):
        # self.instruments['stage'].MoveTo(pos)
        pass

    def read_lockin(self):

        vals = np.random.rand(2)
        snapVals = {}
        for i in range(len(self.lockinParameters)):
            snapVals[self.lockinParameters[i]] = vals[i]
        # snapVals = self.instruments['lockin'].readSnap()
        return snapVals


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


if __name__ == '__main__':

    pass