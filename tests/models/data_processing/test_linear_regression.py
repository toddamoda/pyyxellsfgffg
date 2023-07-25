#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.
import datatree.testing
import numpy as np
import pytest
import xarray as xr
from datatree import DataTree

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
    detector.set_readout(num_steps=3, start_time=0.0, end_time=3.0)
    return detector


# def test_raise_error():
#     """Test that error is raised when less than two times are given."""
#
#     with pytest.raises()


def test_linear_regression(ccd_10x10):
    """Test model 'linear_regression'."""

    # Create fake image for three different times
    rng = np.random.default_rng(seed=100)
    absolute_time = [0.0, 1.0, 2.0]
    image = xr.DataArray(
        rng.random((3, 4, 5)),
        dims=["time", "y", "x"],
        coords={"time": absolute_time, "y": range(4), "x": range(5)},
    )
    detector = ccd_10x10
    time_step_it = readout.time_step_it()
    for i, (time, step) in enumerate(time_step_it):
        detector.time = time
        detector.time_step = step
        detector.pipeline_count = i

        detector.image.array = rng.random((10, 10))
        linear_regression(detector, data_structure="image")

    data_array = detector.data["/linear_regression/image"]
    # convert to Dataset
    data_array = data_array.to_dataset()
    # TODO: Expand test for r2 variable.
    data_array = data_array.drop_vars("r2")
    computed_result = detector.data["image"].polyfit(
        dim="time", deg=1, full=True, cov=True
    )

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

    # check that both datasets are the same
    xr.testing.assert_allclose(data_array, expected)
