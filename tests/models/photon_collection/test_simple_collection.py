#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from enum import Enum, auto

import numpy as np
import pytest
import xarray as xr

from pyxel.data_structure import Photon, Scene
from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    WavelengthHandling,
)
from pyxel.models.photon_collection.simple_collection import (
    aggregate_monochromatic,
    aggregate_multiwavelength,
    extract_wavelength,
    simple_collection,
)

# This is equivalent to 'import pytest_mock'
pytest_mock = pytest.importorskip(
    "pytest_mock",
    reason="Package 'pytest_mock' is not installed. Use 'pip install pytest-mock'",
)


@pytest.fixture
def ccd_3x3_no_photon() -> CCD:
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
        environment=Environment(),
        characteristics=Characteristics(),
    )

    detector.set_readout(times=[1.0], start_time=0.0)

    return detector


@pytest.fixture
def ccd_100x100_no_photon() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=100,
            col=100,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
            # pixel_scale=1.65,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )

    detector.set_readout(times=[1.0], start_time=0.0)

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
        "attrs": {
            "right_ascension": "57.1829668 deg",
            "declination": "23.84371349 deg",
            "fov_radius": "0.5 deg",
        },
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
def dummy_scene(mocker: pytest_mock.MockerFixture, scene_dataset: xr.Dataset):
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

    exp_ds = scene_dataset.interp(wavelength=wavelengths).sel(
        wavelength=slice(336, 342)
    )

    xr.testing.assert_equal(ds, exp_ds)


@pytest.mark.parametrize(
    "aperture, env_wavelength, geo_pixel_scale, filter_band, resolution, pixelscale",
    [
        pytest.param(1.0, None, None, (336, 342), 2, 1.65, id="no wavelength"),
        pytest.param(
            1.5, 336.0, None, (336, 342), 2, 1.65, id="with 'float' wavelength"
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            (336, 342),
            None,
            None,
            id="no resolution",
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            None,
            2,
            None,
            id="no filter_band",
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            None,
            None,
            None,
            id="no filter_band, resolution and pixelscale",
        ),
    ],
)
def test_simple_collection_photon_2d(
    aperture,
    env_wavelength,
    geo_pixel_scale,
    filter_band,
    resolution,
    pixelscale,
    ccd_100x100_no_photon: CCD,
    scene_dataset: xr.Dataset,
):
    """Test function 'simple_collection'."""
    detector = ccd_100x100_no_photon
    detector.environment._wavelength = env_wavelength
    detector.geometry._pixel_scale = geo_pixel_scale

    # Check if 'scene' and 'photon' are empty
    assert detector.scene == Scene()
    assert detector.photon == Photon(geo=detector.geometry)

    # Add a scene
    detector.scene.add_source(scene_dataset)

    # Run the model
    simple_collection(
        detector=detector,
        aperture=aperture,
        filter_band=filter_band,
        resolution=resolution,
        pixel_scale=pixelscale,
        integrate_wavelength=True,
    )

    # Check if a 2D photon is created
    photon_2d = detector.photon._array
    assert isinstance(photon_2d, np.ndarray)
    assert photon_2d.shape == (100, 100)
    assert photon_2d.dtype == float


@pytest.mark.parametrize(
    "aperture, env_wavelength, geo_pixel_scale, filter_band, resolution, pixelscale",
    [
        pytest.param(1.0, None, None, (336, 342), 2, 1.65, id="no wavelength"),
        pytest.param(
            1.5, 336.0, None, (336, 342), 2, 1.65, id="with 'float' wavelength"
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            (336, 342),
            None,
            None,
            id="no resolution",
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            None,
            2,
            None,
            id="no filter_band",
        ),
        pytest.param(
            3.0,
            WavelengthHandling(cut_on=336.0, cut_off=342, resolution=2),
            1.65,
            None,
            None,
            None,
            id="no filter_band, resolution and pixelscale",
        ),
    ],
)
def test_simple_collection_photon_3d(
    aperture,
    env_wavelength,
    geo_pixel_scale,
    filter_band,
    resolution,
    pixelscale,
    ccd_100x100_no_photon: CCD,
    scene_dataset: xr.Dataset,
):
    """Test function 'simple_collection'."""
    detector = ccd_100x100_no_photon
    detector.environment._wavelength = env_wavelength
    detector.geometry._pixel_scale = geo_pixel_scale

    # Check if 'scene' and 'photon' are empty
    assert detector.scene == Scene()
    assert detector.photon == Photon(geo=detector.geometry)

    # Add a scene
    detector.scene.add_source(scene_dataset)

    # Run the model
    simple_collection(
        detector=detector,
        aperture=aperture,
        filter_band=filter_band,
        resolution=resolution,
        pixel_scale=pixelscale,
        integrate_wavelength=False,
    )

    # Check if a 2D photon is created
    photon_2d = detector.photon._array
    assert isinstance(photon_2d, xr.DataArray)
    assert photon_2d.sizes == {"wavelength": 3, "y": 100, "x": 100}
    assert photon_2d.dtype == float


class SceneType(Enum):
    """Used only for testing."""

    Missing = auto()
    Valid = auto()
    Invalid = auto()


class PhotonType(Enum):
    """Used only for testing."""

    NoPhoton = auto()
    Photon_2D = auto()
    Photon_3D = auto()


@pytest.mark.parametrize(
    "scene_type, photon_type, env_wavelength, geo_pixel_scale, aperture, filter_band, resolution, pixelscale, integrate_wavelength, exp_exception, exp_error",
    [
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            0.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Expected \'aperture\' > 0",
            id="aperture is 0",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            -1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Expected \'aperture\' > 0",
            id="aperture is negative",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 342),
            10,
            1.1,
            True,
            ValueError,
            r"\'filter_band\' must be increasing",
            id="same filter_band",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (346, 342),
            10,
            1.1,
            True,
            ValueError,
            r"\'filter_band\' must be increasing",
            id="wrong filter_band",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (-1, 342),
            10,
            1.1,
            True,
            ValueError,
            r"\'filter_band\' must be increasing",
            id="negative filter_band",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            0,
            1.1,
            True,
            ValueError,
            r"Expected \'resolution\' > 0",
            id="resolution is 0",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            -1,
            1.1,
            True,
            ValueError,
            r"Expected \'resolution\' > 0",
            id="resolution is negative",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            0,
            True,
            ValueError,
            r"Expected \'pixel_scale\' > 0",
            id="pixelscale is 0",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            -1,
            True,
            ValueError,
            r"Expected \'pixel_scale\' > 0",
            id="pixelscale is negative",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - No Photon",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.Photon_2D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - Photon2D",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.Photon_3D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - Photon3D",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            False,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - No Photon - no integration",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.Photon_2D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            False,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - Photon2D - no integration",
        ),
        pytest.param(
            SceneType.Missing,
            PhotonType.Photon_3D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            False,
            ValueError,
            r"Missing \'scene\'",
            id="No Scene - Photon3D - no integration",
        ),
        pytest.param(
            SceneType.Invalid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"No objects projected in the detector",
            id="Invalid Scene (Detector too small)",
        ),
        pytest.param(
            SceneType.Invalid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            False,
            ValueError,
            r"No objects projected in the detector",
            id="Invalid Scene (Detector too small) - no integration",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.Photon_2D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Photons are already defined",
            id="With Scene - Photon2D",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.Photon_3D,
            None,
            1.65,
            1.0,
            (342, 346),
            10,
            1.1,
            True,
            ValueError,
            r"Photons are already defined",
            id="With Scene - Photon3D",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            344.0,
            1.65,
            1.0,
            (342, 346),
            None,
            1.1,
            True,
            ValueError,
            r"No \'resolution\' provided",
            id="No resolution",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            344.0,
            1.65,
            1.0,
            None,
            -1,
            1.1,
            True,
            ValueError,
            r"Expected \'resolution\' > 0",
            id="No filter_band, negative resolution",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            344.0,
            1.65,
            1.0,
            None,
            10,
            1.1,
            True,
            ValueError,
            r"No \'filter_band\' provided",
            id="No filter_band",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            344.0,
            1.65,
            1.0,
            None,
            None,
            1.1,
            True,
            ValueError,
            r"\'filter_band\' and \'resolution\' have both to be provided",
            id="No filter_band and no resolution",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            (342, 346),
            None,
            1.1,
            True,
            ValueError,
            r"No \'resolution\' provided",
            id="No resolution - wavelength is float",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            None,
            10,
            1.1,
            True,
            ValueError,
            r"No \'filter_band\' provided",
            id="No filter_band - wavelength is float",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            1.65,
            1.0,
            None,
            None,
            1.1,
            True,
            ValueError,
            r"\'filter_band\' and \'resolution\' have both to be provided",
            id="No filter_band and no resolution - wavelength is float",
        ),
        pytest.param(
            SceneType.Valid,
            PhotonType.NoPhoton,
            None,
            None,
            1.0,
            (342, 346),
            10,
            None,
            True,
            ValueError,
            r"Pixel scale is not defined",
            id="No pixelscale",
        ),
    ],
)
def test_simple_collection_error(
    scene_type: SceneType,
    photon_type: PhotonType,
    env_wavelength: WavelengthHandling | float | None,
    geo_pixel_scale: float | None,
    aperture,
    filter_band,
    resolution,
    pixelscale,
    integrate_wavelength,
    exp_exception: Exception,
    exp_error: str,
    ccd_3x3_no_photon: CCD,
    ccd_100x100_no_photon: CCD,
    scene_dataset: xr.Dataset,
):
    """Test function 'simple_collection' with wrong inputs."""
    # Add a scene (or not)
    if scene_type is SceneType.Missing:
        detector = ccd_100x100_no_photon
        assert detector.scene == Scene()

    elif scene_type is SceneType.Invalid:
        detector = ccd_3x3_no_photon
        assert detector.scene == Scene()

        detector.scene.add_source(scene_dataset)

    elif scene_type is SceneType.Valid:
        detector = ccd_100x100_no_photon
        assert detector.scene == Scene()

        detector.scene.add_source(scene_dataset)

    assert detector.photon.ndim == 0

    detector.environment._wavelength = env_wavelength
    detector.geometry._pixel_scale = geo_pixel_scale

    # Add Photons (or not)
    if photon_type is PhotonType.NoPhoton:
        # Do nothing
        pass
    elif photon_type is PhotonType.Photon_2D:
        detector.photon.array = np.zeros(
            shape=(detector.geometry.row, detector.geometry.col), dtype=float
        )
    else:
        detector.photon.array_3d = xr.DataArray(
            np.zeros(
                shape=(3, detector.geometry.row, detector.geometry.col), dtype=float
            ),
            dims=["wavelength", "y", "x"],
            coords={"wavelength": [400, 500, 600]},
        )

    with pytest.raises(exp_exception, match=exp_error):
        simple_collection(
            detector=detector,
            aperture=aperture,
            filter_band=filter_band,
            resolution=resolution,
            pixel_scale=pixelscale,
            integrate_wavelength=integrate_wavelength,
        )


def test_aggregate_monochromatic():
    """Test function 'aggregate_monochromatic'."""
    ds = xr.Dataset()
    ds["converted_flux"] = xr.DataArray(
        [10.0, 20.0, 30.0, 1.0, 40.0],
        dims=["ref"],
        coords={
            "ref": [22, 23, 24, 25, 26],
            "detector_coords_x": xr.DataArray([2, 0, 4, 2, 2], dims="ref"),
            "detector_coords_y": xr.DataArray([3, 0, 4, 3, 2], dims="ref"),
        },
    )

    result_2d = aggregate_monochromatic(data=ds, rows=5, cols=5)
    assert isinstance(result_2d, np.ndarray)

    exp_result_2d = np.array(
        [
            [20.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 40.0, 0.0, 0.0],
            [0.0, 0.0, 11.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 30.0],
        ]
    )

    np.testing.assert_allclose(result_2d, exp_result_2d)


def test_aggregate_multiwavelength():
    """Test function 'aggregate_multiwavelength'."""
    ds = xr.Dataset()
    ds["converted_flux"] = xr.DataArray(
        [
            [10.0, 11.0, 12.0],
            [20.0, 21.0, 22.0],
            [32.0, 31.0, 30.0],
            [1.0, 1.0, 1.0],
            [40.0, 40.5, 41.0],
        ],
        dims=["ref", "wavelength"],
        coords={
            "ref": [22, 23, 24, 25, 26],
            "wavelength": [336, 338, 340],
            "detector_coords_x": xr.DataArray([2, 0, 4, 2, 2], dims="ref"),
            "detector_coords_y": xr.DataArray([3, 0, 4, 3, 2], dims="ref"),
        },
        attrs={"units": "m2 ph / cm2"},
    )

    result_3d = aggregate_multiwavelength(data=ds, rows=5, cols=5)
    assert isinstance(result_3d, xr.DataArray)

    exp_result_3d = xr.DataArray(
        [
            [
                [20.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 40.0, 0.0, 0.0],
                [0.0, 0.0, 11.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 32.0],
            ],
            [
                [21.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 40.5, 0.0, 0.0],
                [0.0, 0.0, 12.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 31.0],
            ],
            [
                [22.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 41.0, 0.0, 0.0],
                [0.0, 0.0, 13.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 30.0],
            ],
        ],
        dims=["wavelength", "y", "x"],
        coords={"wavelength": [336, 338, 340]},
        attrs={"units": "m2 ph / cm2"},
    )

    xr.testing.assert_allclose(result_3d, exp_result_3d)
