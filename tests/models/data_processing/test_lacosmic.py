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


def test_lacosmic():
    fits_file = "/Users/hans.smit/data/frame-Tint1.2s_GD12.5V_001.fits"
    data = fits.getdata(fits_file)
    data = data[0:1000, 0:1000].astype(float)
    fits_file = "/Users/hans.smit/data/lacosmic-test.fits"
    fits.writeto(filename=fits_file, data=data, clobber=True)
    cleaned_image, cr_mask = lacosmic.lacosmic(
        data,
        contrast=1.0,
        cr_threshold=50.0,
        neighbor_threshold=50.0,
        effective_gain=1.0,
        readnoise=1.0,
    )
    print(cleaned_image)
    print(cr_mask)
    fits_file = "/Users/hans.smit/data/lacosmic-test-cleaned.fits"
    fits.writeto(filename=fits_file, data=cleaned_image, clobber=True)


def test_lacosmic_simple():
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

    fits_file = "/Users/hans.smit/data/lacosmic-sample.fits"
    fits.writeto(filename=fits_file, data=data, clobber=True)

    # requests.get(url="http://localhost:9991/append", params={"file": fits_file},)
    cr_threshold = np.arange(0.0, 100.0, 10.0)
    cr = 2.0
    neighbor_threshold = np.arange(0.0, 100.0, 10.0)
    nt = 2.0
    effective_gain = np.arange(0.0, 5.0, 0.1)
    eg = 2.0
    # for c in contrast:
    # contrast = np.arange(0.0, 5.0, 0.5)
    c = 2.0
    for eg in effective_gain:
        cleaned_image, cr_mask = lacosmic.lacosmic(
            data,
            contrast=c,
            cr_threshold=cr,
            neighbor_threshold=nt,
            effective_gain=eg,
            readnoise=0.0,
        )
        fits_file = "/Users/hans.smit/data/lacosmic-sample-cleaned.fits"
        fits.writeto(filename=fits_file, data=cleaned_image, clobber=True)
        # requests.get(url="http://localhost:9991/append", params={"file": fits_file},)
