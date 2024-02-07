#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from pyxel.util import complete_path, is_path_relative


@pytest.mark.parametrize(
    "filename, exp_result",
    [
        ("sub", True),
        (Path("sub"), True),
        # ("/sub/test.fits", False), # This test gives a different result in Windows
        pytest.param(PureWindowsPath("/sub/test.fits"), True, id="Relative - Windows"),
        pytest.param(PurePosixPath("/sub/test.fits"), False, id="Absolute - Posix"),
        ("sub\\sub2\\test.fits", True),
        (Path("sub\\sub2\\test.fits"), True),
        ("ftp://test", False),
        # (Path("ftp://test"), False),  # This should not be possible
        ("http://test", False),
        # ("c:\\test", False),  # This test gives a different result in Windows
        pytest.param(PureWindowsPath("c:/test"), False, id="Absolute - Windows"),
    ],
)
def test_is_relative_true(filename, exp_result):
    """Test function 'is_path_relative'."""
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
        # Test with a URL
        ("http://foo/bar.fits", None, "http://foo/bar.fits"),
        ("http://foo/bar.fits", "", "http://foo/bar.fits"),
        ("http://foo/bar.fits", "parent", "http://foo/bar.fits"),
        ("http://foo/bar.fits", Path("parent"), "http://foo/bar.fits"),
        ("http://foo/bar.fits", "/parent", "http://foo/bar.fits"),
        ("http://foo/bar.fits", Path("/parent"), "http://foo/bar.fits"),
    ],
)
def test_complete_file(filename, working_dir, exp_result):
    result = complete_path(filename=filename, working_dir=working_dir)
    assert result == exp_result
