import pyqtgraph as PG
import qdarkstyle
from PyQt5 import QtGui, QtWidgets, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from utils import gfs
import numpy as np
from utils import stepscan
import pandas as pd

import sys
sys.path.append("C:\code\Soft-for-TR-MOKE-setup")
try:
    import NewPortStagelib
    import USBGPIBlib
    testMode = False
except ImportError:
    print('Couldnt import instruments: Test mode activated')
    testMode = True
import time

class StepScanMainWindow(QtWidgets.QMainWindow):
    """ Main application window """

    def __init__(self):
        """Initialize by setting window title, size and graphic options"""
        super().__init__()

        self.setWindowTitle('Step StepScan Meter')
        self.setGeometry(300, 100, 1200, 700)
        self.initUI()
        # set the cool dark theme and other plotting settings
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        PG.setConfigOption('background', 0.1)
        PG.setConfigOption('foreground', 0.7)
        PG.setConfigOptions(antialias=True)


    def initUI(self):
        """Create the layout, adding central widget, layout style and status bar. """

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
        self.scan = stepscan.StepScan() # this will contain all data!

        self.parameters = Parameter.create(name='params', type='group', children=self.scan.parameters)
        # self.scan_thread = QtCore.QThread()

        self.n_of_averages = 5
        self.scansLeft = self.n_of_averages
        self.scanning = False
        self.lockinParameters = ['X','Y']
        self.plotParameters = self.lockinParameters
        self.plotData = {'avg': pd.DataFrame()}
        self.plotPen = {'Xa':(255,0,0),
                        'Ya':(0,255,0),
                        'X':(75,0,0),
                        'Y':(0,75,0),
                        }

        """ Generate GUI layout """
        self.setup_font_styles()
        self.make_layout()
        self.show()


        self.monitor_timer = QtCore.QTimer()
        self.monitor_timer.timeout.connect(self.on_monitor_timer)
        self.stageMoveTimer = QtCore.QTimer()
        self.stageMoveTimer.timeout.connect(self.on_stage_move_timer)


        #self.monitor_timer.start(400)


        self.instruments = {}
        if not testMode:
            self.instruments['lockin'] = USBGPIBlib.USBGPIB()
            self.instruments['lockin'].connect()
            self.instruments['stage'] = NewPortStagelib.NewPortStage()
            self.instruments['stage'].Initilize()
            # self.currentStagePosition = self.instruments['stage'].get_current_position()
        self.currentStagePosition = 0
    def make_layout(self):
        """ Generate the GUI layout """

        # ------- DEFINE LEFT PANEL -------
        layoutLeftPanel = QtWidgets.QVBoxLayout()
        layoutLeftPanel.setSpacing(10)


        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)


        self.parameterTree = ParameterTree()
        self.parameterTree.setParameters(self.parameters)
        self.parameterTree.setSizePolicy(sizePolicy)

        layoutLeftPanel.addWidget(QtGui.QLabel('StepScan Parameters:'))
        layoutLeftPanel.addWidget(self.parameterTree)

        self.printTreeButton = QtWidgets.QPushButton('print tree')
        self.printTreeButton.clicked.connect(self.print_parameters)
        layoutLeftPanel.addWidget(self.printTreeButton)

        # ------- DEFINE CENTRAL PANEL -------
        layoutCentralPanel = QtWidgets.QGridLayout()
        layoutCentralPanel.setSpacing(10)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)



        self.mainPlot = PG.PlotWidget()
        layoutCentralPanel.addWidget(self.mainPlot,0,0,1,2)
        self.mainPlot.setSizePolicy(sizePolicy)


        self.scanStatusBox = QtWidgets.QGroupBox('StepScan Status:')
        layoutCentralPanel.addWidget(self.scanStatusBox,2,0)
        scanStatusLayout = QtWidgets.QGridLayout()
        scanStatusSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.scanStatusBox.setSizePolicy(scanStatusSizePolicy)
        self.scanStatusBox.setLayout(scanStatusLayout)

        self.startstop_button = QtWidgets.QPushButton('Start StepScan')
        self.startstop_button.clicked.connect(self.startstop_scan)
        scanStatusLayout.addWidget(self.startstop_button, 0, 2, 1, 2)

        self.save_button = QtWidgets.QPushButton('save')
        scanStatusLayout.addWidget(self.save_button,1,3,1,1)
        self.save_button.clicked.connect(self.save_to_HDF5)
        self.n_of_averages_box = QtWidgets.QSpinBox()
        # self.n_of_averages_box.valueChanged.connect(self.set_n_of_averages)
        self.n_of_averages_box.setValue(self.n_of_averages)
        scanStatusLayout.addWidget(self.n_of_averages_box,1,2,2,2)

        self.stageControl = QtWidgets.QGroupBox('stageControl:')
        layoutCentralPanel.addWidget(self.stageControl, 2, 1)
        stageControlLayout = QtWidgets.QGridLayout()
        scanStatusSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.stageControl.setSizePolicy(scanStatusSizePolicy)
        self.stageControl.setLayout(stageControlLayout)


        self.moveStageToButton = QtWidgets.QPushButton('Move stage')
        self.moveStageToSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveStageToSpinBox.setSuffix(' mm')
        self.moveStageToSpinBox.setRange(-150, 150)
        self.moveStageToSpinBox.setValue(0)
        self.moveStageToSpinBox.setSingleStep(0.01)
        self.moveStageToButton.clicked.connect(self.move_stage_to_spinbox_value)

        self.moveStageLeft = QtWidgets.QPushButton("<")
        self.moveStageLeft.pressed.connect(lambda: self.moving_stage('-'))
        self.moveStageLeft.released.connect(lambda: self.moving_stage(None))
        self.moveStageRight = QtWidgets.QPushButton(">")
        self.moveStageRight.pressed.connect(lambda: self.moving_stage('+'))
        self.moveStageRight.released.connect(lambda: self.moving_stage(None))


        self.moveStageStep = QtWidgets.QDoubleSpinBox()
        self.moveStageStep.setSuffix(' mm')
        self.moveStageStep.setRange(-150, 150)
        self.moveStageStep.setValue(0.01)
        self.moveStageStep.setSingleStep(0.001)


        stageControlLayout.addWidget(QtWidgets.QLabel("Position:"), 0, 0)
        stageControlLayout.addWidget(self.moveStageToSpinBox,0,1)
        stageControlLayout.addWidget(self.moveStageToButton,0,2)
        stageControlLayout.addWidget(self.moveStageLeft,1,0)
        stageControlLayout.addWidget(self.moveStageStep,1,1)
        stageControlLayout.addWidget(self.moveStageRight,1,2)



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
        self.timeRanges = 3
        init_steps = [0.05, 0.05, 0.1, 0.2, 0.5, 2, 5, 10]
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

    def moving_stage(self, direction):
        if direction is None:
            self.stageMoveTimer.stop()
        else:
            self.moveStageDirection = direction
            self.stageMoveTimer.start(100)

    def on_stage_move_timer(self):
        if self.moveStageDirection == "+":
            newPos = self.currentStagePosition + self.moveStageStep.value()
        elif self.moveStageDirection == "-":
            newPos = self.currentStagePosition - self.moveStageStep.value()
        self.move_stage_to(newPos)

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
                stagePositions.append(j*0.299792458*2)
        if gfs.monotonically_increasing(timescale):
            self.scan.timeScale = timescale
            self.scan.stagePositions = stagePositions

        else:
            print('time scale defined is not monotonous! check again!!')
        print('StepScan contains {0} points, ranging from {1} to {2} ps.'.format(len(self.scan.timeScale),self.scan.timeScale[0],self.scan.timeScale[-1]))

    @QtCore.pyqtSlot()
    def on_monitor_timer(self):
        if testMode:
            self.X = np.random.rand(1)[0]*0.001
            self.Y = np.random.rand(1)[0]*0.001
        else:
            self.X = self.instruments['lockin'].readValue('X')
            self.Y = self.instruments['lockin'].readValue('Y')
        self.lockin_X_monitor.setText('{:.3E} V'.format(self.X))
        self.lockin_Y_monitor.setText('{:.3E} V'.format(self.Y))

    @QtCore.pyqtSlot()
    def move_stage_to_spinbox_value(self):
        newPos = self.moveStageToSpinBox.value()
        if testMode:
            print('Stage moved to: {}'.format(newPos))
        else:
            self.instruments['stage'].MoveTo(newPos)

    @QtCore.pyqtSlot(float)
    def move_stage_to(self, pos):
        self.currentStagePosition = pos
        if testMode:
            print('Stage moved to: {}'.format(pos))
        else:
            self.instruments['stage'].MoveTo(pos)


    @QtCore.pyqtSlot()
    def startstop_scan(self):
        if self.scanning:
            self.stop_scan_after_current()
            self.scanning = False
        else:
            self.monitor_timer.stop()
            print('scan started')
            for parameter in self.lockinParameters:
                self.scan.data[parameter] = pd.DataFrame(np.zeros(len(self.scan.timeScale)),columns=['avg'], index = self.scan.timeScale)
            self.plotData['avg'] = pd.DataFrame(np.zeros(len(self.scan.timeScale)),columns=['avg'], index = self.scan.timeScale)
            self.scanNumber = 0
            self.make_single_scan()
            self.scanning = True

    @QtCore.pyqtSlot()
    def make_single_scan(self):
        """ performs a single scan with the given stagePositions"""
        for parameter in self.plotParameters:
            self.plotData[parameter] = {self.scanNumber: []}


        self.scan_thread = QtCore.QThread()
        print('scanning for {0} with {1} dwelltime'.format(self.lockinParameters,self.scan.settings_lockIn['dwellTime'], self.instruments))
        self.w = StepScanWorker(self.scan.stagePositions, self.lockinParameters, self.scan.settings_lockIn['dwellTime'], self.instruments)
        self.w.finished[pd.DataFrame].connect(self.on_finished)
        self.w.newData.connect(self.append_new_data)
        self.w.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.w.work)
        self.scan_thread.start()

    @QtCore.pyqtSlot(dict)
    def on_finished(self,dict):
        """ Prints the threads's output and starts a new one until total number of averages is reached"""
        # print(dict)
        print('average n {}'.format(self.scanNumber))
        time.sleep(1)

        for key, item in dict.items():
            self.scan.data[key][self.scanNumber] = item
            self.scan.data['avg'][key] = self.scan.data[key].mean(axis=1)
        try:
            self.clear_plot()
            for key in self.plotParameters:
                ya = self.scan.data['avg'][key]
                xa = self.scan.timeScale
                pen = self.plotPen['{}a'.format(key)]
                self.mainPlot.plot(xa, ya, pen=pen)
        except:
            pass
        self.scanNumber += 1
        if self.scanNumber >= self.n_of_averages:
            print('done scanning')
            for key, value in self.scan.data.items():
                print(key)
                print(value)
            self.scanning = False
        else:
            self.make_single_scan()

    @QtCore.pyqtSlot()
    def stop_scan_after_current(self):
        print('scan will stop after current run.')
        self.n_of_averages = self.scanNumber
        self.n_of_averages_box.setValue(self.scanNumber)

    @QtCore.pyqtSlot(int,dict)
    def append_new_data(self,index,value):
        for key in self.plotParameters:
            self.plotData[key][self.scanNumber].append(value[key])
        self.plot_parameters()

    @QtCore.pyqtSlot()
    def save_to_HDF5(self):
        self.scan.save_to_HDF5()
        self.scan.save_to_csv()


    # todo: implement following code for plot refreshing
    # def set_plotdata(self, name, dataset_x, dataset_y):
    #
    #     self.canvas = self.win.addPlot(title='bla')
    #
    #     if name in self.traces:
    #         self.tracesname.setData(dataset_x,dataset_y)
    #     else:
    #         self.traces[name] = self.canvas.plot(pen='y')


    @QtCore.pyqtSlot()
    def plot_parameters(self):
        try:
            for key in self.plotParameters:
                pen = self.plotPen[key]
                y = self.plotData[key][self.scanNumber]
                x = self.scan.timeScale[0:len(y)]
                self.mainPlot.plot(x, y , pen=pen)

        except Exception as error:
            self.rise_error('plotting',error)

    @QtCore.pyqtSlot()
    def clear_plot(self):
        self.mainPlot.clear()

    @QtCore.pyqtSlot()
    def print_parameters(self):
        print(self.scan.parameters)

    @QtCore.pyqtSlot(str,str)
    def rise_error(self, doingWhat, errorHandle, type='Warning', popup=True):
        """ opens a dialog window showing the error"""
        errorMessage = 'Error while {0}:\n{1}'.format(doingWhat,errorHandle)
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

    def closeEvent(self): # todo: implement correct closing procedure
        for name, inst in self.instruments.items():
            inst.close()
            print('{} closed'.format(name))
        QtCore.QCoreApplication.instance().quit()


class StepScanWorker(QtCore.QObject):
    """ Object that performs a single scan. It is intended to be transfered to a new thread."""

    # Signals:
    finished = QtCore.pyqtSignal(dict)
    newData = QtCore.pyqtSignal(int, dict)
    scanning = QtCore.pyqtSignal(bool)

    def __init__(self, stagePositions, lockinParameters, dwelltime, instruments):
        super().__init__()
        self.stagePositions = stagePositions
        self.dwelltime = dwelltime
        self.lockinParameters = lockinParameters
        self.instruments = instruments
        self.data = {}
        for parameter in self.lockinParameters:
            self.data[parameter] = []

    def work(self):
        print('worker scanning')
        for i in range(len(self.stagePositions)):

            self.move_stage_to(self.stagePositions[i])
            time.sleep(self.dwelltime)
            newdataDict = self.read_lockin()
            # print(newdataDict)
            self.newData.emit(i, newdataDict)
            for parameter, value in newdataDict.items():
                self.data[parameter].append(value)
        self.finished.emit(self.data)


    def move_stage_to(self,pos):
        try:
            self.instruments['stage'].MoveTo(pos)
        except Exception as error:
            self.rise_error('moving stage', error, popup=False)

    def read_lockin(self):
        """ read values declared in lockinParameters from the lock-in and outputs them in dict format."""
        try:
            snapVals = self.instruments['lockin'].readSnap(self.lockinParameters)
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






if __name__ == '__main__':

    pass