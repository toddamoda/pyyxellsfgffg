#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package to handle and validate matrix structures and readout positions for multi-channels detectors.

**Example of four channels**

In this example four channels ``OP9``, ``OP13``, ``OP1`` and ``OP5`` are
defined in a matrix configuration as follows:

.. figure:: _static/channels.png
    :scale: 70%
    :alt: Channels
    :align: center

Based on the standard readout position, the **channel order** is: ``OP9`` (top-left), ``OP13`` (top-right),
``OP1`` (bottom-left) and ``OP1`` (bottom-right).

The corresponding YAML definition could be:

.. code-block:: yaml


 geometry:
    row: 1028
    col: 1024
    channels:
      matrix: [[OP9, OP13],
               [OP1, OP5 ]]
      readout_position:
        - OP9:  top-left
        - OP13: top-left
        - OP1:  bottom-left
        - OP5:  bottom-left
"""

import difflib
from collections.abc import Hashable, Iterator, Mapping, Sequence
from typing import Literal

import numpy as np
from typing_extensions import Self
from dataclasses import dataclass

@dataclass
class ReferenceGeometry:
    """Class to store and validate the 1D or 2D matrix structure.

    Examples
    --------
    >>> matrix = Matrix([["OP9", "OP13"], ["OP1", "OP5"]])
    >>> matrix.shape
    (2, 2)
    >>> matrix.size
    4
    >>> matrix.ndim
    2
    >>> list(matrix)
    ['OP9', 'OP13', 'OP1', 'OP5']
    """

    row: list[int] | None = None
    col: list[int] | None = None



