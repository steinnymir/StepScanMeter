# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\py_code\StepScanMeter\core\QT\ui_plotArea.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Ui_PlotArea(object):
    def setupUi(self, Ui_PlotArea):
        Ui_PlotArea.setObjectName("Ui_PlotArea")
        Ui_PlotArea.resize(1088, 614)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        Ui_PlotArea.setWidget(self.dockWidgetContents)

        self.retranslateUi(Ui_PlotArea)
        QtCore.QMetaObject.connectSlotsByName(Ui_PlotArea)

    def retranslateUi(self, Ui_PlotArea):
        _translate = QtCore.QCoreApplication.translate
        Ui_PlotArea.setWindowTitle(_translate("Ui_PlotArea", "DockWidget"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Ui_PlotArea = QtWidgets.QDockWidget()
    ui = Ui_Ui_PlotArea()
    ui.setupUi(Ui_PlotArea)
    Ui_PlotArea.show()
    sys.exit(app.exec_())

