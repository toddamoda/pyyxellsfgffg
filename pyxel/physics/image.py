#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Image class."""
import numpy as np
from astropy.units import cds
from pyxel.detectors.geometry import Geometry

cds.enable()


class Image:
    """Image class defining and storing information of detector image."""

    def __init__(self, geo: Geometry) -> None:
        """TBW.

        :param geo:
        """
        self.array = np.zeros((geo.row, geo.col), dtype=float)  # todo
