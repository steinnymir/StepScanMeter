"""
@author Steinn Ymir Agustsson

"""

""" 

Usefull functions to be implemented throughout the whole repo.

"""

import numpy as np
from PyQt5 import QtWidgets

def monotonically_increasing(l):
    return all(x < y for x, y in zip(l, l[1:]))


def raise_Qerror(self, doingWhat, errorHandle, type='Warning', popup=True):
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


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


