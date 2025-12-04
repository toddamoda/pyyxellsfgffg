#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from typing import Annotated, Literal

import pytest
from annotated_types import Ge, Interval

from pyxel.util import check_validity

# ---------------------------------------------------------
# VALID INPUTS (should NOT raise)
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "value, exp_type",
    [
        pytest.param(3.0, float, id="float"),
        pytest.param(3, int, id="int"),
        pytest.param("Hello", str, id="str"),
        pytest.param(True, bool, id="bool"),
        pytest.param((0, 0), tuple[int, int], id="tuple 2 elements"),
        pytest.param("top_left", Literal["top_left", "top_right"], id="literal"),
        pytest.param(3.0, Annotated[float, Ge(0.0)], id="Annotated, >= 0.0"),
        pytest.param(10, Annotated[int, Ge(0)], id="Annotated, > 0"),
        pytest.param(
            (0, 0),
            tuple[Annotated[int, Ge(0)], Annotated[int, Ge(0)]],
            id="Annotated, tuple",
        ),
    ],
)
def test_valid_basic(value, exp_type):
    """Test valid inputs."""
    check_validity(value, exp_type)


@pytest.mark.parametrize(
    "value, exp_type, exp_exc, exp_msg",
    [
        # ---------------------------------------------------------
        # INVALID TYPES (TypeError)
        # ---------------------------------------------------------
        (3.14, int, TypeError, r"Expecting a \'int\'"),
        ("a", float, TypeError, r"Expecting a \'float\'"),
        ([1, 2], tuple[int, int], TypeError, r"Expecting a tuple"),
        # ---------------------------------------------------------
        # INVALID VALUES (ValueError)
        # ---------------------------------------------------------
        (
            3.0,
            Annotated[float, Interval(ge=10.0, le=20.0)],
            ValueError,
            r"Value 3\.0 is less",
        ),
        (3, Annotated[int, Ge(4)], ValueError, r"Value 3 is less"),
    ],
)
def test_invalid_type(value, exp_type, exp_exc, exp_msg):
    """Test invalid inputs."""
    with pytest.raises(exp_exc, match=exp_msg):
        check_validity(value, exp_type)
