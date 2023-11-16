#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest

from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.data_processing import extract_roi_to_xarray


@pytest.mark.parametrize(
    "array_type,exp_warn",
    [
        ("pixel", "pixel data array is empty"),
        ("signal", "signal data array is empty"),
        ("image", "image data array is empty"),
        ("photon", "photon data array is empty"),
        ("charge", "charge data array is empty"),
    ],
)
def test_extract_roi_to_xarray_empty_array(ccd_10x10: CCD, array_type, exp_warn):
    """Tests empty array warning."""
    with pytest.warns(UserWarning, match=exp_warn):
        extract_roi_to_xarray(detector=ccd_10x10, array_type=array_type)


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


def test_extract_roi_to_xarray_pixel(ccd_10x10: CCD):
    ccd_10x10.pixel.array = np.full(fill_value=1, shape=(10, 10), dtype=float)
    extract_roi_to_xarray(detector=ccd_10x10, array_type="pixel")


def test_extract_roi_to_xarray_signal(ccd_10x10: CCD):
    ccd_10x10.signal.array = np.full(fill_value=1, shape=(10, 10), dtype=float)
    extract_roi_to_xarray(detector=ccd_10x10, array_type="signal")


def test_extract_roi_to_xarray_image(ccd_10x10: CCD):
    ccd_10x10.image.array = np.full(fill_value=1, shape=(10, 10), dtype=np.uint64)
    extract_roi_to_xarray(detector=ccd_10x10, array_type="image")


def test_extract_roi_to_xarray_photon(ccd_10x10: CCD):
    ccd_10x10.photon.array = np.full(fill_value=1, shape=(10, 10), dtype=float)
    extract_roi_to_xarray(detector=ccd_10x10, array_type="photon")


def test_extract_roi_to_xarray_charge(ccd_10x10: CCD):
    ccd_10x10.charge.add_charge_array(
        np.full(fill_value=1, shape=(10, 10), dtype=float)
    )
    extract_roi_to_xarray(detector=ccd_10x10, array_type="charge")


#     #assert np.any(ccd_10x10.pixel.array != 0)
#     """Test to ensure warning isn't triggered for filled array"""


def test_extract_roi_to_xarray_incorrect_array_type(ccd_10x10: CCD, array_type="test"):
    ccd_10x10.pixel.array = np.random.rand(10, 10)
    """Test to ensure warning isn't triggered for filled array"""

    with pytest.raises(ValueError, match=r"Incorrect array_type\. Must be one of"):
        extract_roi_to_xarray(ccd_10x10, array_type="test")
