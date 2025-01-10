#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

import pyxel
from pyxel.exposure import Exposure


@pytest.fixture
def current_folder(request: pytest.FixtureRequest) -> Path:
    previous_folder = Path().cwd()

    new_folder: Path = request.path.parent / Path("config")
    assert new_folder.exists()

    os.chdir(new_folder)
    yield new_folder

    os.chdir(previous_folder)


@pytest.mark.parametrize(
    "config_filename",
    [
        # Without a working directory
        "exposure.yaml",
        "observation_product.yaml",
        "observation_sequential.yaml",
        "observation_custom.yaml",
        "calibration.yaml",
        # With a working directory
        "exposure_with_working_directory.yaml",
        "observation_product_with_working_directory.yaml",
        "observation_sequential_with_working_directory.yaml",
        "observation_custom_with_working_directory.yaml",
        "calibration_with_working_directory.yaml",
    ],
)
def test_exposure(config_filename: str, current_folder: Path, tmp_path: Path):
    """Test exposure mode."""
    config_full_path: Path = current_folder / config_filename
    assert config_full_path.exists()

    if "calibration" in config_filename:
        # Skip this test if 'pygmo' is not installed
        _ = pytest.importorskip("pygmo", reason="Pygmo is not installed")

    cfg = pyxel.load(config_full_path)

    current_date = datetime(
        year=2024, month=7, day=3, hour=8, minute=20, tzinfo=ZoneInfo("Europe/Paris")
    )
    output_folder: Path = tmp_path / "output"
    assert not output_folder.exists()

    mode = cfg.running_mode
    mode.outputs.output_folder = output_folder

    with freeze_time(current_date):
        result = pyxel.run_mode(
            mode=cfg.running_mode,
            detector=cfg.detector,
            pipeline=cfg.pipeline,
        )

    assert result is not None

    # Check output folder
    current_output_folder: Path = output_folder / "run_20240703_062000"
    assert current_output_folder.exists()

    if isinstance(cfg.running_mode, Exposure):
        output_dataset = current_output_folder / "dataset.nc"
        assert not output_dataset.exists()  # TODO: Fix this


def test_observation_bad_parameter(current_folder: Path):
    """Test function 'run_mode' with a Observation configuration file and bad parameters."""
    config_filename = current_folder / "observation_bad_parameter.yaml"
    assert config_filename.exists()

    config = pyxel.load(config_filename)

    with pytest.raises(KeyError, match=r"Cannot access Observation parameter"):
        _ = pyxel.run_mode(
            mode=config.running_mode,
            detector=config.detector,
            pipeline=config.pipeline,
        )
