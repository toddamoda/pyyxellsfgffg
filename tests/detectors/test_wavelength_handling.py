#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


import pytest
import xarray as xr

from pyxel.detectors import WavelengthHandling


@pytest.mark.parametrize(
    "cut_on, cut_off, resolution, exp_wavelengths",
    [
        (1.0, 1.0, 1, xr.DataArray([], dims="wavelength", attrs={"units": "nm"})),
        (
            1.0,
            4.0,
            1,
            xr.DataArray([1.0, 2.0, 3.0], dims="wavelength", attrs={"units": "nm"}),
        ),
        (
            5.0,
            6.5,
            0.5,
            xr.DataArray([5.0, 5.5, 6.0], dims="wavelength", attrs={"units": "nm"}),
        ),
    ],
)
def test_wavelength_handling(
    cut_on: float, cut_off: float, resolution: int, exp_wavelengths: xr.DataArray
):
    """Test class 'WavelengthHandling."""
    obj = WavelengthHandling(cut_on=cut_on, cut_off=cut_off, resolution=resolution)

    # Test method 'WavelengthHandling.to_dict'
    dct = obj.to_dict()
    exp_dct = {"cut_on": cut_on, "cut_off": cut_off, "resolution": resolution}
    assert dct == exp_dct

    # Test class method 'WavelengthHandling.from_dict'
    new_obj = WavelengthHandling.from_dict(data=exp_dct)
    assert isinstance(new_obj, WavelengthHandling)
    assert new_obj == obj

    # Test method 'WavelengthHandling.get_wavelengths'
    wavelengths = obj.get_wavelengths()
    assert isinstance(wavelengths, xr.DataArray)
    xr.testing.assert_equal(wavelengths, exp_wavelengths)


@pytest.mark.parametrize(
    "cut_on, cut_off, resolution, exp_exc, exp_msg",
    [
        (0, 4.0, 1, ValueError, "'cut_on' must be > 0"),
        (-1.0, 4.0, 1, ValueError, "'cut_on' must be > 0"),
        (4.0, 1.0, 1, ValueError, "'cut_off' must be bigger than 'cut_on'"),
        (1.0, 4.0, 0, ValueError, "'resolution' must be > 0"),
        (1.0, 4.0, -1, ValueError, "'resolution' must be > 0"),
    ],
)
def test_wavelength_handling_wrong_inputs(
    cut_on: float,
    cut_off: float,
    resolution: int,
    exp_exc: type[Exception],
    exp_msg: str,
):
    """Test class 'WavelengthHandling."""
    with pytest.raises(exp_exc, match=exp_msg):
        _ = WavelengthHandling(cut_on=cut_on, cut_off=cut_off, resolution=resolution)
