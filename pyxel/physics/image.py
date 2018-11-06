#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Image class."""
# import numpy as np
from astropy.units import cds

cds.enable()


class Image:
    """Image class defining and storing information of detector image."""

    def __init__(self, detector=None):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.array = None
