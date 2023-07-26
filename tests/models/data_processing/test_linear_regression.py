#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
import statsmodels.api as s
import xarray as xr

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.data_processing import linear_regression


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
    detector.set_readout(num_steps=3, start_time=1.0, end_time=4.0)

    return detector


def test_raise_error():
    """Test that error is raised when less than two times are given."""

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
    detector.set_readout(num_steps=2, start_time=1.0, end_time=4.0)

    with pytest.raises(ValueError, match="Expecting at least 3 steps"):
        linear_regression(detector=detector)


@pytest.fixture
def image_3d():
    """Create fake image for three different times."""

    rng = np.random.default_rng(seed=100)
    absolute_time = [1.0, 2.0, 3.0]
    image = xr.DataArray(
        rng.random((3, 10, 10)),
        dims=["time", "y", "x"],
        coords={"time": absolute_time, "y": range(10), "x": range(10)},
    )
    return image


@pytest.fixture
def expected_result(image_3d):
    """Create expected result."""
    computed_result = image_3d.polyfit(dim="time", deg=1, full=True, cov=True)

    # create expected Dataset
    expected = xr.Dataset()
    expected["slope"] = computed_result["polyfit_coefficients"].isel(degree=0)
    expected["intercept"] = computed_result["polyfit_coefficients"].isel(degree=1)
    # expected["r2"]=computed_result["polyfit_residuals"]
    expected["slope_std"] = np.sqrt(
        computed_result["polyfit_covariance"].sel(cov_i=0, cov_j=0)
    )
    expected["intercept_std"] = np.sqrt(
        computed_result["polyfit_covariance"].sel(cov_i=1, cov_j=1)
    )
    del expected["degree"]

    return expected


def test_linear_regression(
    ccd_10x10: CCD, image_3d: np.ndarray, expected_result: xr.Dataset
):
    """Test model 'linear_regression'."""

    detector = ccd_10x10
    image = image_3d
    steps = [1.0, 1.0, 1.0]
    absolute_time = image_3d.time.to_numpy()

    model = s.OLS(
        endog=image_3d.isel(x=0, y=0).to_numpy(), exog=s.add_constant(absolute_time)
    )
    results = model.fit()

    for i, (time, step) in enumerate(zip(absolute_time, steps)):
        detector.time = time
        detector.time_step = step
        detector.pipeline_count = i

        detector.image.array = image.isel(time=i).to_numpy()
        linear_regression(detector=detector, data_structure="image")

    data_array = detector.data["/linear_regression/image"]
    # convert to Dataset
    data_array = data_array.to_dataset()
    # TODO: Expand test for r2 variable.
    data_array = data_array.drop_vars("r2")

    # check that both datasets are the same
    xr.testing.assert_allclose(data_array, expected_result)
