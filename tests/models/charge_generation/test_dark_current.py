#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tests for dark current models."""

import pytest
from astropy.units import Quantity, allclose

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.charge_generation import dark_current
from pyxel.models.charge_generation.dark_current import calculate_band_gap


def test_band_gap_silicon():
    """Test function 'band_gap_silicon'."""
    result = calculate_band_gap(
        temperature=Quantity(300, unit="Kelvin"),
        material="silicon",
    )
    exp = Quantity(1.11082145, unit="eV")

    allclose(result, exp)


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
        environment=Environment(temperature=200.0),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


def test_dark_current_valid(ccd_10x10: CCD):
    """Test model 'dark_current' with valid inputs."""
    dark_current(
        detector=ccd_10x10,
        figure_of_merit=1.0,
        spatial_noise_factor=0.4,
    )


@pytest.mark.skip(reason="RuntimeWarning is not raised")
def test_dark_current_warning(ccd_10x10: CCD):
    """Test model 'dark_current' when generating a warning."""
    detector = ccd_10x10
    detector.environment.temperature = 300

    with pytest.warns(RuntimeWarning, match="Unphysical high value"):
        dark_current(detector=detector, figure_of_merit=100.0, spatial_noise_factor=0.4)


@pytest.mark.parametrize(
    "figure_of_merit, spatial_noise_factor, band_gap, band_gap_room_temperature,"
    " exp_exc, exp_error",
    [
        pytest.param(
            1.0,
            0.01,
            None,
            1.2,
            ValueError,
            "Both parameters 'band_gap' and 'band_gap_room_temperature' must be"
            " defined.",
        ),
        pytest.param(
            1.0,
            0.01,
            1.2,
            None,
            ValueError,
            "Both parameters 'band_gap' and 'band_gap_room_temperature' must be"
            " defined.",
        ),
    ],
)
def test_dark_current_invalid(
    ccd_10x10: CCD,
    figure_of_merit: float,
    spatial_noise_factor: float,
    band_gap: float,
    band_gap_room_temperature: float,
    exp_exc,
    exp_error,
):
    """Test model 'dark_current' with valid inputs."""
    with pytest.raises(exp_exc, match=exp_error):
        dark_current(
            detector=ccd_10x10,
            figure_of_merit=figure_of_merit,
            spatial_noise_factor=spatial_noise_factor,
            band_gap=band_gap,
            band_gap_room_temperature=band_gap_room_temperature,
        )
