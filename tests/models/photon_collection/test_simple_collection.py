#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from contextlib import nullcontext as does_not_raise

import numpy as np
import pytest
import xarray as xr
from pytest_mock import MockerFixture  # pip install pytest-mock

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.photon_collection.simple_collection import (
    extract_wavelength,
    simple_collection,
)


@pytest.fixture
def ccd_3x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=3,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
            pixel_scale=1.65,
        ),
        environment=Environment(wavelength=600.0),
        characteristics=Characteristics(),
    )
    detector.photon.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector


@pytest.fixture
def ccd_4x5_multi_wavelength() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=4,
            col=5,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
            pixel_scale=1.65,
        ),
        environment=Environment(wavelength=600.0),
        characteristics=Characteristics(),
    )

    num_rows, num_cols = detector.geometry.shape

    detector.photon.array_3d = xr.DataArray(
        np.zeros(shape=(3, num_rows, num_cols), dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [620.0, 640.0, 680.0]},
    )

    return detector


@pytest.fixture
def scene_dataset() -> xr.Dataset:
    """Create a valid scene dataset."""
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
    wavelengths = xr.DataArray(
        data=[336.0, 337.0, 338.0, 339.0, 340.0, 341.0, 342.0], dims="wavelength"
    )

    ds = extract_wavelength(
        scene=dummy_scene,
        wavelengths=wavelengths,
    )

    exp_ds = scene_dataset.copy().sel(wavelength=slice(336, 342))

    xr.testing.assert_equal(ds, exp_ds)


@pytest.mark.parametrize(
    "aperture, filter_band, resolution, pixelscale, integrate_wavelength, expectation",
    [
        pytest.param(3.0, [600.0, 650.0], 10, 0.01, True, does_not_raise(), id="valid"),
        pytest.param(
            3.0,
            [650.0, 600.0],
            10,
            0.01,
            True,
            pytest.raises(ValueError, match=""),
            id="invalid",
        ),
    ],
)
def test_simple_collection(
    ccd_4x5_multi_wavelength: CCD,
    with_scene: bool,
    with_photon_2d: bool,
    with_photon_3d: bool,
    with_env_wavelength,
    aperture: float,
    filter_band: tuple[float, float],
    resolution: int,
    pixelscale: float,
    integrate_wavelength: bool,
    expectation,
    scene_dataset,
):
    """Test input parameters for function 'simple_collection'."""
    detector = ccd_4x5_multi_wavelength
    if with_scene:
        detector.scene = scene_dataset

    with expectation:
        simple_collection(
            detector=ccd_4x5_multi_wavelength,
            aperture=aperture,
            filter_band=filter_band,
            resolution=resolution,
            pixelscale=pixelscale,
            integrate_wavelength=integrate_wavelength,
        )
