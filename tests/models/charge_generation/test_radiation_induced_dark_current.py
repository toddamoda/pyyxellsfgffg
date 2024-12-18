#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tests for radiation induced dark current model."""

import pytest

from pyxel.detectors import (
    CCD,
    CMOS,
    CCDGeometry,
    Characteristics,
    CMOSGeometry,
    Environment,
    ReadoutProperties,
)
from pyxel.models.charge_generation import radiation_induced_dark_current


@pytest.fixture(params=["ccd", "cmos"])
def detector_5x5(request: pytest.FixtureRequest) -> CCD | CMOS:
    """Create a valid CMOS detector."""
    if request.param == "cmos":
        detector = CMOS(
            geometry=CMOSGeometry(
                row=5,
                col=5,
                total_thickness=40.0,
                pixel_vert_size=10.0,
                pixel_horz_size=10.0,
            ),
            environment=Environment(temperature=80),
            characteristics=Characteristics(),
        )

    elif request.param == "ccd":
        detector = CCD(
            geometry=CCDGeometry(
                row=5,
                col=5,
                total_thickness=40.0,
                pixel_vert_size=10.0,
                pixel_horz_size=10.0,
            ),
            environment=Environment(temperature=80),
            characteristics=Characteristics(),
        )

    else:
        raise NotImplementedError

    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


def test_radiation_induced_dark_current_valid(detector_5x5: CCD | CMOS):
    """Test model 'radiation_induced_dark_current' with valid inputs."""
    detector = detector_5x5

    # Call the function with appropriate arguments
    depletion_volume = 64  # µm3
    annealing_time = 0.1  # weeks
    displacement_dose = 50 * 10  # TeV/g
    seed = 42

    radiation_induced_dark_current(
        detector=detector,
        depletion_volume=depletion_volume,
        annealing_time=annealing_time,
        displacement_dose=displacement_dose,
        seed=seed,
        shot_noise=False,
    )
