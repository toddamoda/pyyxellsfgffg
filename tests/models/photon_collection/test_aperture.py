#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

import pytest
import xarray as xr
from pytest_mock import MockerFixture  # pip install pytest-mock

from pyxel.data_structure import Scene
from pyxel.models.photon_collection.aperture import extract_wavelength


def test_extract_wavelength_error():
    with pytest.raises(
        ValueError,
        match="First input in wavelength_band needs to be smaller than the second.",
    ):
        extract_wavelength(scene=..., wavelength_band=[900, 500])


@pytest.fixture
def scene_dataset() -> xr.Dataset:
    dct = {
        "coords": {
            "ref": {"dims": ("ref",), "attrs": {}, "data": [0, 1, 2]},
            "wavelength": {
                "dims": ("wavelength",),
                "attrs": {"units": "nm"},
                "data": [336.0, 338.0, 340.0, 342.0],
            },
        },
        "attrs": {},
        "dims": {"ref": 3, "wavelength": 4},
        "data_vars": {
            "x": {
                "dims": ("ref",),
                "attrs": {"units": "arcsec"},
                "data": [205732.81147230256, 205832.50867371075, 206010.7213446728],
            },
            "y": {
                "dims": ("ref",),
                "attrs": {"units": "arcsec"},
                "data": [85748.89015925185, 85802.09354969644, 85961.12201291585],
            },
            "weight": {
                "dims": ("ref",),
                "attrs": {"units": "mag"},
                "data": [11.489056587219238, 14.131349563598633, 15.217577934265137],
            },
            "flux": {
                "dims": ("ref", "wavelength"),
                "attrs": {"units": "ph / (cm2 nm s)"},
                "data": [
                    [
                        0.03769071172453367,
                        0.041374086069586175,
                        0.03988154035070513,
                        0.0362458369803364,
                    ],
                    [
                        0.01151902543689362,
                        0.010221036617896213,
                        0.009752581546174546,
                        0.009850105680742818,
                    ],
                    [
                        0.0019267151902375244,
                        0.0017953813076332019,
                        0.0016775406524146613,
                        0.001506762466011516,
                    ],
                ],
            },
        },
    }
    return xr.Dataset.from_dict(dct)


@pytest.fixture
def dummy_scene(mocker: MockerFixture, scene_dataset: xr.Dataset):
    scene = Scene()

    mocker.patch.object(scene, "to_xarray", return_value=scene_dataset)
    return scene


def test_extract_wavelength(dummy_scene: Scene, scene_dataset: xr.Dataset):
    """..."""
    ds = extract_wavelength(scene=dummy_scene, wavelength_band=[336, 340])

    exp_ds = scene_dataset.copy().sel(wavelength=slice(336, 340))

    xr.testing.assert_equal(ds, exp_ds)
