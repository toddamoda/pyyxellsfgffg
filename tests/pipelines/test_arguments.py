#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

from pyxel.pipelines import Arguments


def test_arguments():
    """Test class 'Arguments'."""
    dct = {"foo": 1, "bar": None}
    arguments = Arguments(dct)

    # Test .__len__
    assert len(arguments) == 2

    # Test __iter__
    assert list(arguments) == ["foo", "bar"]

    # Test .__hasitem__
    assert "foo" in arguments
    assert "FOO" not in arguments

    # Test .__setitem__
    arguments["foo"] = 2

    with pytest.raises(KeyError):
        arguments["unknown"] = 1

    # Test .__getitem__
    assert arguments["foo"] == 2
    assert arguments["bar"] is None

    with pytest.raises(KeyError):
        _ = arguments["unknown"]

    # Test .__setattr__
    arguments.bar = 3.14
    with pytest.raises(AttributeError):
        arguments.unknown = 1

    # Test .__getattr__
    assert arguments.bar == 3.14
    assert arguments.foo == 2

    with pytest.raises(AttributeError):
        _ = arguments.unknown

    # Test .__delitem__
    del arguments["bar"]
    assert list(arguments) == ["foo"]

    # Test .__dir__
    assert "foo" in dir(arguments)
    assert "bar" not in dir(arguments)

    assert dct == {"foo": 1, "bar": None}
