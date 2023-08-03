#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Scene generator creates Scopesim Source object."""
import astropy.units as u
import numpy as np
import requests
import scopesim
from astropy.table import Table
from astroquery.gaia import Gaia
from specutils import Spectrum1D
from synphot import SourceSpectrum

from pyxel.data_structure import Scene
from pyxel.detectors import Detector


def load_objects_from_gaia(
    right_ascension: float,
    declination: float,
    fov_radius: float,
) -> scopesim.Source:
    """Load objects from GAIA Catalog for given coordinates and FOV.

    Parameters
    ----------
    right_ascension: float
        RA coordinate in degree.
    declination: float
        DEC coordinate in degree.
    fov_radius: float
        FOV radius of teescope optics.

    Returns
    -------
    scopesim.Source
        Scopesim Source object in the FOV at given coordinates found by the GAIA catalog.

    Raises
    ------
    ConnectionError
        If the connection to the GAIA database cannot be established.
    """

    # Unlimited rows.
    Gaia.ROW_LIMIT = -1
    # we get the data from GAIA DR3
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

    try:
        # Query for the catalog to search area with coordinates in FOV of optics.
        job = Gaia.launch_job_async(
            f"SELECT source_id, ra, dec, has_xp_sampled, phot_bp_mean_mag, phot_g_mean_mag, phot_rp_mean_mag \
        FROM gaiadr3.gaia_source \
        WHERE CONTAINS(POINT('ICRS', ra, dec),CIRCLE('ICRS',{right_ascension},{declination},{fov_radius}))=1 \
        AND has_xp_sampled = 'True'"
        )

        # get the results from the query job
        result = job.get_results()
        # set parameters to load data from Gaia catalog
        retrieval_type = "XP_SAMPLED"
        data_release = "Gaia DR3"
        data_structure = "COMBINED"
        # load spectra from stars
        spectra = Gaia.load_data(
            ids=result["source_id"],
            retrieval_type=retrieval_type,
            data_release=data_release,
            data_structure=data_structure,
        )
    except requests.HTTPError as exc:
        raise ConnectionError(
            "Error when trying to communicate with the Gaia database"
        ) from exc

    # save key
    key = f"{retrieval_type}_{data_structure}.xml"

    # Source IDs are stored in the table metadata with accessing through the key
    source_ids = [
        product.get_field_by_id("source_id").value for product in spectra[key]
    ]

    d = {}
    spec_list = []
    # loop through all sources and create Source Spectrum to attach to a list of spectra
    for i, sid in zip(range(0, len(source_ids)), source_ids):
        d[sid] = spectra["XP_SAMPLED_COMBINED.xml"][i].to_table()
        output = spectra["XP_SAMPLED_COMBINED.xml"][i].to_table()
        # create 1D spectrum
        spec = Spectrum1D(
            spectral_axis=output["wavelength"] * u.m / u.m,
            flux=output["flux"] * u.m / u.m,
        )
        # turn 1D spectrum into synphot Source spectrum
        sp = SourceSpectrum.from_spectrum1d(spec)
        spec_list.append(sp)

    # Create astropy.table with relevant input parameters

    # Convert the positions to arcseconds and center around 0.0, 0.0.
    # The centering is necessary because ScopeSIM cannot actually 'point' the telescope.
    x = 3600 * (result["ra"] - result["ra"].mean())
    y = 3600 * (result["dec"] - result["dec"].mean())

    # set index as ref.
    ref = np.arange(0, (len(result)), dtype=int)

    # select magnitude band. Could be an input parameter of model.
    weight = result["phot_bp_mean_mag"]

    tbl = Table(
        names=["x", "y", "ref", "weight"],
        data=[x, y, ref, weight],
        units=[u.arcsec, u.arcsec, None, None],
    )

    source = scopesim.Source(table=tbl, spectra=spec_list)
    return source


def generate_scene(
    detector: Detector,
    right_ascension: float,
    declination: float,
    fov_radius: float,
):
    """Generate scene from scopesim Source object loading stars from the GAIA catalog.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    right_ascension: float
        RA coordinate in degree.
    declination: float
        DEC coordinate in degree.
    fov_radius: float
        FOV radius of telescope optics.

    """
    source: scopesim.Source = load_objects_from_gaia(
        right_ascension=right_ascension, declination=declination, fov_radius=fov_radius
    )

    detector.scene = Scene(source)
