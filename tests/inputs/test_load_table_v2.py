#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from astropy.table import Table

from pyxel.inputs import load_table_v2


@pytest.fixture(
    params=[
        pytest.param(("file", Path("table_tab.txt")), id="txt + tab"),
        pytest.param(("file", "table_space.data"), id="txt + space"),
        pytest.param(("file", Path("table_comma.csv")), id="txt + comma"),
        pytest.param(("file", "table_pipe.TXT"), id="txt + pipe"),
        pytest.param(("file", "table_semicolon.CSV"), id="txt + semicolon"),
        pytest.param(("file", "table.npy"), id="npy"),
        pytest.param(("file", "table.fits"), id="fits"),
    ]
)
def table_filename(request: pytest.FixtureRequest, tmp_path: Path) -> Path | str:
    """Build a table."""
    param: tuple[str, str] = request.param
    file_type, file_name = param

    df = pd.DataFrame(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        columns=["col1", "col2", "col3"],
        dtype=float,
    )

    if file_type == "file":
        full_path: Path = tmp_path / file_name

        if str(file_name).lower().startswith("table_tab"):
            df.to_csv(full_path, header=False, index=False, sep="\t")
        elif str(file_name).lower().startswith("table_space"):
            df.to_csv(full_path, header=False, index=False, sep=" ")
        elif str(file_name).lower().startswith("table_comma"):
            df.to_csv(full_path, header=False, index=False, sep=",")
        elif str(file_name).lower().startswith("table_pipe"):
            df.to_csv(full_path, header=False, index=False, sep="|")
        elif str(file_name).lower().startswith("table_semicolon"):
            df.to_csv(full_path, header=False, index=False, sep=";")
        elif str(file_name).lower() == "table.npy":
            np.save(full_path, arr=df.to_numpy())
        elif str(file_name).lower() == "table.fits":
            table: Table = Table.from_pandas(df)
            table.write(full_path)

        else:
            raise NotImplementedError

        if isinstance(file_name, str):
            return str(full_path)
        else:
            return full_path

    else:
        raise NotImplementedError


def test_load_table_v2(table_filename: Path | str):
    """Test function 'load_table_v2'."""
    df = load_table_v2(table_filename)
    assert isinstance(df, pd.DataFrame)

    if str(table_filename).endswith(".fits"):
        columns = ["col1", "col2", "col3"]
    else:
        columns = [0, 1, 2]

    exp_df = pd.DataFrame(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        columns=columns,
        dtype=float,
    )

    pd.testing.assert_frame_equal(df, exp_df)


def test_with_rename_cols(table_filename: Path | str):
    """Test function 'load_table_v2'."""
    df = load_table_v2(table_filename, rename_cols={"col1": 0, "col2": 1, "col3": 2})
    assert isinstance(df, pd.DataFrame)

    exp_df = pd.DataFrame(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        columns=["col1", "col2", "col3"],
        dtype=float,
    )

    pd.testing.assert_frame_equal(df, exp_df)


def test_wrong_input():
    """Test function 'load_table_v2' with invalid filename."""
    with pytest.raises(FileNotFoundError, match=r"Input file"):
        _ = load_table_v2(Path("unknown.txt"))


def test_wrong_delimiter(tmp_path: Path):
    """Test function 'load_table_v2' with invalid filename."""
    df = pd.DataFrame(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        columns=["col1", "col2", "col3"],
        dtype=float,
    )
    full_path = tmp_path / "table_bad_delimiter.csv"
    df.to_csv(full_path, header=False, index=False, sep="X")

    with pytest.raises(ValueError, match=r"Cannot find the separator"):
        _ = load_table_v2(full_path)
