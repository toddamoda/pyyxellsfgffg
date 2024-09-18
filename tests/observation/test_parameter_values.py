#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
import pytest

from pyxel.observation import ParameterValues
from pyxel.observation.parameter_values import ParameterType


def test_parameter_values():
    params = ParameterValues(key="foo", values="_")
    assert repr(params).startswith("ParameterValues<key='foo'")

    assert params.enabled is True
    assert params.logarithmic is False
    assert params.current is None

    assert params.key == "foo"
    assert params.short_name == "foo"
    assert params.type is ParameterType.Multi

    assert len(params) == 1
    assert list(params) == ["_"]
    assert params.values == "_"
    assert params.boundaries is None


def test_parameter_values_numpy():
    params = ParameterValues(
        key="foo.bar",
        values="numpy.arange(3, dtype='float')",
        logarithmic=True,
        boundaries=(4, 5),
    )

    assert params.enabled is True
    assert params.logarithmic is True
    assert params.current is None

    assert params.key == "foo.bar"
    assert params.short_name == "bar"
    assert params.type is ParameterType.Simple

    assert len(params) == 3
    assert list(params) == [0, 1.0, 2.0]
    assert params.values == "numpy.arange(3, dtype='float')"
    np.testing.assert_allclose(params.boundaries, np.array([4, 5], dtype=float))


def test_parameter_values_simple_str():
    params = ParameterValues(
        key="pipeline.charge_collection.fixed_pattern_noise.arguments.filename",
        values=["noise_64x64.npy", "no_noise_64x64.npy"],
    )

    assert params.enabled is True
    assert params.logarithmic is False
    assert params.current is None

    assert (
        params.key
        == "pipeline.charge_collection.fixed_pattern_noise.arguments.filename"
    )
    assert params.short_name == "filename"
    assert params.type is ParameterType.Simple

    assert len(params) == 2
    assert list(params) == ["noise_64x64.npy", "no_noise_64x64.npy"]
    assert params.values == ["noise_64x64.npy", "no_noise_64x64.npy"]


def test_parameter_values_multi():
    params = ParameterValues(
        key="XX.sampling.start_time",
        values=["_", "_", "_"],
        boundaries=[(0, 4), (5, 8), (10, 20)],
    )

    assert params.enabled is True
    assert params.logarithmic is False
    assert params.current is None

    assert params.key == "detector.sampling_properties.start_time"
    assert params.short_name == "start_time"
    assert params.type is ParameterType.Multi

    assert len(params) == 3
    assert list(params) == ["_", "_", "_"]
    assert params.values == ["_", "_", "_"]
    np.testing.assert_allclose(
        params.boundaries, np.array([[0, 4], [5, 8], [10, 20]], dtype=float)
    )


def test_parameter_values_multi2():
    params = ParameterValues(
        key="foo",
        values=[("_", "_"), ("_", "_"), ("_", "_")],
        boundaries=[(0, 4), (5, 8), (10, 20)],
    )

    assert params.enabled is True
    assert params.logarithmic is False
    assert params.current is None

    assert params.key == "foo"
    assert params.short_name == "foo"
    assert params.type is ParameterType.Multi

    assert len(params) == 3
    assert list(params) == [("_", "_"), ("_", "_"), ("_", "_")]
    assert params.values == [("_", "_"), ("_", "_"), ("_", "_")]
    np.testing.assert_allclose(
        params.boundaries, np.array([[0, 4], [5, 8], [10, 20]], dtype=float)
    )


def test_parameter_values_list():
    params = ParameterValues(key="foo", values=[1, 3.14], enabled=False)

    assert params.enabled is False
    assert params.logarithmic is False
    assert params.current is None

    assert params.key == "foo"
    assert params.short_name == "foo"
    assert params.type is ParameterType.Simple

    assert len(params) == 2
    assert list(params) == [1, 3.14]
    assert params.values == [1, 3.14]
    assert params.boundaries is None


@pytest.mark.parametrize(
    "values",
    [
        42,
    ],
)
def test_wrong_values(values):
    """Test class 'ParameterValues' with wrong values."""
    with pytest.raises(ValueError, match="Parameter values cannot be initiated"):
        _ = ParameterValues(key="foo", values=values)


@pytest.mark.parametrize(
    "values, boundaries, exp_msg",
    [
        ([1, 2], [4, 5, 6], "Expecting only two values"),
        ([1, 2], [[4], [5]], "Expecting a 2x"),
        ([1, 2], [[4, 5, 6], [7, 8, 9]], "Expecting a 2x"),
        ([1, 2], [[4, 5], [7, 8], [9, 10]], "Expecting a 2x"),
        ([1, 2], [[[1, 2], [3, 4], [5, 6]]], "Wrong format"),
    ],
)
def test_wrong_boundaries(values, boundaries, exp_msg):
    """Test class 'ParameterValues' with wrong boundaries."""
    with pytest.raises(ValueError, match=exp_msg):
        _ = ParameterValues(key="foo", values=values, boundaries=boundaries)


@pytest.mark.parametrize("values", ["numpy.xyz"])
def test_wrong_expression(values):
    """Test class 'ParameterValues' with wrong expression."""
    parameters = ParameterValues(key="foo", values=values)

    with pytest.raises(NameError):
        _ = len(parameters)
