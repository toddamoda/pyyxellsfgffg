#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.
import astropy
import astropy.units as u
import scopesim
import scopesim_templates
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astroquery.gaia import Gaia
from scopesim_templates.rc import Source
from scopesim_templates.utils import general_utils as gu

from pyxel.detectors import Detector


def load_objects_from_gaia(
    right_ascension: float,
    declination: float,
    fov_width: float,
    fov_heigth: float,
) -> astropy.table.table.Table:
    """Load objects from GAIA Catalog for given coordinactes and FOV.

    Parameters
    ----------
    right_ascension : float
        RA coordinates of object.
    declination : float
        DEC coordinates of object.
    fov_width : float
        Width of FOV of optics.
    fov_heigth : float
        Height of FOV of optics.

    Returns
    -------
    objects : astropy.table.table.Table
        Objects in the FOV at given coordinates found by the GAIA catalog.
    """
    # The coordinates of the object
    # Frame: Type of coordinate frame this SkyCoord should represent.
    # Default now is International Celestial Reference System (ICRS).
    coord = SkyCoord(
        ra=right_ascension,
        dec=declination,
        frame="icrs",
    )
    # alternative to give over ra and dec and calculate the sycoords one could directly use skycoords as input like alex
    # coords_detector: SkyCoord (ICRS): (ra, dec) in deg. # Coordinates of the pointing of the telescope.

    # The FOV of the optics limits the region in the sky together with the coordinates of the pointing of the optics.
    # alternative: fov_radius, if we assume its always round
    width = fov_width * u.arcsec
    height = fov_heigth * u.arcsec

    # Unlimited rows.
    Gaia.ROW_LIMIT = -1
    # we get the data from GAIA DR3 at the coordinates
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

    # Query for the catalog to search area with coordinates in FOV of optics.
    objects = Gaia.query_object_async(
        coordinate=coord,
        width=width,
        height=height,
    )

    return objects


def generate_scene(
    detector: Detector,
    right_ascension: float,
    declination: float,
    fov_width: float,
    fov_heigth: float,
    filter_name: str = "H",  # or list?
    spectrum_type: str = "A0V",  # or list?
    # magnitude:
):
    objects = load_objects_from_gaia(
        right_ascension=right_ascension,
        declination=declination,
        fov_width=fov_width,
        fov_heigth=fov_heigth,
    )

    # Convert the positions to arcseconds and center around 0.0, 0.0.
    # The centering is necessary because ScopeSIM cannot actually 'point' the telescope.
    x = 3600 * (objects["ra"] - objects["ra"].mean())
    y = 3600 * (objects["dec"] - objects["dec"].mean())
    # Select a nice magnitude of the sources.
    mags = objects["phot_g_mean_mag"]  # could be an input as well

    scene = scopesim_templates.stellar.stars(
        filter_name=filter_name,
        spec_types=spectrum_type,
        amplitudes=mags,
        x=x,
        y=y,
    )

    detector.scene = scene
