#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import astropy.units as u
import pytest
import xarray as xr
from astropy.table import Table
from astropy.utils.diff import diff_values
from numpy.testing import assert_allclose
from pytest_mock import MockerFixture  # pip install pytest-mock
from scopesim import Source
from synphot import SourceSpectrum

from pyxel.detectors import CCD
from pyxel.models.scene_generation import generate_scene


@pytest.fixture
def source_ids() -> list[int]:
    """Return unique source identifier from the GAIA database"""
    return [66727234683960320, 65214031805717376, 65225851555715328, 65226195153096192]


@pytest.fixture
def positions(source_ids: list[int]) -> xr.Dataset:
    """Return source objects as a Dataset."""
    source_id = xr.DataArray(
        source_ids,
        dims="source_id",
    )

    ds = xr.Dataset(coords={"source_id": source_id})
    ds["ra"] = xr.DataArray(
        [56.760485086776846, 56.74561610052, 56.726951308177455, 56.736700233543914],
        dims="source_id",
        attrs={"units": "deg"},
    )

    ds["dec"] = xr.DataArray(
        [24.149991010998, 24.089174782613, 24.111718134110, 24.149504345515],
        dims="source_id",
        attrs={"units": "deg"},
    )
    ds["has_xp_sampled"] = xr.DataArray([True] * 4, dims="source_id")
    ds["phot_bp_mean_mag"] = xr.DataArray(
        [14.734505, 12.338661, 14.627676, 14.272486],
        dims="source_id",
        attrs={"units": "mag"},
    )
    ds["phot_g_mean_mag"] = xr.DataArray(
        [14.433147, 11.940813, 13.91212, 13.613182],
        dims="source_id",
        attrs={"units": "mag"},
    )
    ds["phot_rp_mean_mag"] = xr.DataArray(
        [13.954827, 11.368548, 13.091035, 12.804853],
        dims="source_id",
        attrs={"units": "mag"},
    )

    return ds


@pytest.fixture
def positions_table(positions: xr.Dataset) -> Table:
    """Return source objects as an Astropy Table."""
    table = Table.from_pandas(positions.to_pandas().reset_index())
    table["ra"].unit = u.deg
    table["dec"].unit = u.deg
    table["phot_bp_mean_mag"].unit = u.mag
    table["phot_g_mean_mag"].unit = u.mag
    table["phot_rp_mean_mag"].unit = u.mag

    return table


@pytest.fixture
def wavelengths() -> xr.DataArray:
    """Return wavelengths."""
    return xr.DataArray(
        [336.0, 338.0, 1018.0, 1020.0],
        dims="wavelength",
        attrs={"dims": "nm"},
    )


@pytest.fixture
def spectra1(wavelengths: xr.DataArray) -> xr.Dataset:
    """Return spectra for the first object."""
    ds = xr.Dataset(coords={"wavelength": wavelengths})
    ds["flux"] = xr.DataArray(
        [4.1858373e-17, 4.1012171e-17, 1.3888942e-17, 1.3445790e-17],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )
    ds["flux_error"] = xr.DataArray(
        [5.8010027e-18, 4.3436358e-18, 4.2265315e-18, 4.1775913e-18],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )

    return ds


@pytest.fixture
def spectra2(wavelengths: xr.DataArray) -> xr.Dataset:
    """Return spectra for the second object."""
    ds = xr.Dataset(coords={"wavelength": wavelengths})
    ds["flux"] = xr.DataArray(
        [3.0237057e-16, 2.9785625e-16, 2.4918341e-16, 2.5573007e-16],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )
    ds["flux_error"] = xr.DataArray(
        [2.8953863e-17, 2.1999507e-17, 1.7578710e-17, 1.7167379e-17],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )

    return ds


@pytest.fixture
def spectra3(wavelengths: xr.DataArray) -> xr.Dataset:
    """Return spectra for the third object."""
    ds = xr.Dataset(coords={"wavelength": wavelengths})
    ds["flux"] = xr.DataArray(
        [2.0389929e-17, 2.2613652e-17, 6.1739404e-17, 6.5074511e-17],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )
    ds["flux_error"] = xr.DataArray(
        [6.6810894e-18, 5.1004213e-18, 7.3332771e-18, 7.2768021e-18],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )

    return ds


@pytest.fixture
def spectra4(wavelengths: xr.DataArray) -> xr.Dataset:
    """Return spectra for the fourth object."""
    ds = xr.Dataset(coords={"wavelength": wavelengths})
    ds["flux"] = xr.DataArray(
        [2.4765946e-17, 2.1556272e-17, 9.0950110e-17, 9.1888827e-17],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )
    ds["flux_error"] = xr.DataArray(
        [6.9233657e-18, 5.2693949e-18, 7.4365125e-18, 7.1868190e-18],
        dims="wavelength",
        attrs={"dims": "W / (nm * m^2)"},
    )

    return ds


@pytest.fixture
def spectra_dct(
    source_ids: list[int],
    spectra1: xr.Dataset,
    spectra2: xr.Dataset,
    spectra3: xr.Dataset,
    spectra4: xr.Dataset,
) -> dict[int, Table]:
    """Return spectra for the four objects as dictionary."""
    dct = {}
    for source_id, spectra in zip(source_ids, [spectra1, spectra2, spectra3, spectra4]):
        table: Table = Table.from_pandas(spectra.to_pandas().reset_index())
        table["wavelength"].unit = u.nm
        table["flux"].unit = u.W / (u.nm * u.m * u.m)
        table["flux_error"].unit = u.W / (u.nm * u.m * u.m)

        dct[source_id] = table

    return dct


def test_scene_generator(
    mocker: MockerFixture,
    ccd_10x10: CCD,
    positions_table: Table,
    spectra_dct: dict[int, Table],
    wavelengths: xr.DataArray,
):
    """Test model 'scene_generator."""

    # Mock function 'pyxel.models.scene_generation.scene_generator.retrieve_objects_from_gaia'
    # When this function will be called (with any parameters), it will always return this tuple
    # (positions_table, spectra_dct)
    mocker.patch(
        target="pyxel.models.scene_generation.scene_generator.retrieve_objects_from_gaia",
        return_value=(positions_table, spectra_dct),
    )

    # Run model
    detector: CCD = ccd_10x10
    generate_scene(
        detector=detector,
        right_ascension=0.0,  # This parameter is not important
        declination=0.0,  # This parameter is not important
        fov_radius=0.0,  # This parameter is not important
    )

    # Check outputs
    obj = detector.scene.data
    assert isinstance(obj, Source)

    # Check .fields
    assert len(obj.fields) == 1
    first_field: Table = obj.fields[0]

    expected_x = 3600 * (positions_table["ra"] - positions_table["ra"].mean()).data
    expected_y = 3600 * (positions_table["dec"] - positions_table["dec"].mean()).data

    exp_field = Table(
        {
            "x": expected_x * u.arcsec,
            "y": expected_y * u.arcsec,
            "ref": [0, 1, 2, 3],
            "weight": [14.734505, 12.338661, 14.627676, 14.272486] * u.mag,
        }
    )

    assert all(diff_values(first_field, exp_field))

    # Check .spectra
    wavelengths_nm: u.Quantity = wavelengths.to_numpy() * u.nm
    assert len(obj.spectra) == 4

    source_spectrum: SourceSpectrum = obj.spectra[0]
    spectra = source_spectrum(wavelengths_nm)
    assert_allclose(
        spectra.value, [0.00070802, 0.00069783, 0.00071177, 0.00069041], rtol=1e-5
    )

    source_spectrum: SourceSpectrum = obj.spectra[1]
    spectra = source_spectrum(wavelengths_nm)
    assert_allclose(
        spectra.value, [0.00511449, 0.00506812, 0.01276998, 0.01313122], rtol=1e-5
    )

    source_spectrum: SourceSpectrum = obj.spectra[2]
    spectra = source_spectrum(wavelengths_nm)
    assert_allclose(
        spectra.value, [0.00034489, 0.00038478, 0.00316398, 0.00334145], rtol=1e-5
    )

    source_spectrum: SourceSpectrum = obj.spectra[3]
    spectra = source_spectrum(wavelengths_nm)
    assert_allclose(
        spectra.value, [0.00041891, 0.00036679, 0.00466095, 0.00471831], rtol=1e-5
    )
