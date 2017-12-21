# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson
"""
import numpy as np

def main():
    properties = {'pump_power': 40, 'probe_power': 20}
    asd = {'asdf':3}
    scan = Scan(properties, asd,  other='bla')
    print(scan.__dict__)


class Result(object):
    """ parent class for any type of measurement data.
    :arg
    """
    def __init__(self, *args, **kwargs):

        self.data = {'x_axis':np.array([]),
                     'raw':np.array([]),
                     'avg':np.array([]),
                     }

        # manage metadata import
        self._metadataList = []

        for arg in args:

            self.add_property(args, kwargs)


    def add_properties(self,**kwargs):

        # for arg in args:
        #     assert isinstance(arg, dict)
        #     for key, val in arg.items():
        #         setattr(self, key, val)
        #         self._metadataList.append(key)

        for key, val in kwargs.items():
            setattr(self, key, val)
            self._metadataList.append(key)


if __name__ == '__main__':
    main()
