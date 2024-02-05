#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

import pyxel
from pyxel import Configuration
from pyxel.exposure import Exposure


@contextmanager
def chdir(folder: Path):
    current_folder = Path().resolve()

    try:
        os.chdir(folder)
        yield
    finally:
        os.chdir(current_folder)


@pytest.fixture
def valid_simple_config_filename(request: pytest.FixtureRequest) -> Path:
    """Get a valid existing YAML filename."""
    filename: Path = request.path.parent / "data/simple_exposure.yaml"
    return filename.resolve(strict=True)


def test_exposure_output(valid_simple_config_filename: Path, tmp_path: Path):
    """Test simple mode with different outputs."""
    zone = ZoneInfo("Europe/Amsterdam")
    date_2023_12_18_08_20 = datetime(
        year=2023, month=12, day=18, hour=8, minute=20, tzinfo=zone
    )
    date_2023_12_19_08_20 = datetime(
        year=2023, month=12, day=19, hour=8, minute=20, tzinfo=zone
    )
    date_2023_12_19_08_30 = datetime(
        year=2023, month=12, day=19, hour=8, minute=30, tzinfo=zone
    )
    date_2023_12_19_08_40 = datetime(
        year=2023, month=12, day=19, hour=8, minute=40, tzinfo=zone
    )

    # Change the current directory
    with chdir(tmp_path):

        # Check that 'tmp_path' is empty
        assert list(tmp_path.glob("*")) == []

        # Load YAML configuration file
        with freeze_time(date_2023_12_18_08_20):
            config = pyxel.load(valid_simple_config_filename)

        assert isinstance(config, Configuration)
        mode = config.running_mode
        detector = config.detector
        pipeline = config.pipeline

        # Check that 'tmp_path' is still empty
        assert list(tmp_path.glob("*")) == []

        # Check 'mode.output.output_dir'
        with pytest.raises(RuntimeError):
            _ = mode.outputs.current_output_folder

        #
        # First run
        #
        assert isinstance(mode, Exposure)
        with freeze_time(date_2023_12_19_08_20):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if an empty 'output' folder is created
        folder_output_01 = tmp_path / "output"
        assert folder_output_01.exists()
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }
        assert filenames_output == {Path("output/run_20231219_082000")}

        folder_run_01 = folder_output_01 / "run_20231219_082000"
        assert folder_run_01.exists()
        assert list(folder_run_01.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_01

        #
        # Second run - same time
        #
        with freeze_time(date_2023_12_19_08_20):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }
        assert filenames_output == {
            Path("output/run_20231219_082000"),
            Path("output/run_20231219_082000_1"),
        }

        folder_run_02 = folder_output_01 / "run_20231219_082000_1"
        assert folder_run_02.exists()
        assert list(folder_run_02.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_02

        #
        # Third run - different time
        #
        with freeze_time(date_2023_12_19_08_30):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }
        assert filenames_output == {
            Path("output/run_20231219_082000"),
            Path("output/run_20231219_082000_1"),
            Path("output/run_20231219_083000"),
        }

        folder_run_03 = folder_output_01 / "run_20231219_083000"
        assert folder_run_03.exists()
        assert list(folder_run_03.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_03

        #
        # Fourth run - change 'custom_dir_name'
        #
        mode.outputs.custom_dir_name = "foo_"
        with freeze_time(date_2023_12_19_08_30):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }
        assert filenames_output == {
            Path("output/run_20231219_082000"),
            Path("output/run_20231219_082000_1"),
            Path("output/run_20231219_083000"),
            Path("output/foo_20231219_083000"),
        }
        folder_run_04 = folder_output_01 / "foo_20231219_083000"
        assert folder_run_04.exists()
        assert list(folder_run_04.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_04

        #
        # Fifth run - same 'custom_dir_name', same time
        #
        with freeze_time(date_2023_12_19_08_30):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }
        assert filenames_output == {
            Path("output/run_20231219_082000"),
            Path("output/run_20231219_082000_1"),
            Path("output/run_20231219_083000"),
            Path("output/foo_20231219_083000"),
            Path("output/foo_20231219_083000_1"),
        }
        folder_run_05 = folder_output_01 / "foo_20231219_083000_1"
        assert folder_run_05.exists()
        assert list(folder_run_05.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_05

        #
        # Sixth run - change 'output_folder'
        #
        mode.outputs.output_folder = "folder1/folder2"
        folder_output_02 = tmp_path / "folder1/folder2"
        assert not folder_output_02.exists()

        with freeze_time(date_2023_12_19_08_40):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        assert folder_output_02.exists()

        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_02.glob("*")
        }
        assert filenames_output == {Path("folder1/folder2/foo_20231219_084000")}
        folder_run_06 = folder_output_02 / "foo_20231219_084000"
        assert folder_run_06.exists()
        assert list(folder_run_06.glob("*")) != []

        # Check 'mode.output.output_dir'
        output_dir = mode.outputs.current_output_folder
        assert output_dir == folder_run_06
