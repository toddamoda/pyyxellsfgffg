#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import pytest
import requests
import numpy as np
from astropy.io import fits
import lacosmic
from skimage.draw import line_aa, circle_perimeter_aa, disk

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
from pyxel.models.data_processing import remove_cosmic_rays


def create_image_with_cosmics():
    data = np.zeros(shape=(50, 50), dtype=float)

    rr, cc = disk((10, 30), 3, shape=None)
    data[rr, cc] = 200.0

    rr, cc = disk((30, 10), 5, shape=None)
    data[rr, cc] = 200.0

    # data[25, :] = 500.0
    data[24, :] = 500.0

    rr, cc, val = line_aa(1, 1, 8, 8)
    data[rr, cc] = val * 500.0

    rr, cc, val = line_aa(1, 28, 8, 21)
    data[rr, cc] = val * 300.0

    rr, cc, val = line_aa(25, 25, 26, 26)
    data[rr, cc] = val * 300.0

    rr, cc, val = circle_perimeter_aa(30, 30, 15)
    data[rr, cc] = val * 200.0

    rr, cc, val = line_aa(10, 10, 30, 30)
    data[rr, cc] = val * 100.0

    return data


@pytest.fixture
def ccd_50x50() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=50,
            col=50,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(num_steps=1)
    return detector


def test_lacosmic(ccd_50x50: CCD):
    """Test input parameters for function 'statistics'."""
    detector = ccd_50x50
    pixels = create_image_with_cosmics()  # 2d array
    detector.pixel.array = pixels
    remove_cosmic_rays(detector=detector)

    data = detector.data
    assert isinstance(data, DataTree)

    # TODO: assert that data is ok
    x = data[f"/lacosmic/cosmic_ray_clean"]
    # for name in ["cosmic_ray_mask", "cosmic_ray_clean"]:
    #     data_statistics = data[f"/statistics/{name}"]
    #     assert isinstance(data_statistics, DataTree)
    #
    #     assert "time" in data_statistics.coords
    #     assert list(data_statistics.coords["time"]) == [0.0]
    #
    #     dataset = data_statistics.to_dataset()
    #     assert isinstance(dataset, xr.Dataset)
    #
    #     assert "time" in dataset.coords
    #     assert list(dataset.coords["time"]) == [0.0]
    #
    # Old tests
    # dataset = detector.processed_data.data
    # assert "time" in dataset.coords
    # assert list(dataset.coords["time"].values) == [0.0]



#
# def test_lacosmic():
#     fits_file = "/Users/hans.smit/data/frame-Tint1.2s_GD12.5V_001.fits"
#     data = fits.getdata(fits_file)
#     data = data[0:1000, 0:1000].astype(float)
#     fits_file = "/Users/hans.smit/data/lacosmic-test.fits"
#     fits.writeto(filename=fits_file, data=data, clobber=True)
#     cleaned_image, cr_mask = lacosmic.lacosmic(
#         data,
#         contrast=1.0,
#         cr_threshold=50.0,
#         neighbor_threshold=50.0,
#         effective_gain=1.0,
#         readnoise=1.0,
#     )
#     print(cleaned_image)
#     print(cr_mask)
#     fits_file = "/Users/hans.smit/data/lacosmic-test-cleaned.fits"
#     fits.writeto(filename=fits_file, data=cleaned_image, clobber=True)
#
#
# def test_lacosmic_simple():
#     data = np.zeros(shape=(50, 50), dtype=float)
#
#     rr, cc = disk((10, 30), 3, shape=None)
#     data[rr, cc] = 200.0
#
#     rr, cc = disk((30, 10), 5, shape=None)
#     data[rr, cc] = 200.0
#
#     # data[25, :] = 500.0
#     data[24, :] = 500.0
#
#     rr, cc, val = line_aa(1, 1, 8, 8)
#     data[rr, cc] = val * 500.0
#
#     rr, cc, val = line_aa(1, 28, 8, 21)
#     data[rr, cc] = val * 300.0
#
#     rr, cc, val = line_aa(25, 25, 26, 26)
#     data[rr, cc] = val * 300.0
#
#     rr, cc, val = circle_perimeter_aa(30, 30, 15)
#     data[rr, cc] = val * 200.0
#
#     rr, cc, val = line_aa(10, 10, 30, 30)
#     data[rr, cc] = val * 100.0
#
#     fits_file = "/Users/hans.smit/data/lacosmic-sample.fits"
#     fits.writeto(filename=fits_file, data=data, clobber=True)
#
#     # requests.get(url="http://localhost:9991/append", params={"file": fits_file},)
#     cr_threshold = np.arange(0.0, 100.0, 10.0)
#     cr = 2.0
#     neighbor_threshold = np.arange(0.0, 100.0, 10.0)
#     nt = 2.0
#     effective_gain = np.arange(0.0, 5.0, 0.1)
#     eg = 2.0
#     # for c in contrast:
#     # contrast = np.arange(0.0, 5.0, 0.5)
#     c = 2.0
#     for eg in effective_gain:
#         cleaned_image, cr_mask = lacosmic.lacosmic(
#             data,
#             contrast=c,
#             cr_threshold=cr,
#             neighbor_threshold=nt,
#             effective_gain=eg,
#             readnoise=0.0,
#         )
#         fits_file = "/Users/hans.smit/data/lacosmic-sample-cleaned.fits"
#         fits.writeto(filename=fits_file, data=cleaned_image, clobber=True)
#         # requests.get(url="http://localhost:9991/append", params={"file": fits_file},)
