#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
import sys
from datetime import datetime
from pathlib import Path

import pytest

import pyxel
from pyxel import Configuration

if sys.version_info < (3, 11):
    from contextlib import contextmanager

    @contextmanager
    def chdir(folder: Path):
        current_folder = Path.cwd()

        try:
            os.chdir(folder)
            yield
        finally:
            os.chdir(current_folder)

else:
    from contextlib import chdir

# This is equivalent to 'import freezegun'
freezegun = pytest.importorskip(
    "freezegun",
    reason="Package 'freezegun' is not installed. Use 'pip install freezegun'",
)


@pytest.fixture
def folder_parent(request: pytest.FixtureRequest) -> Path:
    """Get a valid existing YAML filename."""
    return request.path.parent


@pytest.mark.parametrize(
    "config_filename, with_outputs",
    [
        ("data/simple_exposure.yaml", True),
        ("data/simple_exposure_no_outputs.yaml", False),
        ("data/simple_observation.yaml", True),
        ("data/simple_observation_no_outputs.yaml", False),
    ],
)
def test_exposure_output(  # noqa: C901
    config_filename: str, with_outputs: bool, folder_parent: Path, tmp_path: Path
):
    """Test simple mode with different outputs."""
    full_config_filename = folder_parent.joinpath(config_filename).resolve(strict=True)

    date_2023_12_18_08_20 = datetime(year=2023, month=12, day=18, hour=8, minute=20)
    date_2023_12_19_08_20 = datetime(year=2023, month=12, day=19, hour=8, minute=20)
    date_2023_12_19_08_30 = datetime(year=2023, month=12, day=19, hour=8, minute=30)
    date_2023_12_19_08_40 = datetime(year=2023, month=12, day=19, hour=8, minute=40)

    # Change the current directory
    with chdir(tmp_path):
        # Check that 'tmp_path' is empty
        assert list(tmp_path.glob("*")) == []

        # Load YAML configuration file
        with freezegun.freeze_time(date_2023_12_18_08_20):
            config = pyxel.load(full_config_filename)

        assert isinstance(config, Configuration)
        mode = config.running_mode
        detector = config.detector
        pipeline = config.pipeline

        # Check that 'tmp_path' is still empty
        assert list(tmp_path.glob("*")) == []

        # Check 'mode.output.output_dir'
        if with_outputs:
            with pytest.raises(RuntimeError):
                _ = mode.outputs.current_output_folder
        else:
            assert mode.outputs is None

        #
        # First run
        #
        with freezegun.freeze_time(date_2023_12_19_08_20):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if an empty 'output' folder is created
        folder_output_01 = tmp_path / "output"

        if with_outputs:
            assert folder_output_01.exists()
            filenames_output: set[Path] = {
                filename.relative_to(tmp_path)
                for filename in folder_output_01.glob("*")
            }
            assert filenames_output == {Path("output/run_20231219_082000")}

            folder_run_01 = folder_output_01 / "run_20231219_082000"
            assert folder_run_01.exists()
            assert list(folder_run_01.glob("*")) != []

        else:
            assert not folder_output_01.exists()

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_01
        else:
            assert mode.outputs is None

        #
        # Second run - same time
        #
        with freezegun.freeze_time(date_2023_12_19_08_20):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        if with_outputs:
            # Check if the folders in 'output'
            filenames_output: set[Path] = {
                filename.relative_to(tmp_path)
                for filename in folder_output_01.glob("*")
            }
            assert filenames_output == {
                Path("output/run_20231219_082000"),
                Path("output/run_20231219_082000_1"),
            }

        folder_run_02 = folder_output_01 / "run_20231219_082000_1"

        if with_outputs:
            assert folder_run_02.exists()
            assert list(folder_run_02.glob("*")) != []
        else:
            assert not folder_run_02.exists()

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_02
        else:
            assert mode.outputs is None

        #
        # Third run - different time
        #
        with freezegun.freeze_time(date_2023_12_19_08_30):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }

        if with_outputs:
            assert filenames_output == {
                Path("output/run_20231219_082000"),
                Path("output/run_20231219_082000_1"),
                Path("output/run_20231219_083000"),
            }
        else:
            assert filenames_output == set()

        folder_run_03 = folder_output_01 / "run_20231219_083000"

        if with_outputs:
            assert folder_run_03.exists()
            assert list(folder_run_03.glob("*")) != []

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_03
        else:
            assert mode.outputs is None

        #
        # Fourth run - change 'custom_dir_name'
        #
        if with_outputs:
            mode.outputs.custom_dir_name = "foo_"
            with freezegun.freeze_time(date_2023_12_19_08_30):
                _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }

        if with_outputs:
            assert filenames_output == {
                Path("output/run_20231219_082000"),
                Path("output/run_20231219_082000_1"),
                Path("output/run_20231219_083000"),
                Path("output/foo_20231219_083000"),
            }
            folder_run_04 = folder_output_01 / "foo_20231219_083000"
            assert folder_run_04.exists()

        if with_outputs:
            assert list(folder_run_04.glob("*")) != []

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_04
        else:
            assert mode.outputs is None

        #
        # Fifth run - same 'custom_dir_name', same time
        #
        with freezegun.freeze_time(date_2023_12_19_08_30):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        filenames_output: set[Path] = {
            filename.relative_to(tmp_path) for filename in folder_output_01.glob("*")
        }

        if with_outputs:
            assert filenames_output == {
                Path("output/run_20231219_082000"),
                Path("output/run_20231219_082000_1"),
                Path("output/run_20231219_083000"),
                Path("output/foo_20231219_083000"),
                Path("output/foo_20231219_083000_1"),
            }

        folder_run_05 = folder_output_01 / "foo_20231219_083000_1"
        if with_outputs:
            assert folder_run_05.exists()
        else:
            assert not folder_run_05.exists()

        if with_outputs:
            assert list(folder_run_05.glob("*")) != []
        else:
            assert list(folder_run_05.glob("*")) == []

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_05
        else:
            assert mode.outputs is None

        #
        # Sixth run - change 'output_folder'
        #
        if with_outputs:
            mode.outputs.output_folder = "folder1/folder2"
            folder_output_02 = tmp_path / "folder1/folder2"
            assert not folder_output_02.exists()

        with freezegun.freeze_time(date_2023_12_19_08_40):
            _ = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)

        # Check if the folders in 'output'
        if with_outputs:
            assert folder_output_02.exists()

            filenames_output: set[Path] = {
                filename.relative_to(tmp_path)
                for filename in folder_output_02.glob("*")
            }
            assert filenames_output == {Path("folder1/folder2/foo_20231219_084000")}
            folder_run_06 = folder_output_02 / "foo_20231219_084000"
            assert folder_run_06.exists()

        if with_outputs:
            assert list(folder_run_06.glob("*")) != []

        # Check 'mode.output.output_dir'
        if with_outputs:
            output_dir = mode.outputs.current_output_folder
            assert output_dir == folder_run_06
        else:
            assert mode.outputs is None
