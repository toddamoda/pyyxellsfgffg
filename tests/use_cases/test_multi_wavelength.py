#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import pytest
import xarray as xr

import pyxel


@pytest.fixture
def folder_parent(request: pytest.FixtureRequest) -> Path:
    """Get the folder 'tests'."""
    folder: Path = request.path.parent
    return folder.resolve(strict=True)


@pytest.mark.functional_test
def test_multi_wavelength(folder_parent: Path, tmp_path: Path):
    """Test multi-wavelength capability."""
    config_filename = folder_parent / "multi_wavelength.yaml"
    assert config_filename.exists()

    output_folder = tmp_path / "output"
    assert not output_folder.exists()

    cfg = pyxel.load(config_filename)
    data_tree = pyxel.run_mode(
        mode=cfg.running_mode,
        detector=cfg.detector,
        pipeline=cfg.pipeline,
        with_inherited_coords=True,
        override_dct={"exposure.outputs.output_folder": output_folder},
    )

    assert isinstance(data_tree, xr.DataTree)
    assert output_folder.exists()
