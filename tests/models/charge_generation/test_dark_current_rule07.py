#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Tests for dark current models."""

import numpy as np
import pytest

from pyxel.detectors import (
    CCD,
    CMOS,
    MKID,
    CCDGeometry,
    Characteristics,
    CMOSGeometry,
    Environment,
    MKIDGeometry,
    ReadoutProperties,
)
from pyxel.models.charge_generation import dark_current_rule07


@pytest.fixture(params=["ccd", "cmos"])
def detector_4x3(request: pytest.FixtureRequest) -> CCD | CMOS:
    """Create a valid CCD or CMOS detector."""
    if request.param == "cmos":
        detector = CMOS(
            geometry=CMOSGeometry(
                row=4,
                col=3,
                total_thickness=40.0,
                pixel_vert_size=10.0,
                pixel_horz_size=10.0,
            ),
            environment=Environment(temperature=273.15),
            characteristics=Characteristics(),
        )

    elif request.param == "ccd":
        detector = CCD(
            geometry=CCDGeometry(
                row=4,
                col=3,
                total_thickness=40.0,
                pixel_vert_size=10.0,
                pixel_horz_size=10.0,
            ),
            environment=Environment(temperature=273.15),
            characteristics=Characteristics(),
        )

    else:
        raise NotImplementedError

    detector._readout_properties = ReadoutProperties(times=[0.1])
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
    detector_4x3: CCD | CMOS,
    cutoff_wavelength: float | None,
    spatial_noise_factor: float | None,
    temporal_noise: bool,
):
    """Test model 'dark_current_rule07' with valid inputs."""
    detector = detector_4x3

    if cutoff_wavelength is None:
        dark_current_rule07(
            detector=detector,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
            seed=123456,
        )

        exp_array = np.array(
            [
                [73984001.0, 73987171.0, 73989033.0],
                [73978696.0, 73987076.0, 73979049.0],
                [73999108.0, 73983027.0, 73992523.0],
                [74000480.0, 73979893.0, 73992006.0],
            ]
        )

        charge_arrays = detector.charge.array
        np.testing.assert_allclose(charge_arrays, exp_array)
    else:
        dark_current_rule07(
            detector=detector,
            cutoff_wavelength=cutoff_wavelength,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
            seed=123456,
        )

        if temporal_noise:
            exp_array = np.array(
                [
                    [82360.0, np.inf, np.inf],
                    [np.inf, 82463.0, 82194.0],
                    [82865.0, 82327.0, 82645.0],
                    [np.inf, np.inf, 82627.0],
                ]
            )
        else:
            exp_array = np.array(
                [
                    [8.88795759e14, 8.88795759e14, 8.88795759e14],
                    [8.88795759e14, 8.88795759e14, 8.88795759e14],
                    [8.88795759e14, 8.88795759e14, 8.88795759e14],
                    [8.88795759e14, 8.88795759e14, 8.88795759e14],
                ]
            )

        charge_arrays = detector.charge.array
        np.testing.assert_allclose(charge_arrays, exp_array)


@pytest.mark.parametrize(
    "cutoff_wavelength, exp_exc, exp_msg",
    [
        (1.69, ValueError, r"'cutoff' must be between 1.7 and 15.0"),
        (15.01, ValueError, r"'cutoff' must be between 1.7 and 15.0"),
    ],
)
def test_dark_current_rule07_invalid(
    detector_4x3: CCD | CMOS,
    cutoff_wavelength,
    exp_exc,
    exp_msg,
):
    """Test model 'dark_current_rule07' with invalid inputs."""
    with pytest.raises(exp_exc, match=exp_msg):
        dark_current_rule07(
            detector=detector_4x3,
            cutoff_wavelength=cutoff_wavelength,
        )


def test_dark_current_rule07_invalid_detector():
    """Test model 'dark_current_rule07' with an invalid detector."""
    detector = MKID(
        geometry=MKIDGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )

    with pytest.raises(TypeError, match="Expecting a CCD or CMOS object for detector"):
        dark_current_rule07(detector=detector)
