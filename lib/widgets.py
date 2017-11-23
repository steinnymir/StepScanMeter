import pyqtgraph as PG
import qdarkstyle
from PyQt5 import QtGui as QG, QtWidgets as QW, QtCore as QC
from pyqtgraph.parametertree import Parameter, ParameterTree
from lib import gfs
import numpy as np
from lib import scan
import pandas as pd


class StepScanMainWindow(QW.QMainWindow):
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

        layout = QG.QGridLayout()  # create a grid for subWidgets
        layout.setSpacing(10)
        self.setLayout(layout)


        self.centralWidget = StepScanCentralWidget()
        layout.addWidget(self.centralWidget, 0, 0)
        self.setCentralWidget(self.centralWidget)
        self.statusBar().showMessage('Message in statusbar.')

        self.show()



class StepScanCentralWidget(QW.QWidget):
    """ Main widget for the step scan measuring software """

    def __init__(self):
        super().__init__()
        self.title = 'centralWidget'
        self.scan = scan.Scan() # this will contain all data!

        self.parameters = Parameter.create(name='params', type='group', children=self.scan.parameters)

        """ Generate GUI layout """
        self.setup_font_styles()
        self.make_layout()
        self.show()

        self.scan_timer = QC.QTimer()
        self.scan_timer.timeout.connect(self.on_scan_timer)



    def make_layout(self):
        """ Generate the GUI layout """

        # ------- DEFINE LEFT PANEL -------
        layoutLeftPanel = QW.QVBoxLayout()
        layoutLeftPanel.setSpacing(10)


        self.parameterTree = ParameterTree()
        self.parameterTree.setParameters(self.parameters)

        layoutLeftPanel.addWidget(QG.QLabel('Scan Parameters:'))
        layoutLeftPanel.addWidget(self.parameterTree,stretch=1)


        # ------- DEFINE CENTRAL PANEL -------
        layoutCentralPanel = QW.QGridLayout()
        layoutCentralPanel.setSpacing(10)

        self.mainPlot = PG.PlotWidget()
        layoutCentralPanel.addWidget(self.mainPlot,0,0,2,1)
        self.scanStatusBox = QW.QGroupBox('Scan Status:')
        layoutCentralPanel.addWidget(self.scanStatusBox,2,0,1,1)
        scanStatusLayout = QW.QGridLayout()
        self.scanStatusBox.setLayout(scanStatusLayout)
        self.start_button = QW.QPushButton('Start')
        self.start_button.clicked.connect(self.start_scan)
        scanStatusLayout.addWidget(self.start_button,0,0)

        # ------- DEFINE RIGHT PANEL -------
        layoutRightPanel = QW.QVBoxLayout()
        layoutRightPanel.setSpacing(10)

        self.monitorGroup = QW.QGroupBox('Instrument Monitor')
        layoutRightPanel.addWidget(self.monitorGroup)
        monitorGroupLayout = QW.QGridLayout()
        self.monitorGroup.setLayout(monitorGroupLayout)


        self.lockin_X_monitor = QW.QLabel('1,00')
        self.lockin_X_monitor.setFont(self.monitor_number_font)
        lockin_X_monitor_box = QW.QLabel('Lockin X:')
        monitorGroupLayout.addWidget(lockin_X_monitor_box, 0, 0)
        monitorGroupLayout.addWidget(self.lockin_X_monitor, 1, 0, 1, 3)

        self.lockin_Y_monitor = QW.QLabel('1,00')
        self.lockin_Y_monitor.setFont(self.monitor_number_font)

        monitorGroupLayout.addWidget(QW.QLabel('Lockin X:'), 2, 0)
        monitorGroupLayout.addWidget(self.lockin_Y_monitor, 3, 0, 1, 3)

        self.temperature_monitor = QW.QLabel('1,00')
        self.temperature_monitor.setFont(self.monitor_number_font)
        monitorGroupLayout.addWidget(QW.QLabel('Temperature:'), 4, 0)
        monitorGroupLayout.addWidget(self.temperature_monitor, 5, 0, 1, 3)

        self.setTimeAxisGroup = QW.QGroupBox('Set Time Axis')
        sizePolicy = QW.QSizePolicy(QW.QSizePolicy.Minimum, QW.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setTimeAxisGroup.setSizePolicy(sizePolicy)
        layoutRightPanel.addWidget(self.setTimeAxisGroup)
        setTimeAxisGroupLayout = QW.QGridLayout()
        self.setTimeAxisGroup.setLayout(setTimeAxisGroupLayout)

        setTimeAxisGroupLayout.addWidget(QW.QLabel('from:'),0,0)
        setTimeAxisGroupLayout.addWidget(QW.QLabel('Step size:'),0,1)

        v_position = 0
        self.timeRanges = 5
        init_steps = [0.01, 0.01, 0.05, 0.2, 0.5, 2, 5, 10]
        init_ranges = [-1, 0, 1, 3, 10, 50, 100, 200, 500]
        for i in range(self.timeRanges):
            v_position = i+1
            name_from = 'timeRange' + str(i) + '_from'
            value = QW.QDoubleSpinBox()
            setattr(self, name_from, QW.QDoubleSpinBox())
            getattr(self, name_from).setRange(-1000, 1000)
            getattr(self, name_from).setSuffix(' ps')
            getattr(self, name_from).setSingleStep(0.01)
            getattr(self, name_from).setValue(init_ranges[i])
            setTimeAxisGroupLayout.addWidget(getattr(self, name_from), v_position, 0)
            name_step = 'timeRange' + str(i) + '_step'
            setattr(self, name_step, QW.QDoubleSpinBox())
            getattr(self, name_step).setRange(0, 100)
            getattr(self, name_step).setSuffix(' ps')
            getattr(self, name_step).setSingleStep(0.01)
            getattr(self, name_step).setValue(init_steps[i])

            setTimeAxisGroupLayout.addWidget(getattr(self, name_step), v_position, 1)

        self.setTimeAxisApply = QW.QPushButton('Apply')
        self.setTimeAxisApply.clicked.connect(self.set_time_axis)
        setTimeAxisGroupLayout.addWidget(self.setTimeAxisApply, v_position+1, 0, 1, 2)



        mainLayout = QW.QHBoxLayout()  # create a grid for subWidgets
        mainLayout.setSpacing(10)
        mainLayout.addLayout(layoutLeftPanel)
        mainLayout.addLayout(layoutCentralPanel)
        mainLayout.addLayout(layoutRightPanel)

        self.setLayout(mainLayout)


    def setup_font_styles(self):
        """ Give settings for fonts to use in widget"""
        self.title_font = QG.QFont()
        self.title_font.setBold(True)
        self.title_font.setPixelSize(15)

        self.subtitle_font = QG.QFont()
        self.subtitle_font.setPixelSize(12)
        self.subtitle_font.setBold(True)

        self.text_font = QG.QFont()
        self.text_font.setPixelSize(10)

        self.monitor_number_font = QG.QFont()
        self.monitor_number_font.setPixelSize(12)
        self.monitor_number_font.setBold(True)

    @QC.pyqtSlot()
    def set_time_axis(self):
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
            print('time scale defined is not monotonous! check!')
        print(self.scan.timeScale)
        print(self.scan.stagePositions)

    def start_scan(self):
        self.test_start_scan()



    def test_start_scan(self):
        print('scan started')
        self.clear_plot()

        self.currentPoint=0
        self.scan_timer.start(self.scan.dwellTime)


    def on_scan_timer(self):
        if self.currentPoint < len(self.scan.timeScale):
            value = self.read_values()
            self.scan.currentScan['time'].append(self.scan.timeScale[self.currentPoint])
            self.scan.currentScan['x'].append(value[0])
            self.scan.currentScan['y'].append(value[1])

            self.currentPoint += 1
        else:
            self.scan_timer.stop()
            print('scan stopped')

        self.refresh_plot()


    def read_values(self):
        x = np.random.rand(2)
        return x[0]-0.5,x[1]-0.5

    def clear_plot(self):
        self.mainPlot.clear()

    def refresh_plot(self):
        t = self.scan.currentScan['time']
        x = self.scan.currentScan['x']
        y = self.scan.currentScan['y']

        self.plot = self.mainPlot.plot(t, x, pen=(255, 0, 0))
        self.plot = self.mainPlot.plot(t, y, pen=(0, 255, 0))

        # self.mainPlot.