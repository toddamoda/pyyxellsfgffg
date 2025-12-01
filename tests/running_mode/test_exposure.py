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
def test_exposure(folder_data: Path, with_debug: bool, tmp_path: Path):
    """Run 'exposure' mode."""
    filename = folder_data / "data/exposure.yaml"
    assert filename.exists()

    config = pyxel.load(filename)
    config.running_mode.outputs.output_folder = tmp_path

    data_tree = pyxel.run_mode(config, debug=with_debug)

    exp_bucket = xr.Dataset(
        {
            "photon": xr.DataArray(
                [
                    [
                        [933837.890625, 933837.890625, 933837.890625],
                        [933837.890625, 933837.890625, 933837.890625],
                    ],
                    [
                        [933837.890625, 933837.890625, 933837.890625],
                        [933837.890625, 933837.890625, 933837.890625],
                    ],
                    [
                        [933837.890625, 933837.890625, 933837.890625],
                        [933837.890625, 933837.890625, 933837.890625],
                    ],
                ],
                dims=["time", "y", "x"],
            ),
            "charge": xr.DataArray(
                [
                    [[747037.0, 746938.0, 747990.0], [746784.0, 747046.0, 747151.0]],
                    [[747290.0, 747972.0, 746957.0], [746822.0, 747194.0, 747716.0]],
                    [[746675.0, 746964.0, 746447.0], [747387.0, 747455.0, 747044.0]],
                ],
                dims=["time", "y", "x"],
            ),
            "pixel": xr.DataArray(
                [
                    [[80000.0, 80000.0, 80000.0], [80000.0, 80000.0, 80000.0]],
                    [[80000.0, 80000.0, 80000.0], [80000.0, 80000.0, 80000.0]],
                    [[80000.0, 80000.0, 80000.0], [80000.0, 80000.0, 80000.0]],
                ],
                dims=["time", "y", "x"],
            ),
            "signal": xr.DataArray(
                [
                    [[0.32, 0.32, 0.32], [0.32, 0.32, 0.32]],
                    [[0.32, 0.32, 0.32], [0.32, 0.32, 0.32]],
                    [[0.32, 0.32, 0.32], [0.32, 0.32, 0.32]],
                ],
                dims=["time", "y", "x"],
            ),
            "image": xr.DataArray(
                np.array(
                    [
                        [[6990, 6990, 6990], [6990, 6990, 6990]],
                        [[6990, 6990, 6990], [6990, 6990, 6990]],
                        [[6990, 6990, 6990], [6990, 6990, 6990]],
                    ],
                    dtype=np.uint16,
                ),
                dims=["time", "y", "x"],
            ),
        },
        coords={"time": [1.0, 2.0, 3.0], "y": [0, 1], "x": [0, 1, 2]},
    )
    xr.testing.assert_allclose(data_tree["/bucket"].to_dataset(), exp_bucket)

    bucket = data_tree["/bucket"].to_dataset()
    xr.testing.assert_allclose(bucket, exp_bucket)
