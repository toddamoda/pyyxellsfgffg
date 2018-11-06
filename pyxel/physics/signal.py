#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel Signal class."""
# import numpy as np
from astropy.units import cds

cds.enable()


class Signal:
    """Signal class defining and storing information of detector signal."""

    def __init__(self, detector=None):
        """TBW.

        :param detector:
        """
        self.detector = detector
        self.array = None
