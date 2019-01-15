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
    """
    Image class defining and storing information of detector image.

    Accepted array types: np.uint16, np.uint32, np.uint64
    """

    def __init__(self, geo: Geometry) -> None:
        """TBW.

        :param geo:
        """
        super().__init__()                  # TODO: add unit (ADU)
        self.exp_type = np.uint
        self.type_list = [np.uint16, np.uint32, np.uint64]
        self._array = np.zeros((geo.row, geo.col), dtype=self.exp_type)
