#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import datatree.testing
import numpy as np
import xarray as xr
from datatree import DataTree

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.data_processing import mean_variance


def test_mean_variance():
    """Test model 'mean_variance'."""
    # Create fake photons for three different times
    rng = np.random.default_rng(seed=100)

    absolute_time = [0.0, 1.0, 2.0]
    photons = xr.DataArray(
        rng.random((3, 4, 5)),
        dims=["time", "y", "x"],
        coords={"time": absolute_time, "y": range(4), "x": range(5)},
    )

    # Created expected 'mean-variance'
    expected_variance = photons.var(dim=["y", "x"])
    expected_mean = photons.mean(dim=["y", "x"])

    expected_mean_variance = xr.Dataset()
    expected_mean_variance["variance"] = xr.DataArray(
        expected_variance.to_numpy(),
        dims=["mean"],
        coords={"mean": expected_mean.to_numpy()},
    )

    # Create fake CCD detector
    detector = CCD(
        geometry=CCDGeometry(row=4, col=5),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector.set_readout(times=[1.0, 2.0, 3.0])

    # Step 1
    detector.photon.array = photons.isel(time=0).to_numpy()
    mean_variance(detector, data_structure="photon")

    expected_photon_step1 = DataTree().from_dict(
        {"mean_variance/partial/photon": expected_mean_variance.isel(mean=[0])}
    )
    datatree.testing.assert_equal(detector.data, expected_photon_step1)

    # Step 2
    detector.photon.array = photons.isel(time=1).to_numpy()
    mean_variance(detector, data_structure="photon")

    expected_photon_step2 = DataTree().from_dict(
        {"mean_variance/partial/photon": expected_mean_variance.isel(mean=[1, 0])}
    )
    datatree.testing.assert_equal(detector.data, expected_photon_step2)

    # Step 3
    detector.photon.array = photons.isel(time=2).to_numpy()
    mean_variance(detector, data_structure="photon")

    expected_photon_step3 = DataTree().from_dict(
        {"mean_variance/partial/photon": expected_mean_variance.isel(mean=[2, 1, 0])}
    )
    datatree.testing.assert_equal(detector.data, expected_photon_step3)
