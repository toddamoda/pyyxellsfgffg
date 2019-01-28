"""Unittests for the 'PixelLoader' class."""
import re
import inspect
import numpy as np
import pytest
import yaml


def _expr_processor(loader: yaml.Loader, node: yaml.ScalarNode):
    value = loader.construct_scalar(node)

    try:
        result = eval(value, {}, np.__dict__)

        if callable(result) or inspect.ismodule(result):
            result = value

    except NameError:
        result = value

    return result


yaml.Loader.add_implicit_resolver('!expr', re.compile(r'^.*$'), None)
yaml.Loader.add_constructor('!expr', _expr_processor)


@pytest.mark.parametrize('data, expected', [
    ('a: !expr 3.14', {'a': 3.14}),
    ('x: !expr 2**16', {'x': 65536}),
    ('- !expr 3 * (4 + 5)', [27]),
    ('- !expr 1.0e-6', [0.000001]),
    ('- !expr 1.1E+2', [110.0]),
    ('- !expr 1.1e+2', [110.0]),
    ('- !expr 1e+2', [100.0]),
    ('a: !expr 2 * foo', {'a': '2 * foo'}),
    ('b: !expr pi * 2', {'b': 6.283185307179586}),
    ('- !expr sin(pi / 2)', [1.0]),
    ('- !expr range(3)', [range(3)]),
    ('- !expr range(3, 10, 2)', [range(3, 10, 2)]),
    ('!expr arange(4)', np.array([0, 1, 2, 3])),
    ('!expr random', 'random'),
    ('random', 'random'),

    ('a: 3.14', {'a': 3.14}),
    ('x: 2**16', {'x': 65536}),
    ('- 3 * (4 + 5)', [27]),
    ('- 1.0e-6', [0.000001]),
    ('- 1.1E+2', [110.0]),
    ('- 1.1e+2', [110.0]),
    ('- 1e+2', [100.0]),
    ('a: 2 * foo', {'a': '2 * foo'}),
    ('b: pi * 2', {'b': 6.283185307179586}),
    ('- sin(pi / 2)', [1.0]),
    ('- range(3)', [range(3)]),
    ('- range(3, 10, 2)', [range(3, 10, 2)]),
    ('arange(4)', np.array([0, 1, 2, 3])),
])
def test_expr_with_tag(data, expected):
    """Test tag '!expr'."""
    obj = yaml.load(data)

    if isinstance(expected, np.ndarray):
        # Test `numpy.ndarray`
        np.testing.assert_array_equal(obj, expected)
    else:
        # Normal test
        assert obj == expected
