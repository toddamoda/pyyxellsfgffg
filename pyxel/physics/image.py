#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Image class."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry
from pyxel.physics.array import Array

cds.enable()


class Image(Array):
    """Image class defining and storing information of detector image."""

    def __init__(self, geo: Geometry) -> None:
        """TBW.

        :param geo:
        """
        super().__init__()
        self.exp_type = np.int
        self.type_list = [np.int, np.int16, np.int32, np.int64]       # uint16, uint64 ??
        self._array = np.zeros((geo.row, geo.col), dtype=self.exp_type)
        # np.int8 results bitpix error from fitsfile
