#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections.abc import Sequence
from typing import Literal, Optional

import pytest

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.photon_collection import illumination


@pytest.fixture
def ccd_10x10() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


@pytest.mark.parametrize(
    "level, option, object_size, object_center, time_scale",
    [
        pytest.param(1.0, "uniform", None, None, 1.0, id="valid_uniform"),
        pytest.param(1.0, "elliptic", [2, 2], [5, 5], 1.0, id="valid_elliptic"),
        pytest.param(1.0, "rectangular", [2, 2], [5, 5], 1.0, id="valid_rectangular"),
        pytest.param(
            1.0,
            "rectangular",
            [2, 2],
            [15, 15],
            1.0,
            id="invalid_center_rectangular",
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
        pytest.param(
            1.0,
            "elliptic",
            [2, 2],
            [15, 15],
            1.0,
            id="invalid_center_elliptic",
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
        pytest.param(
            1.0,
            "elliptic",
            [2, 2],
            "foo",
            1.0,
            id="invalid_center_elliptic",
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
        pytest.param(
            1.0,
            "rectangular",
            [2, 2],
            "foo",
            1.0,
            id="invalid_center_rectangular",
            marks=pytest.mark.xfail(raises=ValueError, strict=True),
        ),
    ],
)
def test_illumination(
    ccd_10x10: CCD,
    level: float,
    option: Literal["uniform", "rectangular", "elliptic"],
    object_size: Optional[Sequence[int]],
    object_center: Optional[Sequence[int]],
    time_scale: float,
):
    """Test input parameters for function 'illumination'."""
    illumination(
        detector=ccd_10x10,
        level=level,
        option=option,
        object_size=object_size,
        object_center=object_center,
        time_scale=time_scale,
    )
