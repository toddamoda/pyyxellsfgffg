#  Copyright (c) European Space Agency, 2020.
#
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Utility packages for Scene Generation models."""

from pathlib import Path

import xarray as xr
from astropy.table import QTable
from astropy.units import spectral_density


# TODO: Use 'pyckles' to retrieve this spectrum ?
def get_vega_a0v_table() -> QTable:
    """Get the reference A0V spectrum from Vega.

    This function returns the spectral energy distribution of Vega,
    the A0V spectral standard.

    The data is useful as a standard reference spectrum.

    Returns
    -------
    QTable
        The A0V spectrum.

    Examples
    --------
    >>> from pyxel.models.scene_generation.utils import get_vega_a0v_table
    >>> spectrum = get_vega_a0v_table()
    >>> spectrum
    wavelength          flux
     Angstrom  erg / (Angstrom s cm2)
    ---------- ----------------------
        1150.0               0.181751
        1155.0               0.203323
           ...                    ...
       24995.0               0.006986
       25000.0               0.006983
    Length = 4771 rows
    """
    import pyxel.models.scene_generation.data as module

    # Load the A0V Vega spectrum from a local file
    folder = Path(module.__path__[0])
    table = QTable.read(folder / "a0v.parquet")
    return table


def get_vega_a0v_spectrum() -> xr.DataArray:
    """Get the reference A0V spectrum from Vega as an DataArray.

    This function returns the spectral energy distribution of Vega,
    the A0V spectral standard.

    Returns
    -------
    DataArray
        The A0V spectrum.

    See Also
    --------
    get_spectra_a0v_table : Return the original spectrum as a QTable.

    Examples
    --------
    >>> from pyxel.models.scene_generation.utils import get_vega_a0v_spectrum
    >>> data = get_vega_a0v_spectrum()
    >>> data
    <xarray.DataArray 'A0V' (wavelength: 4771)> Size: 38kB
    array([1.05219908e+11, 1.18220219e+11, 8.29581735e+10, ...,
           8.79359985e+10, 8.79032617e+10, 8.78830900e+10], shape=(4771,))
    Coordinates:
      * wavelength  (wavelength) float64 38kB 115.0 115.5 116.0 ... 2.5e+03 2.5e+03
    Attributes:
        units:          ph / (nm s cm2)
        standard_name:  Flux
    """
    table: QTable = get_vega_a0v_table()

    # Convert wavelength from 'Angstrom' to 'nm'
    wavelength = table["wavelength"].to("nm")

    # Convert flux from 'erg / (Angstrom s cm2)' to 'ph / (nm s cm2)'
    flux = table["flux"].to(
        "ph / (nm s cm2)", equivalencies=spectral_density(wavelength)
    )

    # Build the DataArray
    data_array = xr.DataArray(
        flux.value,
        dims="wavelength",
        coords={"wavelength": wavelength.value},
        name="A0V",
    )

    data_array["wavelength"].attrs = {
        "units": str(wavelength.unit),
        "standard_name": "Wavelength",
    }
    data_array.attrs = {"units": str(flux.unit), "standard_name": "Flux"}

    return data_array
