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

import pyxel


@pytest.fixture
def folder_data(request: pytest.FixtureRequest) -> Path:
    """Get the folder 'tests'."""
    folder = Path(request.module.__file__).parent
    return folder.resolve(strict=True)


@pytest.mark.parametrize("with_debug", [False, True])
def test_exposure(folder_data: Path, with_debug: bool):
    """Run 'exposure' mode."""
    filename = folder_data / "data/exposure.yaml"
    assert filename.exists()

    config = pyxel.load(filename)

    data_tree = pyxel.run_mode(config, debug=with_debug)

    exp_bucket = xr.Dataset(
        {
            "photon": xr.DataArray(
                [
                    [[48637.39, 48637.39, 48637.39], [48637.39, 48637.39, 48637.39]],
                    [[48637.39, 48637.39, 48637.39], [48637.39, 48637.39, 48637.39]],
                    [[48637.39, 48637.39, 48637.39], [48637.39, 48637.39, 48637.39]],
                ],
                dims=["time", "y", "x"],
            ),
            "charge": xr.DataArray(
                [
                    [[38902.0, 38880.0, 39117.0], [38845.0, 38904.0, 38928.0]],
                    [[38959.0, 39113.0, 38884.0], [38854.0, 38937.0, 39026.0]],
                    [[39055.0, 38817.0, 38886.0], [38769.0, 38975.0, 38990.0]],
                ],
                dims=["time", "y", "x"],
            ),
            "pixel": xr.DataArray(
                [
                    [[38902.0, 38880.0, 39117.0], [38845.0, 38904.0, 38928.0]],
                    [[77861.0, 77993.0, 78001.0], [77699.0, 77841.0, 77954.0]],
                    [[100000.0, 100000.0, 100000.0], [100000.0, 100000.0, 100000.0]],
                ],
                dims=["time", "y", "x"],
            ),
            "signal": xr.DataArray(
                [
                    [[3.8902, 3.888, 3.9117], [3.8845, 3.8904, 3.8928]],
                    [[7.7861, 7.7993, 7.8001], [7.7699, 7.7841, 7.7954]],
                    [[10.0, 10.0, 10.0], [10.0, 10.0, 10.0]],
                ],
                dims=["time", "y", "x"],
            ),
            "image": xr.DataArray(
                np.array(
                    [
                        [[25494, 25480, 25635], [25457, 25495, 25511]],
                        [[51026, 51112, 51117], [50920, 51013, 51087]],
                        [[65535, 65535, 65535], [65535, 65535, 65535]],
                    ],
                    dtype=np.uint16,
                ),
                dims=["time", "y", "x"],
            ),
        },
        coords={"time": [1.0, 2.0, 3.0], "y": [0, 1], "x": [0, 1, 2]},
    )
    xr.testing.assert_allclose(data_tree["/bucket"].to_dataset(), exp_bucket)
