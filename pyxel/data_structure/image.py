#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Image class."""

from typing import TYPE_CHECKING

import numpy as np

from pyxel.data_structure import Array

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Image(Array):
    """
    Image class defining and storing information of detector image.

    Accepted array types: ``np.uint16``, ``np.uint32``, ``np.uint64``
    """

    EXP_TYPE = np.dtype(np.uint64)
    TYPE_LIST = (
        np.dtype(np.uint8),
        np.dtype(np.uint16),
        np.dtype(np.uint32),
        np.dtype(np.uint64),
    )
    NAME = "Image"
    UNIT = "adu"

    def __init__(self, geo: "Geometry"):
        super().__init__(shape=(geo.row, geo.col))
