# -*- coding: utf-8 -*-
"""

@author: Steinn Ymir Agustsson
"""
import numpy as np
import h5py

def main():
    
    # # properties = {'pump_power': 40, 'probe_power': 20}
    # asd = {'asdf':3}
    # das = {'das':2}
    # dad = {'dad':1}
    # a=2
    #
    # scan = ScanResult(asd, das,  other='bla', another=3)
    # scan.add_properties(dad)
    # print(scan.__dict__)


    f = h5py.File("testfile.hdf5", "w")

    dset = f.create_dataset("data",(100,),dtype='float64')
    dset.attrs['pump_power'] = 12
    dset.attrs['temperature'] = 4.78
    dset.attrs['samplename'] = "RuCl3"

    print([(i,v) for (i,v)  in dset.attrs.items()])






class ScanResult(object):
    """ parent class for any type of measurement data.
    :arg
    """
    def __init__(self, *args, **kwargs):
        self.data = {'x_axis':np.array([]),
                     'raw':np.array([]),
                     'avg':np.array([]),
                     }

        print('args:',args, type(args), len(args))
        print('kwargs:',kwargs, type(kwargs), len(kwargs))
        # manage metadata import
        self._metadataList = []
        self._metadata = {}

        self.add_properties([x for x in args], kwargs)


    def add_properties(self,*args, **kwargs):
        """ Adds any dictionary or list/tuple of dictionaries entries as class attributes.

        Also stores the same values in the metadatata attribute."""
        print('in args:',args, type(args), len(args))
        print('in kwargs:',kwargs, type(kwargs), len(kwargs))
        dicts = {}
        for arg in args:
            if isinstance(arg, dict):
                kwargs = {**kwargs, **arg}
            else:# isinstance(arg, tuple or list):
                try:
                    for dict_arg in arg:
                        kwargs = {**kwargs, **dict_arg}
                except TypeError:
                    print('property "{}" ignored, not a list, tuple or dictionary.'.format(arg))


        for key, val in kwargs.items():
            setattr(self, key, val)
            self._metadataList.append(key)
            self._metadata[key] = val





if __name__ == '__main__':
    main()
