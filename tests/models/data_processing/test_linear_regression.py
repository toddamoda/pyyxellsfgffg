#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.


import numpy as np
import pytest
import statsmodels.api as sm
import xarray as xr

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
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
    detector.set_readout(times=[1.0, 2.0, 3.0])

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
    detector.set_readout(times=[1.0])

    with pytest.raises(ValueError, match="Expecting at least 2 steps"):
        linear_regression(detector=detector)


@pytest.fixture
def image_3d() -> xr.DataArray:
    """Create fake image for three different times."""

    rng = np.random.default_rng(seed=100)
    relative_time = [1.0, 2.0, 3.0]
    image = xr.DataArray(
        rng.integers(low=0, high=65535, size=(3, 10, 10), dtype=np.uint64),
        dims=["time", "y", "x"],
        coords={"time": relative_time, "y": range(10), "x": range(10)},
    )
    return image


@pytest.fixture
def expected_result(image_3d: xr.DataArray) -> xr.Dataset:
    """Compute expected result with 'statsmodels'."""

    def compute_linear_regression(
        y: np.ndarray, x: np.ndarray
    ) -> tuple[float, float, float, float, float]:
        model = sm.OLS(endog=y, exog=sm.add_constant(x))
        results = model.fit()

        intercept, slope = results.params
        r2 = results.rsquared
        intercept_std, slope_std = results.bse

        return intercept, slope, r2, intercept_std, slope_std

    all_results = xr.apply_ufunc(
        compute_linear_regression,
        image_3d,
        image_3d["time"],
        input_core_dims=[["time"], ["time"]],
        output_core_dims=[[], [], [], [], []],
        vectorize=True,
    )
    intercept, slope, r2, intercept_std, slope_std = all_results

    ds = xr.Dataset()
    ds["intercept"] = intercept
    ds["slope"] = slope
    ds["r2"] = r2
    ds["intercept_std"] = intercept_std
    ds["slope_std"] = slope_std

    return ds


def test_linear_regression(
    ccd_10x10: CCD,
    image_3d: xr.DataArray,
    expected_result: xr.Dataset,
):
    """Test model 'linear_regression'."""

    detector = ccd_10x10
    steps = detector.readout_properties.steps
    absolute_time = detector.readout_properties.times

    for i, (time, step) in enumerate(zip(absolute_time, steps)):
        detector.time = time
        detector.time_step = step
        detector.pipeline_count = i

        detector.image.array = image_3d.isel(time=i).to_numpy()
        linear_regression(detector=detector, data_structure="image")

    dataset = detector.data["/linear_regression/image"].to_dataset()

    # check that both datasets are the same
    xr.testing.assert_allclose(dataset, expected_result)
