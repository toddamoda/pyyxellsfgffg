#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections.abc import Mapping, Sequence

import astropy.units as u
import numpy as np
import pytest
import xarray as xr

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.models.photon_collection import optical_psf
from pyxel.models.photon_collection.poppy import (
    CircularAperture,
    HexagonAperture,
    MultiHexagonalAperture,
    RectangleAperture,
    SecondaryObscuration,
    SineWaveWFE,
    SquareAperture,
    ThinLens,
    ZernikeWFE,
    create_optical_parameter,
)

_ = pytest.importorskip("poppy")


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


@pytest.mark.parametrize(
    "dct, exp_parameter",
    [
        pytest.param(
            {}, None, marks=pytest.mark.xfail(raises=KeyError, strict=True), id="Empty"
        ),
        pytest.param(
            {"item": "CircularAperture", "radius": 3.14},
            CircularAperture(radius=3.14 * u.m),
            id="CircularAperture",
        ),
        pytest.param(
            {
                "item": "ThinLens",
                "nwaves": 1.1,
                "radius": 2.2,
                "reference_wavelength": 600.0,
            },
            ThinLens(nwaves=1.1, radius=2.2 * u.m, reference_wavelength=600.0 * u.nm),
            id="ThinLens",
        ),
        pytest.param(
            {"item": "SquareAperture", "size": 1},
            SquareAperture(size=1 * u.m),
            id="SquareAperture",
        ),
        pytest.param(
            {"item": "RectangularAperture", "width": 1.1, "height": 2.2},
            RectangleAperture(width=1.1 * u.m, height=2.2 * u.m),
            id="RectangularAperture",
        ),
        pytest.param(
            {"item": "HexagonAperture", "side": 1.1},
            HexagonAperture(side=1.1 * u.m),
            id="HexagonAperture",
        ),
        pytest.param(
            {"item": "MultiHexagonalAperture", "side": 1.1, "rings": 2, "gap": 3.3},
            MultiHexagonalAperture(side=1.1 * u.m, rings=2, gap=3.3 * u.m),
            id="MultiHexagonalAperture",
        ),
        pytest.param(
            {
                "item": "SecondaryObscuration",
                "secondary_radius": 1.1,
                "n_supports": 2,
                "support_width": 3.3,
            },
            SecondaryObscuration(
                secondary_radius=1.1 * u.m, n_supports=2, support_width=3.3 * u.m
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
            ZernikeWFE(radius=1.1 * u.m, coefficients=[2.2, 3.3], aperture_stop=4.4),
            id="ZernikeWFE",
        ),
        pytest.param(
            {
                "item": "SineWaveWFE",
                "spatialfreq": 2.2,
                "amplitude": 3.3,
                "rotation": 4.4,
            },
            SineWaveWFE(
                spatialfreq=2.2 * (1 / u.m), amplitude=3.3 * u.um, rotation=4.4
            ),
            id="SineWaveWFE",
        ),
    ],
)
def test_create_optical_parameter(dct: Mapping, ccd_3x3: CCD, exp_parameter):
    """Test function 'create_optical_parameter'."""
    parameter = create_optical_parameter(
        dct, selected_wavelength=ccd_3x3.environment.wavelength * u.nm
    )

    assert parameter == exp_parameter


@pytest.mark.parametrize(
    "wavelength, fov_arcsec, optical_system",
    [
        pytest.param(600, 5, [{"item": "CircularAperture", "radius": 1.0}], id="valid"),
        # pytest.param(
        #     -1,
        #     5,
        #     [{"item": "CircularAperture", "radius": 3.0}],
        #     marks=pytest.mark.xfail(raises=ValueError, strict=True),
        #     id="Negative 'wavelength'",
        # ),
        # pytest.param(
        #     600,
        #     -1,
        #     [{"item": "CircularAperture", "radius": 3.0}],
        #     marks=pytest.mark.xfail(raises=ValueError, strict=True),
        #     id="Negative 'fov_arcsec'",
        # ),
    ],
)
def test_optical_psf(
    ccd_3x3: CCD,
    wavelength: float,
    fov_arcsec: float,
    optical_system: Sequence[Mapping],
):
    """Test input parameters for function 'optical_psf'."""
    optical_psf(
        detector=ccd_3x3,
        wavelength=wavelength,
        fov_arcsec=fov_arcsec,
        optical_system=optical_system,
    )


@pytest.mark.parametrize(
    "wavelengths, fov_arcsec, optical_system",
    [
        pytest.param(
            (600, 700),
            5,
            [{"item": "CircularAperture", "radius": 3.0}],
            id="valid",
        ),
    ],
)
def test_optical_psf_multiwavelength(
    ccd_4x5_multi_wavelength: CCD,
    wavelengths: tuple[float, float],
    fov_arcsec: float,
    optical_system: Sequence[Mapping],
):
    """Test input parameters for function 'optical_psf'."""
    optical_psf(
        detector=ccd_4x5_multi_wavelength,
        wavelength=wavelengths,
        fov_arcsec=fov_arcsec,
        optical_system=optical_system,
    )
