#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from decimal import Decimal
from pathlib import Path

import numpy as np
import pytest
from astropy.units import Quantity

from pyxel.calibration.util import sanitize


@pytest.mark.parametrize(
    "data, exp_data",
    [
        (None, None),
        (True, True),
        (False, False),
        (Path("foo"), "foo"),
        (2, 2),
        (np.uint64(3), 3),
        (np.int16(4), 4),
        (3.14, 3.14),
        (np.float64(1.2), 1.2),
        (Decimal("2"), "2"),
        (Quantity(3.4, unit="m"), "3.4 m"),
        ((1, 2.0, "foo"), (1, 2.0, "foo")),
        ([1, 2.0, "foo"], [1, 2.0, "foo"]),
        (
            {
                (1, 2): None,
                3: [True, False, Path("foo")],
                "bar": {"4": Quantity(5.0, unit="electron")},
            },
            {(1, 2): None, 3: [True, False, "foo"], "bar": {"4": "5.0 electron"}},
        ),
    ],
)
def test_sanitize(data, exp_data):
    """Test function 'sanitize'."""
    result = sanitize(data)

    assert result == exp_data
