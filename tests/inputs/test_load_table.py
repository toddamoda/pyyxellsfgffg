#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
import re
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
import pytest
from astropy.table import Table

import pyxel
from pyxel import load_table

# This is equivalent to 'import pytest_httpserver'
pytest_httpserver = pytest.importorskip(
    "pytest_httpserver",
    reason="Package 'pytest_httpserver' is not installed. Use 'pip install pytest-httpserver'",
)


@pytest.fixture
def valid_table_http_hostname(
    tmp_path: Path, httpserver: pytest_httpserver.HTTPServer
) -> str:
    """Create valid tables locally and on a temporary HTTP server."""
    # Get current folder
    current_folder: Path = Path().cwd()

    try:
        os.chdir(tmp_path)

        # Create folder 'data'
        Path("data").mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            columns=["col1", "col2", "col3"],
            dtype=float,
        )

        # Save tables
        df.to_csv("data/table_tab.txt", header=False, index=False, sep="\t")
        df.to_csv("data/table_space.TXT", header=False, index=False, sep=" ")
        df.to_csv("data/table_comma.data", header=False, index=False, sep=",")
        df.to_csv("data/table_pipe.txt", header=False, index=False, sep="|")
        df.to_csv("data/table_semicolon.txt", header=False, index=False, sep=";")

        df.to_csv("data/table_tab_with_header.txt", header=True, index=False, sep="\t")
        df.to_csv("data/table_space_with_header.TXT", header=True, index=False, sep=" ")
        df.to_csv(
            "data/table_comma_with_header.data", header=True, index=False, sep=","
        )
        df.to_csv("data/table_pipe_with_header.txt", header=True, index=False, sep="|")
        df.to_csv(
            "data/table_semicolon_with_header.txt", header=True, index=False, sep=";"
        )

        df.to_excel("data/table.xlsx", header=False, index=False)
        df.to_excel("data/table_with_header.xlsx", header=True, index=False)

        np.save("data/table.npy", arr=df.to_numpy())

        text_filenames = [
            "data/table_tab.txt",
            "data/table_space.TXT",
            "data/table_comma.data",
            "data/table_pipe.txt",
            "data/table_semicolon.txt",
            "data/table_tab_with_header.txt",
            "data/table_space_with_header.TXT",
            "data/table_comma_with_header.data",
            "data/table_pipe_with_header.txt",
            "data/table_semicolon_with_header.txt",
        ]

        # Put text data in a fake HTTP server
        for filename in text_filenames:
            response_data: str = Path(filename).read_text()
            httpserver.expect_request(f"/{filename}").respond_with_data(
                response_data, content_type="text/plain"
            )

        binary_filenames = [
            ("data/table.xlsx", "application/octet-stream"),
            ("data/table_with_header.xlsx", "application/octet-stream"),
            ("data/table.npy", "application/octet-stream"),
        ]

        # Put binary data in a fake HTTP server
        for filename, content_type in binary_filenames:
            response_data_bytes: bytes = Path(filename).read_bytes()
            httpserver.expect_request(f"/{filename}").respond_with_data(
                response_data_bytes, content_type=content_type
            )

        # Extract an url (e.g. 'http://localhost:59226/)
        url: str = httpserver.url_for("")

        # Extract the hostname (e.g. 'localhost:59226')
        hostname: str = re.findall("http://(.*)/", url)[0]

        yield hostname

    finally:
        os.chdir(current_folder)


@pytest.fixture
def valid_table_heterogeneous(tmp_path: Path) -> str:
    # Create folder 'data'
    df = pd.DataFrame(
        [[1, 2, 3], ["foo", "bar", "baz"], [1.1, 2.2, 3.3]],
        columns=["col1", "col2", "col3"],
    )

    # Save tables
    df.to_csv(tmp_path / "table_tab.txt", header=False, index=False, sep="\t")
    df.to_csv(tmp_path / "table_space.txt", header=False, index=False, sep=" ")
    df.to_csv(tmp_path / "table_pipe.txt", header=False, index=False, sep=",")
    df.to_csv(tmp_path / "table_comma.data", header=False, index=False, sep="|")
    df.to_csv(tmp_path / "table_semicolon.txt", header=False, index=False, sep=";")

    return tmp_path


@pytest.fixture
def invalid_table_http_hostname(
    tmp_path: Path, httpserver: pytest_httpserver.HTTPServer
) -> str:
    """Create invalid tables on temporary folder and HTTP server."""
    # Get current folder
    current_folder: Path = Path().cwd()

    try:
        os.chdir(tmp_path)

        # Create folder 'data'
        Path("invalid_data").mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)

        # Save tables
        df.to_csv("invalid_data/table_X.txt", header=False, index=False, sep="X")
        Path("invalid_data/table_empty.txt").touch()

        text_filenames = [
            "invalid_data/table_X.txt",
            "invalid_data/table_empty.txt",
        ]

        # Put text data in a fake HTTP server
        for filename in text_filenames:
            response_data: str = Path(filename).read_text()
            httpserver.expect_request(f"/{filename}").respond_with_data(
                response_data, content_type="text/plain"
            )

        # Extract an url (e.g. 'http://localhost:59226/)
        url: str = httpserver.url_for("")

        # Extract the hostname (e.g. 'localhost:59226')
        hostname: str = re.findall("http://(.*)/", url)[0]

        yield hostname

    finally:
        os.chdir(current_folder)


@pytest.fixture(
    params=[
        pytest.param(Path("single_column.txt"), id="txt"),
        pytest.param(Path("single_column.TXT"), id="txt2"),
        pytest.param(Path("single_column.csv"), id="csv"),
        pytest.param(Path("single_column.CSV"), id="CSV"),
        pytest.param(Path("single_column.fits"), id="fits"),
    ]
)
def table_single_column_text(
    request: pytest.FixtureRequest, tmp_path: Path
) -> Union[Path, str]:
    """Build a table with a single column."""
    filename = request.param

    df = pd.DataFrame(["foo", "bar", "baz"], columns=["name"])

    full_path: Path = tmp_path / filename

    if Path(filename).suffix.lower() in [".txt", ".csv"]:
        df.to_csv(full_path, header=False, index=False)
    elif Path(filename).suffix.lower() == ".fits":
        table: Table = Table.from_pandas(df)
        table.write(full_path)
    else:
        raise NotImplementedError

    if isinstance(filename, str):
        return str(full_path)
    else:
        return full_path


@pytest.mark.parametrize(
    "filename, exp_error, exp_message",
    [
        # ("dummy", ValueError, r"^Only (.*) implemented.$"),
        # (
        #     Path("unknown.txt"),
        #     FileNotFoundError,
        #     r"^Input file (.*) can not be found\.$",
        # ),
        # ("unknown.txt", FileNotFoundError, None),
        ("invalid_data/table_X.txt", ValueError, "Cannot find the separator"),
        (
            "http://{host}/invalid_data/table_X.txt",
            ValueError,
            "Cannot find the separator",
        ),
        ("invalid_data/table_empty.txt", ValueError, "Cannot find the separator"),
        (
            "http://{host}/invalid_data/table_empty.txt",
            ValueError,
            "Cannot find the separator",
        ),
    ],
)
def test_load_table_invalid_filename(
    invalid_table_http_hostname: str,
    filename,
    exp_error: TypeError,
    exp_message: Optional[str],
):
    """Test function 'load_table' with invalid filenames."""
    if isinstance(filename, str):
        filename = filename.format(host=invalid_table_http_hostname)

    with pytest.raises(exp_error, match=exp_message):
        _ = load_table(filename)


@pytest.mark.parametrize("dtype", ["float", None])
@pytest.mark.parametrize("with_caching", [False, True])
@pytest.mark.parametrize(
    "filename, with_header",
    [
        ("data/table_tab.txt", False),
        ("data/table_space.TXT", False),
        ("data/table_comma.data", False),
        ("data/table_pipe.txt", False),
        ("data/table_semicolon.txt", False),
        ("data/table.xlsx", False),
        ("data/table.npy", False),
        (Path("data/table_tab.txt"), False),
        (Path("data/table_space.TXT"), False),
        (Path("data/table_comma.data"), False),
        (Path("data/table_pipe.txt"), False),
        (Path("data/table_semicolon.txt"), False),
        (Path("data/table.xlsx"), False),
        (Path("data/table.npy"), False),
        ("http://{host}/data/table_tab.txt", False),
        ("http://{host}/data/table_space.TXT", False),
        ("http://{host}/data/table_comma.data", False),
        ("http://{host}/data/table_pipe.txt", False),
        ("http://{host}/data/table_semicolon.txt", False),
        ("http://{host}/data/table.xlsx", False),
        ("http://{host}/data/table.npy", False),
        ("data/table_tab_with_header.txt", True),
        ("data/table_space_with_header.TXT", True),
        ("data/table_comma_with_header.data", True),
        ("data/table_pipe_with_header.txt", True),
        ("data/table_semicolon_with_header.txt", True),
        ("data/table_with_header.xlsx", True),
        (Path("data/table_tab_with_header.txt"), True),
        (Path("data/table_space_with_header.TXT"), True),
        (Path("data/table_comma_with_header.data"), True),
        (Path("data/table_pipe_with_header.txt"), True),
        (Path("data/table_semicolon_with_header.txt"), True),
        (Path("data/table_with_header.xlsx"), True),
        ("http://{host}/data/table_tab_with_header.txt", True),
        ("http://{host}/data/table_space_with_header.TXT", True),
        ("http://{host}/data/table_comma_with_header.data", True),
        ("http://{host}/data/table_pipe_with_header.txt", True),
        ("http://{host}/data/table_semicolon_with_header.txt", True),
        ("http://{host}/data/table_with_header.xlsx", True),
    ],
)
def test_load_table(
    with_caching: bool,
    valid_table_http_hostname: str,
    filename,
    with_header: bool,
    dtype,
):
    """Test function 'load_table'."""
    with pyxel.set_options(cache_enabled=with_caching):
        if isinstance(filename, Path):
            # Load data
            table = load_table(filename, header=with_header, dtype=dtype)
        else:
            full_url: str = filename.format(host=valid_table_http_hostname)

            # Load data
            table = load_table(full_url, header=with_header, dtype=dtype)

        if not with_header:
            exp_table = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
        else:
            exp_table = pd.DataFrame(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                columns=["col1", "col2", "col3"],
                dtype=float,
            )
        pd.testing.assert_frame_equal(table, exp_table)


@pytest.mark.parametrize(
    "filename",
    [
        "table_tab.txt",
        "table_space.txt",
        "table_pipe.txt",
        "table_comma.data",
        "table_semicolon.txt",
    ],
)
def test_load_table_heterogeneous(valid_table_heterogeneous: Path, filename: str):
    """Test function 'load_table' with heterogeneous data."""
    folder = valid_table_heterogeneous

    df = load_table(folder / filename, header=True, dtype=None)

    exp_df = df = pd.DataFrame([[1, 2, 3], ["foo", "bar", "baz"], [1.1, 2.2, 3.3]])
    pd.testing.assert_frame_equal(df, exp_df)


@pytest.mark.parametrize(
    "filename",
    [
        "table_tab.txt",
        "table_space.txt",
        "table_pipe.txt",
        "table_comma.data",
        "table_semicolon.txt",
    ],
)
def test_load_table_heterogeneous_error(valid_table_heterogeneous: Path, filename: str):
    """Test function 'load_table' with heterogeneous data."""
    folder = valid_table_heterogeneous

    with pytest.raises(ValueError, match="could not convert string to float"):
        _ = load_table(folder / filename, header=True)


@pytest.mark.parametrize("filename", ["dummy.foo"])
def test_load_table_invalid_format(tmp_path: Path, filename: str):
    # Create an empty file
    full_filename: Path = tmp_path.joinpath(filename)
    full_filename.touch()

    with pytest.raises(ValueError, match=r"Only .* implemented"):
        _ = load_table(full_filename)


def test_load_table_single_column(table_single_column_text: Union[Path, str]):
    """Test function 'load_table"."""
    df = load_table(table_single_column_text, dtype=None)
    assert isinstance(df, pd.DataFrame)
