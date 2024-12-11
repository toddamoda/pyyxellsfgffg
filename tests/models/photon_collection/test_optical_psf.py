#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import pytest
import xarray as xr
from astropy.units import Quantity

from pyxel.data_structure import Photon
from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    WavelengthHandling,
)
from pyxel.models.photon_collection import optical_psf
from pyxel.models.photon_collection.poppy import create_optical_item

# Try to import 'poppy'
poppy = pytest.importorskip("poppy")


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


@pytest.mark.parametrize(
    "default_wavelength",
    [
        pytest.param(Quantity(300, unit="nm"), id="monochromatic"),
        pytest.param(
            (Quantity(200, unit="nm"), Quantity(400, unit="nm")), id="multivavelength"
        ),
    ],
)
@pytest.mark.parametrize(
    "dct, exp_parameter",
    [
        pytest.param(
            {"item": "CircularAperture", "radius": 3.14},
            poppy.CircularAperture(radius=3.14),
            id="CircularAperture",
        ),
        pytest.param(
            {
                "item": "ThinLens",
                "nwaves": 1.1,
                "radius": 2.2,
                "reference_wavelength": 600.0,
            },
            poppy.ThinLens(nwaves=1.1, radius=2.2, reference_wavelength=600.0),
            id="ThinLens",
        ),
        pytest.param(
            {
                "item": "ThinLens",
                "nwaves": 1.1,
                "radius": 2.2,
            },
            poppy.ThinLens(nwaves=1.1, radius=2.2, reference_wavelength=600.0),
            id="ThinLens - No wavelength",
        ),
        pytest.param(
            {"item": "SquareAperture", "size": 1},
            poppy.SquareAperture(size=1),
            id="SquareAperture",
        ),
        pytest.param(
            {"item": "RectangularAperture", "width": 1.1, "height": 2.2},
            poppy.RectangleAperture(width=1.1, height=2.2),
            id="RectangularAperture",
        ),
        pytest.param(
            {"item": "HexagonAperture", "side": 1.1},
            poppy.HexagonAperture(side=1.1),
            id="HexagonAperture",
        ),
        pytest.param(
            {"item": "MultiHexagonalAperture", "side": 1.1, "rings": 2, "gap": 3.3},
            poppy.MultiHexagonAperture(side=1.1, rings=2, gap=3.3),
            id="MultiHexagonalAperture",
        ),
        pytest.param(
            {
                "item": "SecondaryObscuration",
                "secondary_radius": 1.1,
                "n_supports": 2,
                "support_width": 3.3,
            },
            poppy.SecondaryObscuration(
                secondary_radius=1.1, n_supports=2, support_width=3.3
            ),
            id="SecondaryObscuration",
        ),
        pytest.param(
            {
                "item": "ZernikeWFE",
                "radius": 1.1,
                "coefficients": [2.2, 3.3],
                "aperture_stop": 4.4,
            },
            poppy.ZernikeWFE(radius=1.1, coefficients=[2.2, 3.3], aperture_stop=4.4),
            id="ZernikeWFE",
        ),
        pytest.param(
            {
                "item": "SineWaveWFE",
                "spatialfreq": 2.2,
                "amplitude": 3.3,
                "rotation": 4.4,
            },
            poppy.SineWaveWFE(spatialfreq=2.2, amplitude=3.3, rotation=4.4),
            id="SineWaveWFE",
        ),
    ],
)
def test_create_optical_item(dct: Mapping, exp_parameter: dict, default_wavelength):
    """Test function 'create_optical_item'."""

    parameter = create_optical_item(
        dct,
        default_wavelength=default_wavelength,
    )
    assert isinstance(parameter, poppy.OpticalElement)
    assert isinstance(exp_parameter, poppy.OpticalElement)

    parameter_name = parameter.name
    exp_parameter_name = exp_parameter.name

    assert parameter_name == exp_parameter_name


@pytest.mark.parametrize(
    "dct, exp_error, exp_msg",
    [
        pytest.param({}, KeyError, r"Missing keyword \'item\'", id="no input"),
        pytest.param(
            {"item": "foo"},
            KeyError,
            r"Unknown \'optical_element\'",
            id="Unknown 'optical_element'",
        ),
        pytest.param(
            {"item": "CircularAperture"},
            KeyError,
            r"Missing parameter \'radius\'",
            id="CircularAperture - Missing 'radius'",
        ),
        pytest.param(
            {
                "item": "ThinLens",
                "radius": 2.2,
                "reference_wavelength": 600.0,
            },
            KeyError,
            r"Missing one of these parameters: \'nwaves\', \'radius\'",
            id="ThinLens - Missing 'nwaves'",
        ),
        pytest.param(
            {
                "item": "ThinLens",
                "nwaves": 1.1,
                "reference_wavelength": 600.0,
            },
            KeyError,
            r"Missing one of these parameters: \'nwaves\', \'radius\'",
            id="ThinLens - Missing 'radius'",
        ),
        pytest.param(
            {"item": "SquareAperture"},
            KeyError,
            r"Missing parameter \'size\'",
            id="SquareAperture - Missing 'size'",
        ),
        pytest.param(
            {"item": "RectangularAperture", "height": 2.2},
            KeyError,
            r"Missing one of these parameters: \'width\', \'height\'",
            id="RectangularAperture - Missing 'width'",
        ),
        pytest.param(
            {"item": "RectangularAperture", "width": 1.1},
            KeyError,
            r"Missing one of these parameters: \'width\', \'height\'",
            id="RectangularAperture - Missing 'height'",
        ),
        pytest.param(
            {"item": "HexagonAperture"},
            KeyError,
            r"Missing parameter \'side\'",
            id="HexagonAperture - Missing 'side'",
        ),
        pytest.param(
            {"item": "MultiHexagonalAperture", "rings": 2, "gap": 3.3},
            KeyError,
            r"Missing one of these parameters: \'side\', \'rings\', \'gap\'",
            id="MultiHexagonalAperture - Missing 'side'",
        ),
        pytest.param(
            {"item": "MultiHexagonalAperture", "side": 1.1, "gap": 3.3},
            KeyError,
            r"Missing one of these parameters: \'side\', \'rings\', \'gap\'",
            id="MultiHexagonalAperture - Missing 'rings'",
        ),
        pytest.param(
            {
                "item": "MultiHexagonalAperture",
                "side": 1.1,
                "rings": 2,
            },
            KeyError,
            r"Missing one of these parameters: \'side\', \'rings\', \'gap\'",
            id="MultiHexagonalAperture - Missing 'gap'",
        ),
        pytest.param(
            {
                "item": "SecondaryObscuration",
                "n_supports": 2,
                "support_width": 3.3,
            },
            KeyError,
            r"Missing one of these parameters: \'secondary_radius\', \'n_supports\', \'support_width\'",
            id="SecondaryObscuration - Missing 'secondary_radius'",
        ),
        pytest.param(
            {
                "item": "SecondaryObscuration",
                "secondary_radius": 1.1,
                "support_width": 3.3,
            },
            KeyError,
            r"Missing one of these parameters: \'secondary_radius\', \'n_supports\', \'support_width\'",
            id="SecondaryObscuration - Missing 'n_supports'",
        ),
        pytest.param(
            {
                "item": "SecondaryObscuration",
                "secondary_radius": 1.1,
                "n_supports": 2,
            },
            KeyError,
            r"Missing one of these parameters: \'secondary_radius\', \'n_supports\', \'support_width\'",
            id="SecondaryObscuration - Missing 'support_width'",
        ),
        pytest.param(
            {
                "item": "ZernikeWFE",
                "coefficients": [2.2, 3.3],
                "aperture_stop": 4.4,
            },
            KeyError,
            r"Missing one of these parameters: \'radius\', \'coefficients\', \'aperture_stop\'",
            id="ZernikeWFE - Missing 'radius'",
        ),
        pytest.param(
            {
                "item": "ZernikeWFE",
                "radius": 1.1,
                "aperture_stop": 4.4,
            },
            KeyError,
            r"Missing one of these parameters: \'radius\', \'coefficients\', \'aperture_stop\'",
            id="ZernikeWFE - Missing 'coefficients'",
        ),
        pytest.param(
            {
                "item": "ZernikeWFE",
                "radius": 1.1,
                "coefficients": [2.2, 3.3],
            },
            KeyError,
            r"Missing one of these parameters: \'radius\', \'coefficients\', \'aperture_stop\'",
            id="ZernikeWFE - Missing 'aperture_stop'",
        ),
        pytest.param(
            {
                "item": "ZernikeWFE",
                "radius": 1.1,
                "coefficients": [],
                "aperture_stop": 4.4,
            },
            ValueError,
            r"Expecting a list of numbers for parameter \'coefficients\'",
            id="ZernikeWFE - No 'coefficients'",
        ),
        pytest.param(
            {
                "item": "SineWaveWFE",
                "amplitude": 3.3,
                "rotation": 4.4,
            },
            KeyError,
            r"Missing one of these parameters: \'spatialfreq\', \'amplitude\', \'rotation\'",
            id="SineWaveWFE - Missing 'spatialfreq'",
        ),
        pytest.param(
            {
                "item": "SineWaveWFE",
                "spatialfreq": 2.2,
                "rotation": 4.4,
            },
            KeyError,
            r"Missing one of these parameters: \'spatialfreq\', \'amplitude\', \'rotation\'",
            id="SineWaveWFE - Missing 'amplitude'",
        ),
        pytest.param(
            {
                "item": "SineWaveWFE",
                "spatialfreq": 2.2,
                "amplitude": 3.3,
            },
            KeyError,
            r"Missing one of these parameters: \'spatialfreq\', \'amplitude\', \'rotation\'",
            id="SineWaveWFE - Missing 'rotation'",
        ),
    ],
)
def test_create_optical_item_error(dct: Mapping, exp_error, exp_msg):
    """Test function 'create_optical_item' with wrong inputs."""
    with pytest.raises(exp_error, match=exp_msg):
        _ = create_optical_item(
            dct,
            default_wavelength=Quantity(300, unit="nm"),
        )


class PhotonType(Enum):
    """Used only for testing."""

    NoPhoton = auto()
    Photon_2D = auto()
    Photon_3D = auto()


@pytest.mark.parametrize(
    "apply_jitter",
    [pytest.param(True, id="With jitter"), pytest.param(False, id="Without jitter")],
)
@pytest.mark.parametrize(
    "photon_type, env_wavelength, wavelength",
    [
        pytest.param(
            PhotonType.Photon_2D, None, 620.0, id="Mono. with wavelength (float)"
        ),
        pytest.param(PhotonType.Photon_2D, None, 620, id="Mono. with wavelength (int)"),
        pytest.param(PhotonType.Photon_2D, 620.0, None, id="Mono. without wavelength"),
        pytest.param(
            PhotonType.Photon_3D,
            None,
            (620.0, 680.0),
            id="Multi with wavelength (float)",
        ),
        pytest.param(
            PhotonType.Photon_3D, None, (620, 680), id="Multi with wavelength (int)"
        ),
        pytest.param(
            PhotonType.Photon_3D, None, (600.0, 700.0), id="Multi with wavelength2"
        ),
        pytest.param(
            PhotonType.Photon_3D,
            WavelengthHandling(cut_on=620.0, cut_off=680.0, resolution=2),
            None,
            id="Multi without wavelength",
        ),
    ],
)
@pytest.mark.parametrize(
    "geo_pixel_scale, pixelscale",
    [
        pytest.param(None, 1.65, id="With pixel_scale"),
        pytest.param(1.65, None, id="Without pixel_scale"),
    ],
)
@pytest.mark.parametrize(
    "optical_system",
    [pytest.param([{"item": "CircularAperture", "radius": 1.0}], id="circle")],
)
def test_optical_psf(
    apply_jitter: bool,
    photon_type: PhotonType,
    env_wavelength: WavelengthHandling | float | None,
    wavelength: float | tuple[float, float] | None,
    geo_pixel_scale: float | None,
    pixelscale: float | None,
    optical_system,
    ccd_100x100_no_photon: CCD,
):
    """Test function 'optical_psf'."""
    detector = ccd_100x100_no_photon
    detector.environment._wavelength = env_wavelength
    detector.geometry._pixel_scale = geo_pixel_scale

    # Check if 'photon' is empty
    assert detector.photon == Photon(geo=detector.geometry)
    assert detector.photon.ndim == 0

    # Add Photons (or not)
    if photon_type is PhotonType.NoPhoton:
        # Do nothing
        pass
    elif photon_type is PhotonType.Photon_2D:
        detector.photon.array = np.zeros(
            shape=(detector.geometry.row, detector.geometry.col),
            dtype=float,
        )
    else:
        detector.photon.array_3d = xr.DataArray(
            np.zeros(
                shape=(3, detector.geometry.row, detector.geometry.col),
                dtype=float,
            ),
            dims=["wavelength", "y", "x"],
            coords={"wavelength": [620.0, 640.0, 680.0]},
        )

    optical_psf(
        detector=detector,
        fov_arcsec=5,
        optical_system=optical_system,
        wavelength=wavelength,
        pixel_scale=pixelscale,
        apply_jitter=apply_jitter,
        jitter_sigma=0.007,
    )


@dataclass
class ParamError:
    """Define parameters for 'test_optical_psf_error'."""

    photon_type: PhotonType
    env_wavelength: WavelengthHandling | float | None
    wavelength: float | tuple[float, float] | None
    geo_pixel_scale: float | None
    pixelscale: float | None
    fov_arcsec: float
    optical_system: list | None
    exp_exception: type[Exception]
    exp_error: str


@pytest.mark.parametrize(
    "param",
    [
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=0.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"Expecting strictly positive value for \'fov_arcsec\'",
            ),
            id="fov is zero",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=-1.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"Expecting strictly positive value for \'fov_arcsec\'",
            ),
            id="fov is negative",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[],
                exp_exception=ValueError,
                exp_error=r"Parameter \'optical_system\' does not contain any optical element",
            ),
            id="No optical_system",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=None,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error="Pixel scale is not defined",
            ),
            id="No pixelscale",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=0.0,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'pixelscale\' must be strictly positive",
            ),
            id="pixelscale is zero",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=-1.0,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'pixelscale\' must be strictly positive",
            ),
            id="pixelscale is negative",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=None,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"Wavelength is not defined",
            ),
            id="No Wavelength",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be strictly positive",
            ),
            id="Wavelength is zero (int)",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=0.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be strictly positive",
            ),
            id="Wavelength is zero (float)",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=-0.1,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be strictly positive",
            ),
            id="Wavelength is zero",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=(0, 680),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be increasing",
            ),
            id="Bad multi wavelength1",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=(-1.0, 680.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be increasing",
            ),
            id="Bad multi wavelength2",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=(680, 680.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be increasing",
            ),
            id="Bad multi wavelength3",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=(680.0, 620.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"\'wavelength\' must be increasing",
            ),
            id="Bad multi wavelength4",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.NoPhoton,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"A \'detector.photon\' 2D is expected",
            ),
            id="Monochromatic - No photon",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=620.0,
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"A \'detector.photon\' 2D is expected",
            ),
            id="Monochromatic - Photon3D",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.NoPhoton,
                env_wavelength=None,
                wavelength=(620.0, 680.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"A \'detector.photon\' 3D is expected",
            ),
            id="Multiwavelength - No Photon",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_2D,
                env_wavelength=None,
                wavelength=(620.0, 680.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error=r"A \'detector.photon\' 3D is expected",
            ),
            id="Multiwavelength - Photon2D",
        ),
        pytest.param(
            ParamError(
                photon_type=PhotonType.Photon_3D,
                env_wavelength=None,
                wavelength=(300.0, 400.0),
                geo_pixel_scale=None,
                pixelscale=1.65,
                fov_arcsec=5.0,
                optical_system=[{"item": "CircularAperture", "radius": 1.0}],
                exp_exception=ValueError,
                exp_error="The provided wavelength range",
            ),
            id="Cannot filter wavelength",
        ),
        # pytest.param(
        #     ParamError(
        #         photon_type=PhotonType.Photon_2D,
        #         env_wavelength=None,
        #         wavelength=620.0,
        #         geo_pixel_scale=None,
        #         pixelscale=1.65,
        #         fov_arcsec=5.,
        #         optical_system=[{"item": "CircularAperture", "radius": 1.0}],
        #         exp_exception=ValueError,
        #         exp_error="foo",
        #     ),
        #     id="good",
        # ),
    ],
)
def test_optical_psf_error(
    param: ParamError,
    ccd_100x100_no_photon: CCD,
):
    """Test function 'optical_psf' with wrong inputs."""
    assert isinstance(param, ParamError)

    detector = ccd_100x100_no_photon
    detector.environment._wavelength = param.env_wavelength
    detector.geometry._pixel_scale = param.geo_pixel_scale

    # Check if 'photon' is empty
    assert detector.photon == Photon(geo=detector.geometry)
    assert detector.photon.ndim == 0

    # Add Photons (or not)
    if param.photon_type is PhotonType.NoPhoton:
        # Do nothing
        pass
    elif param.photon_type is PhotonType.Photon_2D:
        detector.photon.array = np.zeros(
            shape=(detector.geometry.row, detector.geometry.col),
            dtype=float,
        )
    else:
        detector.photon.array_3d = xr.DataArray(
            np.zeros(
                shape=(3, detector.geometry.row, detector.geometry.col),
                dtype=float,
            ),
            dims=["wavelength", "y", "x"],
            coords={"wavelength": [620.0, 640.0, 680.0]},
        )

    with pytest.raises(param.exp_exception, match=param.exp_error):
        optical_psf(
            detector=detector,
            fov_arcsec=param.fov_arcsec,
            optical_system=param.optical_system,
            wavelength=param.wavelength,
            pixel_scale=param.pixelscale,
            apply_jitter=False,
            jitter_sigma=0.007,
        )
