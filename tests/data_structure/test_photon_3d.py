#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest
import xarray as xr

from pyxel.data_structure import Photon3d


@pytest.mark.parametrize("dtype", [float, np.float16, np.float32])
def test_photon3d_valid(dtype):
    """Test class 'Photon3D'."""

    data_3d = xr.DataArray(
        np.array(
            [
                [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]],
                [[12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]],
            ],
            dtype=dtype,
        ),
        dims=["wavelength", "y", "x"],
    )

    _ = Photon3d(data_3d)


def test_photon3d_bad_ndim():
    """Test class 'Photon3D' with a non-3D image"""
    data_2d = xr.DataArray(
        np.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]], dtype=float),
        dims=["wavelength", "y", "x"],
    )

    _ = Photon3d(data_2d)


@pytest.mark.parametrize("dtype", [int, np.uint32, np.uint64, np.int32, np.int64])
def test_photon3d_bad_dtype(dtype):
    """Test class 'Photon3D'."""

    data_3d = xr.DataArray(
        np.array(
            [
                [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]],
                [[12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]],
            ],
            dtype=float,
        ),
        dims=["wavelength", "y", "x"],
    )

    _ = Photon3d(data_3d)
