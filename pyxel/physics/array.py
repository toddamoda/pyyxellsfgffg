
#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Signal class."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry

cds.enable()


class Array:
    """Array class."""

    def __init__(self) -> None:
        """TBW.

        :param geo:
        """
        self.type = None
        self.exp_type = None
        self.type_list = None
        self._array = None

    @property
    def array(self):
        """TBW."""
        return self._array.astype(self.type)     # TODO

    @array.setter
    def array(self, value):
        """TBW."""
        if isinstance(value, np.ndarray):      # TODO
            if value.dtype in self.type_list:
                self.type = value.dtype
            else:
                raise TypeError('Type of %s array should be a(n) %s' %
                                (self.__class__.__name__, self.exp_type.__name__))

            self._array = value
        else:
            raise TypeError('%s array should be a numpy.ndarray' % self.__class__.__name__)
