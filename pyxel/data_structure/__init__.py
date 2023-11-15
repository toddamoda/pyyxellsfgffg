#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

# flake8: noqa
from typing import Optional
from collections.abc import Mapping

import numpy as np

from .array import Array
from .photon import Photon
from .scene import Scene
from .pixel import Pixel
from .signal import Signal
from .charge import Charge
from .image import Image
from .phase import Phase
from .persistence import Persistence, SimplePersistence


def copy_array(obj: Optional[Array]) -> Optional[np.ndarray]:
    """Copy the array if the object has an array."""
    if obj and obj.has_array:
        return obj.array.copy()
    return None


def load_array(data: Mapping, key: str, obj: Optional[Array]) -> None:
    """Load new data into array."""
    if obj is not None:
        if key in data:
            if data[key] is not None:
                obj.array = np.asarray(data[key])
            else:
                obj._array = None
