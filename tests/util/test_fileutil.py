from pathlib import Path

import pytest

from pyxel.util import complete_path, is_path_relative


@pytest.mark.parametrize(
    "filename, exp_result",
    [
        ("sub", True),
        (Path("sub"), True),
        ("/sub/test.fits", False),
        (Path("/sub/test.fits"), False),
        ("sub\\sub2\\test.fits", True),
        (Path("sub\\sub2\\test.fits"), True),
        ("ftp://test", False),
        (Path("ftp://test"), False),
        ("http://test", False),
        ("c:\\test", False),
    ],
)
def test_is_relative_true(filename, exp_result):
    """Test function 'get_dtype'."""
    result = is_path_relative(filename)
    assert result == exp_result


@pytest.mark.parametrize(
    "filename, working_dir, exp_result",
    [
        ("sub", None, "sub"),
        ("sub", "", "sub"),
        ("/sub", "parent", "/sub"),
        ("/sub", "/parent", "/sub"),
        ("sub", "parent", "parent/sub"),
        (Path("sub"), Path("parent"), Path("parent/sub")),
        ("sub", "/parent", "/parent/sub"),
        (Path("sub"), Path("/parent"), Path("/parent/sub")),
    ],
)
def test_complete_file(filename, working_dir, exp_result):
    result = complete_path(filename, working_dir)
    assert result == exp_result
