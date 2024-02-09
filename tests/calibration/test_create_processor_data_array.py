#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import numpy as np
import pytest
import xarray as xr
from astropy.io import fits

from pyxel.calibration import create_processor_data_array


@pytest.fixture
def folder_files(tmp_path: Path):
    """Create dummy files."""

    np.save(file=tmp_path / "data00.npy", arr=np.zeros(shape=(10, 2)))
    np.save(file=tmp_path / "data01.npy", arr=np.full(shape=(10, 2), fill_value=1.0))
    np.save(file=tmp_path / "data02.npy", arr=np.full(shape=(10, 2), fill_value=2.0))
    np.save(file=tmp_path / "data03.npy", arr=np.full(shape=(10, 2), fill_value=3.0))
    fits.writeto(
        filename=tmp_path / "data04.fits", data=np.full(shape=(10, 2), fill_value=4.0)
    )

    return tmp_path


def test_create_processor_data_array(folder_files: Path):
    """Test function 'create_processor_data_array'."""
    filenames = [
        folder_files / "data00.npy",
        folder_files / "data01.npy",
        folder_files / "data02.npy",
        folder_files / "data03.npy",
        folder_files / "data04.fits",
    ]

    result = create_processor_data_array(filenames)
    exp_result = xr.DataArray(
        np.broadcast_to(
            np.array([0, 1, 2, 3, 4], dtype=float).reshape((5, 1, 1)), shape=(5, 10, 2)
        ),
        dims=["processor", "y", "x"],
        coords={"processor": range(5), "y": range(10), "x": range(2)},
        attrs={"filenames": list(map(str, filenames))},
    )

    xr.testing.assert_identical(result, exp_result)
