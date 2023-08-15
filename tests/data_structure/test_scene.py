#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest
import xarray as xr
from datatree import DataTree
from datatree.testing import assert_identical

from pyxel.data_structure import Scene


@pytest.fixture
def source() -> xr.Dataset:
    """Create a valid source."""
    return xr.Dataset(
        {
            "x": xr.DataArray([64.97, 11.94, -55.75, -20.66], dims="ref"),
            "y": xr.DataArray([89.62, -129.3, -48.16, 87.87], dims="ref"),
            "weight": xr.DataArray([14.73, 12.34, 14.63, 14.27], dims="ref"),
            "flux": xr.DataArray(
                [
                    [0.1, 0.2, 0.3, 0.4],
                    [0.5, 0.6, 0.7, 0.8],
                    [0.9, 1.0, 1.1, 1.2],
                    [1.3, 1.4, 1.5, 1.6],
                ],
                dims=["ref", "wavelength"],
            ),
        },
        coords={"ref": [0, 1, 2, 3], "wavelength": [336.0, 338.0, 1018.0, 1020.0]},
    )


def test_empty_scene():
    """Tests with an empty Scene."""
    scene = Scene()

    # Test '.data'
    result = scene.data
    assert isinstance(result, DataTree)
    assert_identical(result, DataTree(name="scene"))

    # Test __eq__
    other_scene = Scene()
    assert scene == other_scene


def test_add_source(source: xr.Dataset):
    """Test method 'Scene.add_source'."""
    scene = Scene()

    # Add one source
    scene.add_source(source.copy(deep=True))

    # Check
    data = scene.data
    exp_data = DataTree(name="scene")
    exp_data["/list/0"] = DataTree(source.copy(deep=True))

    assert_identical(data, exp_data)

    # Check __eq__
    another_scene = Scene()
    assert scene != another_scene

    another_scene.add_source(source.copy(deep=True))
    assert scene == another_scene


def test_add_source_twice(source: xr.Dataset):
    """Test method 'Scene.add_source'."""
    scene = Scene()

    # Add inputs
    scene.add_source(source.copy(deep=True))
    scene.add_source(source.copy(deep=True))

    # Check
    data = scene.data
    exp_data = DataTree(name="scene")
    exp_data["/list/0"] = DataTree(source.copy(deep=True))
    exp_data["/list/1"] = DataTree(source.copy(deep=True))

    assert_identical(data, exp_data)

    # Check __eq__
    another_scene = Scene()
    another_scene.add_source(source.copy(deep=True))
    assert scene != another_scene

    another_scene.add_source(source.copy(deep=True))
    assert scene == another_scene


@pytest.mark.parametrize(
    "source, exp_error, exp_message",
    [
        (xr.DataArray(), TypeError, "Expecting a Dataset object for source"),
        (xr.Dataset(), ValueError, "Wrong format for source"),
        (
            xr.Dataset({"x": [1]}, coords={"ref": [1, 2], "wavelength": [1, 2]}),
            ValueError,
            r"Expecting coordinates \'ref\'",
        ),
        (
            xr.Dataset(
                {
                    "x": xr.DataArray([1], dims="ref"),
                    "y": xr.DataArray([1], dims="ref"),
                },
                coords={"ref": [1], "wavelength": [1]},
            ),
            ValueError,
            "Expecting a Dataset with variables",
        ),
    ],
)
def test_add_source_bad_inputs(source, exp_error, exp_message):
    """Test method 'Source.add_source' with bad inputs."""
    scene = Scene()

    with pytest.raises(exp_error, match=exp_message):
        scene.add_source(source)


def test_empty_to_dict_from_dict():
    """Test methods '.to_dict' and '.from_dict'."""
    scene = Scene()

    # Test method '.to_dict'
    dct = scene.to_dict()
    exp_dct = {"/": {"attrs": {}, "coords": {}, "data_vars": {}, "dims": {}}}
    assert dct == exp_dct

    # Test method '.from_dict'
    other_scene = Scene.from_dict(dct)
    assert scene == other_scene


def test_to_dict_from_dict(source: xr.Dataset):
    """Test methods '.to_dict' and '.from_dict'."""
    scene = Scene()
    scene.add_source(source)

    # Test method '.to_dict'
    dct = scene.to_dict()
    exp_dct = {
        "/": {"attrs": {}, "coords": {}, "data_vars": {}, "dims": {}},
        "/list": {"attrs": {}, "coords": {}, "data_vars": {}, "dims": {}},
        "/list/0": {
            "attrs": {},
            "coords": {
                "ref": {"attrs": {}, "data": [0, 1, 2, 3], "dims": ("ref",)},
                "wavelength": {
                    "attrs": {},
                    "data": [336.0, 338.0, 1018.0, 1020.0],
                    "dims": ("wavelength",),
                },
            },
            "data_vars": {
                "flux": {
                    "attrs": {},
                    "data": [
                        [0.1, 0.2, 0.3, 0.4],
                        [0.5, 0.6, 0.7, 0.8],
                        [0.9, 1.0, 1.1, 1.2],
                        [1.3, 1.4, 1.5, 1.6],
                    ],
                    "dims": ("ref", "wavelength"),
                },
                "weight": {
                    "attrs": {},
                    "data": [14.73, 12.34, 14.63, 14.27],
                    "dims": ("ref",),
                },
                "x": {
                    "attrs": {},
                    "data": [64.97, 11.94, -55.75, -20.66],
                    "dims": ("ref",),
                },
                "y": {
                    "attrs": {},
                    "data": [89.62, -129.3, -48.16, 87.87],
                    "dims": ("ref",),
                },
            },
            "dims": {"ref": 4, "wavelength": 4},
        },
    }
    assert dct == exp_dct

    # Test method '.from_dict'
    other_scene = Scene.from_dict(dct)
    assert scene == other_scene
