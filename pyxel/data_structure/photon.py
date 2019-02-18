#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Photon class to generate and track photons."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry
from pyxel.data_structure.array import Array
cds.enable()


class Photon(Array):
    """
    Photon class defining and storing information of all photons.

    Accepted array types: np.int32, np.int64, np.uint32, np.uint64, np.float16, np.float32, np.float64
    """

    def __init__(self, geo: Geometry) -> None:
        """TBW.

        :param geo:
        :param array:
        """
        super().__init__()                  # TODO: add unit (ph)
        self.exp_type = np.int
        self.type_list = [np.int32, np.int64, np.uint32, np.uint64, np.float16, np.float32, np.float64]
        self._array = None

    def new_array(self, new_array):
        """TBW.

        :param new_array:
        """
        if isinstance(new_array, np.ndarray):
            if new_array.dtype in self.type_list:
                self._array = new_array
                self.type = new_array.dtype
            else:
                raise TypeError('Type of %s array should be a(n) %s' %
                                (self.__class__.__name__, self.exp_type.__name__))
        else:
            raise TypeError('%s array should be a numpy.ndarray' % self.__class__.__name__)
