#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from typing import Annotated, Literal

import pytest
from annotated_types import Ge, Interval

from pyxel.util.check_validity import check_validity

# ---------------------------------------------------------
# VALID INPUTS (should NOT raise)
# ---------------------------------------------------------


def test_valid_basic():
    check_validity(3.0, float)
    check_validity(3, int)
    check_validity("Hello", str)
    check_validity(True, bool)
    check_validity((0, 0), tuple[int, int])
    check_validity("top_left", Literal["top_left", "top_right"])


def test_valid_annotated():
    check_validity(3.0, Annotated[float, Ge(0.0)])
    check_validity(10, Annotated[int, Ge(0)])
    check_validity((0, 0), tuple[Annotated[int, Ge(0)], Annotated[int, Ge(0)]])


# ---------------------------------------------------------
# INVALID TYPES (TypeError)
# ---------------------------------------------------------


def test_invalid_type_simple():
    with pytest.raises(TypeError):
        check_validity(3.14, int)

    with pytest.raises(TypeError):
        check_validity("a", float)

    with pytest.raises(TypeError):
        check_validity([1, 2], tuple[int, int])


# ---------------------------------------------------------
# INVALID VALUES (ValueError)
# ---------------------------------------------------------


def test_invalid_values_annotated():
    with pytest.raises(ValueError):
        check_validity(3.0, Annotated[float, Interval(ge=10.0, le=20.0)])

    with pytest.raises(ValueError):
        check_validity(3, Annotated[int, Ge(4)])
