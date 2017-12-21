# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson
"""
from PyQt5 import uic
import os



def recompile(uiDir):
    print('compiling folder {}'.format(uiDir))
    uic.compileUiDir(uiDir, execute=True)
    print('done')

if __name__ == '__main__':
    recompile(os.path.realpath(__file__)[:-11])

