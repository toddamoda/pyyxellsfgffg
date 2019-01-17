#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Pixel class."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry
from pyxel.data_structure.array import Array
cds.enable()


class Pixel(Array):
    """
    Pixel class defining and storing information of charge packets within pixels.

    Accepted array types: np.int32, np.int64, np.uint32, np.uint64, np.float16, np.float32, np.float64
    """

    def __init__(self, geo: Geometry) -> None:
        """TBW.

        :param geo:
        """
        super().__init__()                  # TODO: add unit (e-)
        self.exp_type = np.int
        self.type_list = [np.int32, np.int64, np.uint32, np.uint64, np.float16, np.float32, np.float64]
        self._array = np.zeros((geo.row, geo.col), dtype=self.exp_type)
