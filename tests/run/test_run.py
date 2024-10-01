#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import pytest
from click.testing import CliRunner

from pyxel.run import main

# This is equivalent to 'import pytest_mock'
pytest_mock = pytest.importorskip(
    "pytest_mock",
    reason="Package 'pytest_mock' is not installed. Use 'pip install pytest-mock'",
)


def test_help():
    """Test command 'pyxel-sim --help'."""
    runner = CliRunner()

    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0


def test_version():
    """Test command 'pyxel-sim --version'."""
    runner = CliRunner()

    result = runner.invoke(main, ["--version"])
    assert result.output.startswith("main, version")
    assert result.exit_code == 0


def test_create_model():
    """Test command 'pyxel-sim create-model'."""
    runner = CliRunner()

    result = runner.invoke(main, ["create-model"])
    assert result.exit_code == 0


def test_download_examples(tmp_path: Path, mocker: pytest_mock.MockerFixture):
    """Test command 'pyxel-sim download-examples'."""
    mocker.patch(target="requests.get", return_value=b"hello")

    runner = CliRunner()

    result = runner.invoke(main, ["download-examples", str(tmp_path)])
    assert result.exit_code == 0


@pytest.mark.parametrize("verbosity", [None, "-v", "-vv", "-vvv"])
def test_exposure(verbosity: str):
    """Test command with an Exposure configuration file."""
    base_path = Path(__file__).parent

    filename = Path(f"{base_path}/data/exposure.yaml")
    assert filename.exists()

    runner = CliRunner()

    args = ["run", str(filename)]
    if verbosity:
        args = [*args, verbosity]

    result = runner.invoke(main, args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "override",
    [
        "detector.environment.temperature=100",
        "pipeline.photon_collection.load_image.arguments.level=500",
        "exposure.working_directory={tmp_folder}",
        "exposure.outputs.output_folder={tmp_folder}",
        "exposure.outputs.output_folder=None",
    ],
)
def test_exposure_override(tmp_path: Path, override: str):
    """Test command with an Exposure configuration file and override."""
    base_path = Path(__file__).parent

    filename = Path(f"{base_path}/data/exposure.yaml")
    assert filename.exists()

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["run", str(filename), "--override", override.format(tmp_folder=tmp_path)],
    )
    assert result.exit_code == 0


def test_exposure_override_wrong_input():
    """Test command with wrong override parameter."""
    base_path = Path(__file__).parent
    filename = Path(f"{base_path}/data/exposure.yaml")
    assert filename.exists()

    override = "exposure.dummy=foo"

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["run", str(filename), "--override", override],
    )
    assert result.exit_code == 1
    assert isinstance(result.exception, AttributeError)


def test_observation():
    """Test command with an Observation configuration file."""
    base_path = Path(__file__).parent
    filename = Path(f"{base_path}/data/observation.yaml")

    runner = CliRunner()
    result = runner.invoke(main, ["run", str(filename)])
    assert result.exit_code == 0
    assert result.exit_code == 0
