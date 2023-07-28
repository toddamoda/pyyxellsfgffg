#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from copy import deepcopy
from pathlib import Path

import pytest

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Detector,
    Environment,
    ReadoutProperties,
)
from pyxel.models import load_detector, save_detector

try:
    # Check if library 'asdf' is installed
    import asdf  # noqa: F401
except ImportError:
    WITH_ASDF = False
else:
    WITH_ASDF = True


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
    "filename",
    [
        pytest.param(Path("detector.h5"), id="hdf5"),
        pytest.param(Path("detector.asdf"), id="asdf"),
    ],
)
def test_save_load_detector(ccd_10x10: CCD, tmp_path: Path, filename: Path):
    """Test methods `save_detector` and `load_detector`."""
    detector: Detector = deepcopy(ccd_10x10)
    exp_detector: Detector = deepcopy(ccd_10x10)

    full_filename: Path = tmp_path / filename
    if full_filename.suffix == ".asdf" and not WITH_ASDF:
        pytest.skip(reason="Missing library 'asdf'")

    # Save to a file
    save_detector(detector=detector, filename=full_filename)
    assert full_filename.exists()

    # Load from a file
    load_detector(detector=detector, filename=full_filename)

    assert detector == exp_detector
