#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

from pyxel.util import convert_unit


@pytest.mark.parametrize(
    "name, exp_result",
    [
        ("electron", "e⁻"),
        ("photon", "ph"),
        ("volt", "V"),
        ("adu/s", "adu s⁻¹"),
    ],
)
def test_convert_unit(name, exp_result):
    """Test function 'convert_unit'."""
    result = convert_unit(name)
    assert exp_result == result
