#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from pyxel.outputs import Outputs

# This is equivalent to 'import freezegun'
freezegun = pytest.importorskip(
    "freezegun",
    reason="Package 'freezegun' is not installed. Use 'pip install freezegun'",
)


@pytest.fixture
def valid_output(tmp_path: Path) -> Outputs:
    output = Outputs(output_folder=tmp_path / "folder")
    output.create_output_folder()

    return output


def test_outputs(tmp_path: Path):
    """Test class 'Outputs'."""
    folder_name: Path = tmp_path / "folder"

    output = Outputs(output_folder=str(folder_name))
    assert output.output_folder == folder_name
    assert output.custom_dir_name == ""

    # Test 'Outputs.__repr__'
    assert repr(output) == "Outputs<NO OUTPUT DIR, num_files=1>"

    #
    # Test 'Outputs.create_output_folder'
    #
    # Before calling '.create_output_folder'
    with pytest.raises(RuntimeError, match=r"'current_output_folder' is not defined"):
        _ = output.current_output_folder

    creation_date = datetime(year=2024, month=4, day=25, hour=10, minute=10, second=18)
    with freezegun.freeze_time(creation_date):
        output.create_output_folder()

    # After calling '.create_output_folder'
    exp_folder = folder_name / "run_20240425_101018"
    assert output.current_output_folder == exp_folder

    assert repr(output) == f"Outputs<output_dir='{exp_folder!s}', num_files=1>"


@pytest.mark.parametrize("custom_dir_name", [None, "foo_"])
def test_create_output_directory(tmp_path: Path, custom_dir_name: str | None):
    """Test method 'Outputs.create_output_folder'."""
    folder_name: Path = tmp_path / "folder"

    output = Outputs(output_folder=str(folder_name), custom_dir_name=custom_dir_name)

    # Create a folder
    creation_date = datetime(year=2024, month=4, day=25, hour=10, minute=10, second=18)
    with freezegun.freeze_time(creation_date):
        output.create_output_folder()

    # After calling '.create_output_folder'
    if custom_dir_name is None:
        exp_folder = folder_name / "run_20240425_101018"
    else:
        exp_folder = folder_name / f"{custom_dir_name}20240425_101018"
    assert output.current_output_folder == exp_folder

    # Create again a folder
    creation_date = datetime(year=2024, month=4, day=25, hour=10, minute=10, second=18)
    with freezegun.freeze_time(creation_date):
        output.create_output_folder()

    # After calling '.create_output_folder'
    if custom_dir_name is None:
        exp_folder = folder_name / "run_20240425_101018_1"
    else:
        exp_folder = folder_name / f"{custom_dir_name}20240425_101018_1"
    assert output.current_output_folder == exp_folder

    # Create again a folder with a new date
    creation_date = datetime(year=2024, month=4, day=25, hour=10, minute=11, second=18)
    with freezegun.freeze_time(creation_date):
        output.create_output_folder()

    # After calling '.create_output_folder'
    if custom_dir_name is None:
        exp_folder = folder_name / "run_20240425_101118"
    else:
        exp_folder = folder_name / f"{custom_dir_name}20240425_101118"
    assert output.current_output_folder == exp_folder


def test_output_folder(tmp_path: Path):
    """Test property 'Outputs.output_folder'."""
    folder_name: Path = tmp_path / "folder"

    output = Outputs(output_folder=folder_name)
    assert output.output_folder == folder_name

    new_folder = tmp_path / "new_folder"
    output.output_folder = new_folder
    assert output.output_folder == new_folder


@pytest.mark.parametrize("new_folder", [None, 123])
def test_output_folder_wrong_input(tmp_path: Path, new_folder):
    """Test property 'Outputs.output_folder'."""
    folder_name: Path = tmp_path / "folder"

    output = Outputs(output_folder=folder_name)

    with pytest.raises(
        TypeError, match="Wrong type for parameter 'folder'. Expecting 'str' or 'Path"
    ):
        output.output_folder = new_folder


@pytest.mark.parametrize(
    "custom_name",
    [
        pytest.param(None, id="no custom name"),
        pytest.param("name", id="with custom name"),
    ],
)
def test_custom_dir_name_input(tmp_path: Path, custom_name: str | None):
    """Test property 'Outputs.output_folder'."""
    folder_name: Path = tmp_path / "folder"

    if custom_name is None:
        output = Outputs(output_folder=folder_name)
        assert output.custom_dir_name == ""
    else:
        output = Outputs(output_folder=folder_name, custom_dir_name=custom_name)
        assert output.custom_dir_name == custom_name

    output.custom_dir_name = "new_custom_name"
    assert output.custom_dir_name == "new_custom_name"


@pytest.mark.parametrize("custom_name", [None, 123, Path("new")])
def test_custom_dir_name_input_wrong(tmp_path: Path, custom_name: str | None):
    """Test property 'Outputs.output_folder'."""
    folder_name: Path = tmp_path / "folder"

    output = Outputs(output_folder=folder_name)

    with pytest.raises(
        TypeError, match=r"Wrong type for parameter 'name'. Expecting 'str'"
    ):
        output.custom_dir_name = custom_name


@pytest.mark.parametrize(
    "with_auto_suffix",
    [
        pytest.param(True, id="with auto suffix"),
        pytest.param(False, id="without auto suffix"),
    ],
)
@pytest.mark.parametrize(
    "run_number",
    [
        pytest.param(None, id="no 'run_number'"),
        pytest.param(5, id="with 'run_number'"),
    ],
)
def test_save_to_fits(
    valid_output: Outputs, with_auto_suffix: bool, run_number: int | None
):
    """Test method 'Outputs.save_to_fits'."""
    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    # Save to a FITS file
    filename = output.save_to_fits(
        data=data_2d,
        name="data",
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
    )
    assert filename.exists() is True

    if with_auto_suffix:
        if run_number:
            exp_filename: Path = folder / "data_6.fits"
        else:
            exp_filename: Path = folder / "data_1.fits"
    else:
        exp_filename: Path = folder / "data.fits"

    assert exp_filename == filename


def test_save_multiple_files(valid_output: Outputs):
    """Test method 'Outputs.save_to_fits'."""
    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    # Save to a FITS file
    filename = output.save_to_fits(data=data_2d, name="data")

    exp_filename: Path = folder / "data_1.fits"
    assert filename == exp_filename

    # Save again to a new FITS file
    filename = output.save_to_fits(data=data_2d, name="data")

    exp_filename: Path = folder / "data_2.fits"
    assert filename == exp_filename


def test_save_multiple_files_with_run_number(valid_output: Outputs):
    """Test method 'Outputs.save_to_fits'."""
    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    # Save to a FITS file
    filename = output.save_to_fits(
        data=data_2d,
        name="data",
        run_number=4,
    )

    exp_filename: Path = folder / "data_5.fits"
    assert filename == exp_filename

    # Save again to a new FITS file
    with pytest.raises(OSError):  # noqa: PT011
        _ = output.save_to_fits(
            data=data_2d,
            name="data",
            run_number=4,
        )


def test_save_multiple_files_without_auto_suffix(valid_output: Outputs):
    """Test method 'Outputs.save_to_fits'."""
    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    # Save to a FITS file
    filename = output.save_to_fits(
        data=data_2d,
        name="data",
        with_auto_suffix=False,
    )
    exp_filename: Path = folder / "data.fits"
    assert filename == exp_filename

    # Save again to a new FITS file
    with pytest.raises(OSError):  # noqa: PT011
        _ = output.save_to_fits(
            data=data_2d,
            name="data",
            with_auto_suffix=False,
        )


def test_save_multiple_files_without_auto_suffix_with_run_number(valid_output: Outputs):
    """Test method 'Outputs.save_to_fits'."""
    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    # Save to a FITS file
    filename = output.save_to_fits(
        data=data_2d,
        name="data",
        with_auto_suffix=False,
        run_number=4,
    )

    exp_filename: Path = folder / "data.fits"
    assert filename == exp_filename

    # Save again to a new FITS file
    with pytest.raises(OSError):  # noqa: PT011
        _ = output.save_to_fits(
            data=data_2d,
            name="data",
            with_auto_suffix=False,
            run_number=4,
        )


@pytest.mark.parametrize(
    "with_auto_suffix",
    [
        pytest.param(True, id="with auto suffix"),
        pytest.param(False, id="without auto suffix"),
    ],
)
@pytest.mark.parametrize(
    "run_number",
    [
        pytest.param(None, id="no 'run_number'"),
        pytest.param(5, id="with 'run_number'"),
    ],
)
def test_save_to_txt(
    valid_output: Outputs, with_auto_suffix: bool, run_number: int | None
):
    """Test method 'Outputs.save_to_fits'."""
    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    filename = output.save_to_txt(
        data=data_2d,
        name="data",
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
    )
    assert filename.exists() is True

    if with_auto_suffix:
        if run_number:
            exp_filename: Path = folder / "data_6.txt"
        else:
            exp_filename: Path = folder / "data_1.txt"
    else:
        exp_filename: Path = folder / "data.txt"

    assert exp_filename == filename


@pytest.mark.parametrize(
    "with_auto_suffix",
    [
        pytest.param(True, id="with auto suffix"),
        pytest.param(False, id="without auto suffix"),
    ],
)
@pytest.mark.parametrize(
    "run_number",
    [
        pytest.param(None, id="no 'run_number'"),
        pytest.param(5, id="with 'run_number'"),
    ],
)
def test_save_to_csv(
    valid_output: Outputs, with_auto_suffix: bool, run_number: int | None
):
    """Test method 'Outputs.save_to_fits'."""
    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    filename = output.save_to_csv(
        data=data_2d,
        name="data",
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
    )
    assert filename.exists() is True

    if with_auto_suffix:
        if run_number:
            exp_filename: Path = folder / "data_6.csv"
        else:
            exp_filename: Path = folder / "data_1.csv"
    else:
        exp_filename: Path = folder / "data.csv"

    assert exp_filename == filename


@pytest.mark.parametrize(
    "with_auto_suffix",
    [
        pytest.param(True, id="with auto suffix"),
        pytest.param(False, id="without auto suffix"),
    ],
)
@pytest.mark.parametrize(
    "run_number",
    [
        pytest.param(None, id="no 'run_number'"),
        pytest.param(5, id="with 'run_number'"),
    ],
)
def test_save_to_npy(
    valid_output: Outputs, with_auto_suffix: bool, run_number: int | None
):
    """Test method 'Outputs.save_to_fits'."""
    data_2d = np.array([[1, 2], [3, 4]], dtype=float)

    output: Outputs = valid_output
    folder: Path = output.current_output_folder

    filename = output.save_to_npy(
        data=data_2d,
        name="data",
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
    )
    assert filename.exists() is True

    if with_auto_suffix:
        if run_number:
            exp_filename: Path = folder / "data_6.npy"
        else:
            exp_filename: Path = folder / "data_1.npy"
    else:
        exp_filename: Path = folder / "data.npy"

    assert exp_filename == filename
