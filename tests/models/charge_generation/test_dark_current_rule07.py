#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Tests for dark current models."""

from typing import Optional

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
from pyxel.models.charge_generation import dark_current_rule07


@pytest.fixture
def cmos_10x10() -> CMOS:
    """Create a valid CCD detector."""
    detector = CMOS(
        geometry=CMOSGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(temperature=273.15),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


@pytest.mark.parametrize(
    "cutoff_wavelength, spatial_noise_factor, temporal_noise",
    [
        pytest.param(None, None, True, id="Use default 'cutoff_wavelength'"),
        pytest.param(1.7, 0.5, True, id="With 'spatial_noise_factor'"),
        pytest.param(15.0, None, False, id="Without 'temporal_noise'"),
    ],
)
def test_dark_current_rule07_valid(
    cmos_10x10: CMOS,
    cutoff_wavelength: Optional[float],
    spatial_noise_factor: Optional[float],
    temporal_noise: bool,
):
    """Test model 'dark_current_rule07' with valid inputs."""
    if cutoff_wavelength is None:
        dark_current_rule07(
            detector=cmos_10x10,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
        )
    else:
        dark_current_rule07(
            detector=cmos_10x10,
            cutoff_wavelength=cutoff_wavelength,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
        )


@pytest.mark.parametrize(
    "cutoff_wavelength, exp_exc, exp_msg",
    [
        (1.69, ValueError, r"'cutoff' must be between 1.7 and 15.0"),
        (15.01, ValueError, r"'cutoff' must be between 1.7 and 15.0"),
    ],
)
def test_dark_current_rule07_invalid(
    cmos_10x10: CMOS, cutoff_wavelength, exp_exc, exp_msg
):
    """Test model 'dark_current_rule07' with invalid inputs."""
    with pytest.raises(exp_exc, match=exp_msg):
        dark_current_rule07(detector=cmos_10x10, cutoff_wavelength=cutoff_wavelength)


def test_dark_current_rule07_with_ccd():
    """Test model 'dark_current_rule07' with a `CCD` detector."""
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

    with pytest.raises(TypeError, match="Expecting a CMOS object for detector."):
        dark_current_rule07(detector=detector)
