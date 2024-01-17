#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

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
from pyxel.models.data_processing import signal_to_noise_ratio


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
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.pixel.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.photon.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.image.array = np.zeros(detector.geometry.shape, dtype=np.uint64)
    detector._readout_properties = ReadoutProperties(times=[1.0])
    return detector


def test_snr_input(ccd_10x10: CCD):
    """Test input parameters for function 'signal_to_noise_ratio'."""
    detector = ccd_10x10
    signal_to_noise_ratio(detector=detector, data_structure="all")

    data = detector.data
    assert isinstance(data, DataTree)

    for name in ["pixel", "photon", "signal", "image"]:
        data_snr = data[f"/snr/{name}"]
        assert isinstance(data_snr, DataTree)

        assert "time" in data_snr.coords
        assert list(data_snr.coords["time"]) == [0.0]

        dataset = data_snr.to_dataset()
        assert isinstance(dataset, xr.Dataset)

        assert "time" in dataset.coords
        assert list(dataset.coords["time"]) == [0.0]
