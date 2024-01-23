#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from copy import deepcopy

import numpy as np
import pytest
import xarray as xr

from pyxel.data_structure import Photon
from pyxel.detectors import Geometry


@pytest.fixture
def empty_photon() -> Photon:
    """Empty photon object."""
    return Photon(geo=Geometry(row=2, col=3))


@pytest.fixture
def photon_2d() -> Photon:
    """Contain a 2D array in the Photon object."""
    photon = Photon(geo=Geometry(row=2, col=3))
    photon.array = np.array([[0, 1, 2], [4, 5, 6]], dtype=float)

    return photon


@pytest.fixture
def photon_3d() -> Photon:
    """Contain a 3D array in the Photon object."""
    photon = Photon(geo=Geometry(row=2, col=3))
    photon.array = xr.DataArray(
        np.array(
            [
                [[0, 1, 2], [4, 5, 6]],
                [[12, 13, 14], [16, 17, 18]],
            ],
            dtype=float,
        ),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [300.0, 350.0]},
    )

    return photon


def test_empty_photon():
    """Tests with an empty 'Photon' object."""
    photon = Photon(geo=Geometry(row=2, col=3))

    # Test 'Photon.__array__'
    with pytest.raises(ValueError, match="Not initialized"):
        _ = np.array(photon)

    # Test properties 'Photon.shape' and 'Photon.ndim'
    assert photon.shape == ()
    assert photon.ndim == 0


@pytest.mark.parametrize("dtype", [float, np.float64, np.float32, np.float16])
def test_valid_array_2d(dtype):
    """Test with a valid 2D array."""
    photon = Photon(geo=Geometry(row=2, col=3))

    data_2d = np.array([[0, 1.1, 2.2], [4.4, 5.5, 6.6]], dtype=dtype)
    copied_data_2d = data_2d.copy()

    # Test properties 'Photon.array'
    photon.array = data_2d
    new_data_2d = photon.array

    data_2d *= 2

    np.testing.assert_allclose(new_data_2d, copied_data_2d)
    assert new_data_2d.dtype == copied_data_2d.dtype

    # Test 'Photon.__array__'
    another_data_2d = np.array(photon)
    np.testing.assert_allclose(another_data_2d, copied_data_2d)
    assert another_data_2d.dtype == copied_data_2d.dtype

    # Test 'Photon.shape'
    assert photon.shape == copied_data_2d.shape
    assert photon.ndim == copied_data_2d.ndim


@pytest.mark.parametrize("dtype", [float, np.float64, np.float32, np.float16])
def test_valid_array_3d(dtype):
    """Test with a valid 3D array."""
    photon = Photon(geo=Geometry(row=2, col=3))

    data_3d = xr.DataArray(
        np.array(
            [
                [[0, 1.1, 2.2], [4.4, 5.5, 6.6]],
                [[12.1, 13.2, 14.3], [15.5, 16.6, 17.7]],
            ],
            dtype=dtype,
        ),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [300.0, 350.0]},
    )
    copied_data_3d = data_3d.copy()

    # Test properties 'Photon.array'
    photon.array = data_3d
    new_data_3d = photon.array

    data_3d *= 2

    np.testing.assert_allclose(new_data_3d, copied_data_3d)
    assert new_data_3d.dtype == copied_data_3d.dtype

    # Test 'Photon.__array__'
    another_data_3d = np.array(photon)
    np.testing.assert_allclose(another_data_3d, copied_data_3d)
    assert another_data_3d.dtype == copied_data_3d.dtype

    # Test 'Photon.shape'
    assert photon.shape == copied_data_3d.shape
    assert photon.ndim == copied_data_3d.ndim


@pytest.mark.parametrize("dtype", [float, np.float64, np.float32, np.float16])
def test_valid_negative_array_2d(dtype):
    """Test with negative 2D value."""
    photon = Photon(geo=Geometry(row=2, col=3))

    data_2d = np.array([[0, 1.1, -2.2], [-4.4, 5.5, 6.6]], dtype=dtype)
    expected_data_2d = np.array([[0, 1.1, 0], [0, 5.5, 6.6]], dtype=dtype)

    # Test properties 'Photon.array'
    with pytest.warns(UserWarning, match=r"Trying to set negative values"):
        photon.array = data_2d
    new_data_2d = photon.array

    np.testing.assert_allclose(new_data_2d, expected_data_2d)
    assert new_data_2d.dtype == expected_data_2d.dtype


@pytest.mark.parametrize("dtype", [float, np.float64, np.float32, np.float16])
def test_valid_negative_array_3d(dtype):
    """Test with negative 3D value."""
    photon = Photon(geo=Geometry(row=2, col=3))

    data_3d = xr.DataArray(
        np.array(
            [
                [[0, -1.1, 2.2], [4.4, 5.5, -6.6]],
                [[12.1, 13.2, 14.3], [15.5, -16.6, 17.7]],
            ],
            dtype=dtype,
        ),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [300.0, 350.0]},
    )
    expected_data_3d = xr.DataArray(
        np.array(
            [
                [[0, 0, 2.2], [4.4, 5.5, 0]],
                [[12.1, 13.2, 14.3], [15.5, 0, 17.7]],
            ],
            dtype=dtype,
        ),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [300.0, 350.0]},
    )

    # Test properties 'Photon.array'
    with pytest.warns(UserWarning, match=r"Trying to set negative values"):
        photon.array = data_3d
    new_data_3d = photon.array

    np.testing.assert_allclose(new_data_3d, expected_data_3d)
    assert new_data_3d.dtype == expected_data_3d.dtype


@pytest.mark.parametrize(
    "data, exp_exc, exp_msg",
    [
        pytest.param(
            [[0.0, 1.0, 2.0], [4.0, 5.0, 6.0]],
            TypeError,
            r"Photon array must be a numpy\.ndarray or xr\.DataArray",
            id="2D list",
        ),
        pytest.param(
            None,
            TypeError,
            r"Photon array must be a numpy\.ndarray or xr\.DataArray",
            id="None",
        ),
        pytest.param(
            np.array([[0, 1, 2], [4, 5, 6]], dtype=int),
            ValueError,
            r"'dtype' must be one of these values",
            id="2D Array - wrong dtype",
        ),
        pytest.param(
            xr.DataArray(
                np.array(
                    [
                        [[0, 1, 2], [4, 5, 6]],
                        [[12, 13, 14], [16, 17, 18]],
                    ],
                    dtype=int,
                ),
                dims=["wavelength", "y", "x"],
                coords={"wavelength": [300.0, 350.0]},
            ),
            ValueError,
            r"'dtype' must be one of these values",
            id="3D Array - wrong dtype",
        ),
        pytest.param(
            np.array(
                [
                    [[0, 1, 2], [4, 5, 6]],
                    [[12, 13, 14], [16, 17, 18]],
                ],
                dtype=float,
            ),
            ValueError,
            r"must have 2 dimensions",
            id="2D Array - Wrong ndim",
        ),
        pytest.param(
            xr.DataArray(
                np.array(
                    [[0, 0, 2.2], [4.4, 5.5, 0]],
                    dtype=float,
                ),
                dims=["y", "x"],
            ),
            ValueError,
            r"must have 3 dimensions",
            id="3D Array - Wrong ndim",
        ),
        pytest.param(
            np.array([[0, 1], [2, 4], [5, 6]], dtype=float),
            ValueError,
            r"must have this shape",
            id="2D Array - Wrong shape",
        ),
        pytest.param(
            xr.DataArray(
                np.array(
                    [
                        [[0, 1], [4, 5]],
                        [[12, 13], [16, 17]],
                    ],
                    dtype=float,
                ),
                dims=["wavelength", "y", "x"],
                coords={"wavelength": [300.0, 350.0]},
            ),
            ValueError,
            r"must have this shape",
            id="3D Array - Wrong shape",
        ),
        pytest.param(
            xr.DataArray(
                np.array(
                    [
                        [[0, 1, 2], [4, 5, 6]],
                        [[12, 13, 14], [16, 17, 18]],
                    ],
                    dtype=float,
                ),
                dims=["undef", "y", "x"],
                coords={"undef": [300.0, 350.0]},
            ),
            ValueError,
            r"data array must have these dimensions",
            id="3D Array - wrong dimensions",
        ),
        pytest.param(
            xr.DataArray(
                np.array(
                    [
                        [[0, 1, 2], [4, 5, 6]],
                        [[12, 13, 14], [16, 17, 18]],
                    ],
                    dtype=float,
                ),
                dims=["wavelength", "y", "x"],
            ),
            ValueError,
            r"data array must have coordinates",
            id="3D Array - missing coordinates",
        ),
    ],
)
def test_invalid_array(data, exp_exc: Exception, exp_msg: str):
    """Test with invalid data and empty 'Photon'."""
    photon = Photon(geo=Geometry(row=2, col=3))

    with pytest.raises(exp_exc, match=exp_msg):
        photon.array = data


def test_set_array_3d_after_2d(photon_2d: Photon):
    """Test 'Photon.array' with 3D array when 2D array were set before."""
    photon_3d = xr.DataArray(
        np.array(
            [
                [[0, 1, 2], [4, 5, 6]],
                [[12, 13, 14], [16, 17, 18]],
            ],
            dtype=float,
        ),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [300.0, 350.0]},
    )

    # Try to set '3D' photons to 'photon_2d'
    with pytest.raises(TypeError, match="expects a 2D numpy array"):
        photon_2d.array = photon_3d


def test_set_array_2d_after_3d(photon_3d: Photon):
    """Test 'Photon.array' with 2D array when 3D array were set before."""
    photon_2d = np.array([[0, 1, 2], [4, 5, 6]], dtype=float)

    # Try to set '2D' photons to 'photon_3d'
    with pytest.raises(TypeError, match="expects a 3D Data Array"):
        photon_3d.array = photon_2d


def test_eq(empty_photon: Photon, photon_2d: Photon, photon_3d: Photon):
    """Test method 'Photon.__eq__'."""

    assert empty_photon == deepcopy(empty_photon)
    assert empty_photon != photon_2d
    assert empty_photon != photon_3d

    assert photon_2d != empty_photon
    assert photon_2d == deepcopy(photon_2d)
    assert photon_2d != photon_3d

    assert photon_3d != empty_photon
    assert photon_3d != photon_2d
    assert photon_3d == deepcopy(photon_3d)


def test_to_xarray_empty(empty_photon: Photon):
    """Test method 'Photon.to_xarray()' with an empty Photon."""
    obj = empty_photon.to_xarray()

    exp_obj = xr.DataArray()

    xr.testing.assert_identical(obj, exp_obj)


def test_to_xarray_2d(photon_2d: Photon):
    """Test method 'Photon.to_xarray()' with a 2D Photon."""
    obj = photon_2d.to_xarray()

    exp_obj = xr.DataArray(
        np.array([[0, 1, 2], [4, 5, 6]], dtype=float),
        dims=["y", "x"],
        coords={"y": [0, 1], "x": [0, 1, 2]},
        name="photon",
        attrs={"units": "Ph", "long_name": "Photon"},
    )

    xr.testing.assert_identical(obj, exp_obj)


def test_to_xarray_3d(photon_3d: Photon):
    """Test method 'Photon.to_xarray()' with a 3D Photon."""
    obj = photon_3d.to_xarray()

    exp_obj = xr.DataArray(
        np.array(
            [
                [[0, 1, 2], [4, 5, 6]],
                [[12, 13, 14], [16, 17, 18]],
            ],
            dtype=float,
        ),
        dims=["wavelength", "y", "x"],
        coords={"y": [0, 1], "x": [0, 1, 2], "wavelength": [300.0, 350.0]},
        name="photon",
        attrs={"units": "Ph nm⁻¹", "long_name": "Photon"},
    )
    xr.testing.assert_identical(obj, exp_obj)


def test_to_dict_from_dict_2d(photon_2d: Photon):
    """Test methods 'Photon.to_dict' and 'Photon.from_dict'."""
    dct = photon_2d.to_dict()
    assert isinstance(dct, dict)

    obj = Photon.from_dict(geometry=Geometry(row=2, col=3), data=dct)
    assert isinstance(obj, Photon)

    assert photon_2d == obj


def test_to_dict_from_dict_3d(photon_3d: Photon):
    """Test methods 'Photon.to_dict' and 'Photon.from_dict'."""
    dct = photon_3d.to_dict()
    assert isinstance(dct, dict)

    obj = Photon.from_dict(geometry=Geometry(row=2, col=3), data=dct)
    assert isinstance(obj, Photon)

    assert photon_3d == obj
