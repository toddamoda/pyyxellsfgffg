#  Copyright (c) European Space Agency, 2017.
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
from .photon3d import Photon3D
from .scene import Scene
from .pixel import Pixel
from .signal import Signal
from .charge import Charge
from .image import Image
from .phase import Phase
from .persistence import Persistence, SimplePersistence


def _get_array_if_initialized(obj: Optional[Array]) -> Optional[np.ndarray]:
    """Get a copy of the numpy array if the object is fully initialized.

    Parameters
    ----------
    obj : Array, Optional
        An object that may contain an array.

    Returns
    -------
    Array or None
        A copy of the numpy array contained in 'obj' if it has an array.
    """
    if obj and obj._array is not None:
        return obj.array.copy()
    return None
