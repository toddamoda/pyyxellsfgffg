# Copyright (c) 2023 Alejandro Camazon Pinilla, University of Florida, ARRAKIHS Mission Consortium
#
# acamazon@ufl.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Calculation of the straylight on the detector."""
from typing import Callable

import healpy as hp
import numpy as np
import pandas as pd
from astropy import constants as cte
from astropy import units as u
from astropy import wcs
from astropy.coordinates import SkyCoord, get_moon  # High-level coordinates
from astropy.time import Time
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from scipy.integrate import quad
from tqdm import tqdm

import pyxel.models.photon_collection.arrakihs_tools as tools
from pyxel.detectors import Detector
from pyxel.models.photon_collection.NDI_functions import NDI_iSIM170
from pyxel.util import fit_into_array

#################
### CONSTANTS
#################

T_sun = 5778
T_moon = 190
T_earth = 300
moon_rad = 1737.4 * u.km

pii = np.pi  # setting pii value
h_planck = 6.626075540e-27  # Planck constant in ergs s
c_speed = 2.99792458e10  # speed of light in vaccuum in cm/s
kb = 1.380658e-16  # Boltzmann's const CGS
R_earth = 6378.0  # km
# Earth surface brightness
Rt = R_earth * 1e3
moon_area = np.pi * moon_rad**2
solid_angle_sun = cte.R_sun**2 / (cte.au**2)

m_sun = -26.74  # solar magnitude
m_moon = -12.7  # moon magnitude
albedo_earth = 0.3
albedo_moon = 0.12


###################################################
##### Definition of the detector pixel coordinates:
###################################################


def indextoradec(nside: float, index: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    theta, phi = hp.pixelfunc.pix2ang(nside, index)
    return np.degrees(np.pi * 2.0 - phi), -np.degrees(theta - np.pi / 2.0)


def radectoindex(nside: float, ra: np.ndarray, dec: np.ndarray) -> np.ndarray:
    return hp.pixelfunc.ang2pix(nside, np.radians(-dec + 90.0), np.radians(360.0 - ra))


#############################################################
##### Function for the detector-to-object angular separation:
#############################################################


def angular_separation_single(
    coords_detector: SkyCoord,
    coords_object: SkyCoord,
    pixel_scale: float,
    image: np.ndarray,
) -> np.ndarray:
    """Calculate the angular distance from every pixel of the detector to every object.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    coords_object: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the object responsible of the straylight.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    image: 2-d array.
            Image of the detector (just for the size)

    """
    list_detector = tools.detector_coordinates(coords_detector, image, pixel_scale)

    sep_ang = coords_object.separation(list_detector).deg

    return sep_ang


def angular_separation_list(
    coords_detector: SkyCoord,
    coords_object: list,
    pixel_scale: float,
    image: np.ndarray,
) -> np.ndarray:
    """Calculate the angular distance from every pixel of the detector to every object.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    coords_object: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the object responsible of the straylight.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    image: 2-d array.
            Image of the detector (just for the size)
    """

    list_detector = tools.detector_coordinates(coords_detector, image, pixel_scale)

    sep_ang = np.zeros([len(coords_object), image.shape[0], image.shape[1]])
    for i in tqdm(range(len(coords_object))):
        sep_ang[i] = coords_object[i].separation(list_detector).deg

    return sep_ang


################################################
##### Definition of the spectrum of the objects:
################################################


### Sun spectrum:
def blackbody_sun(x: np.ndarray):
    bb_out = (
        pii
        * (2.0 * h_planck * (c_speed**2.0) / (x * (x * 1.0e-8) ** 4.0))
        / (np.exp(h_planck * c_speed / ((x * 1.0e-8) * kb * T_sun)) - 1.0)
    )  # units [erg/s/cm2/A]
    return bb_out / (
        h_planck * c_speed / (x * 1.0e-8)
    )  # units [ # photons / s / cm2 / A ]


### Moon spectrum:
def moon_spectrum(obs_date: Time, x: np.ndarray):
    distance_moon_earth = get_moon(obs_date).distance
    solid_angle_moon_sun = cte.R_sun**2 / (cte.au + distance_moon_earth.to(u.m)) ** 2
    # reflected from the sun
    bb_moon = blackbody_sun(x) * solid_angle_moon_sun * albedo_moon
    # thermal emission
    bb_out = (
        pii
        * (2.0 * h_planck * (c_speed**2.0) / (x * (x * 1.0e-8) ** 4.0))
        / (np.exp(h_planck * c_speed / ((x * 1.0e-8) * kb * T_moon)) - 1.0)
    )  # units [erg/s/cm2/A]

    return bb_moon + 0.95 * (bb_out) / (
        h_planck * c_speed / (x * 1.0e-8)
    )  # units [ # photons / s / cm2 / A ]


### moon flux integrated:
def moon_flux(obs_date: Time, wave_begin, wave_end):
    wv_beg = wave_begin * 10  # from nm to AA
    wv_end = wave_end * 10  # from nm to AA
    integ_flux, integ_flux_error = quad(
        lambda x: moon_spectrum(obs_date, x), wv_beg, wv_end
    )  # phot / s / cm^2
    return integ_flux, integ_flux_error


### Earth emission spectrum:
def blackbody_earth(x: np.ndarray):
    bb_out = (
        pii
        * (2.0 * h_planck * (c_speed**2.0) / (x * (x * 1.0e-8) ** 4.0))
        / (np.exp(h_planck * c_speed / ((x * 1.0e-8) * kb * T_earth)) - 1.0)
    )  # units [erg/s/cm2/A]
    return bb_out / (
        h_planck * c_speed / (x * 1.0e-8)
    )  # units [ # photons / s / cm2 / A ]


### Total Earth emission spectrum on the eclipse:
def earth_spectrum_night(obs_date: Time, x: np.ndarray):
    distance_moon_earth = get_moon(obs_date).distance
    solid_angle_moon = moon_rad**2 / distance_moon_earth**2
    earth_moon_ref = moon_spectrum(obs_date, x) * albedo_earth * solid_angle_moon / 2
    earth_emiss = blackbody_earth(x)

    return earth_moon_ref + earth_emiss


### Total Earth emission spectrum on the sunlight:
def earth_spectrum_day(x: np.ndarray):
    earth_sun_ref = blackbody_sun(x) * albedo_earth * solid_angle_sun
    earth_emiss = blackbody_earth(x)

    return earth_sun_ref + earth_emiss


##########################
##### Straylight of Earth:
##########################


def earth_straylight(
    NDI_function: Callable,
    sat_distance: float,
    image: np.ndarray,
    pixel_scale: float,
    pix_size: float,
    wave_begin: float,
    wave_end: float,
    obs_date: Time,
    sat_ra_dev: float = 0.0,
    sat_dec_dev: float = 0.0,
):
    """Calculate the straylight from the earth in a LEO telescope.

    Parameters
    ----------
    NDI_function: func
            Normalized Detector Irradiance of the telescope
    sat_distance: float (in km).
            Altitude of the satellite (orbit).
    image: 2-d array.
            Image of the detector (just for the size)
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    pix_size: float (in microns)
            Physical pixel length.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    obs_date: Time object: scale='utc' format='iso'.
            Time of the observation.
    sat_ra_dev: float or int (in degrees).
            RA degrees deviation of the initial pointing direction (RA_0 = 90). Default: 0 degrees
    sat_dec_dev: float or int (in degrees).
            DEC degrees deviation of the initial pointing direction (DEC_0 = 0).  Default: 0 degrees
    Note:
        The function returns a map in photons/s units.
    """
    image_amp = np.zeros([int(image.shape[0] + 500), int(image.shape[1] + 500)])
    image_reduced = np.zeros(
        [int((image_amp.shape[0] + 500) / 100), int((image_amp.shape[1] + 500) / 100)]
    )
    pixel_scale_reduced = pixel_scale * 100

    # Coordinates of the center of the Earth in the POV of the satellite
    lon = 0
    lat = np.pi / 2
    vec = hp.ang2vec(lat, lon)

    # Create a healpix sphere:
    NSIDE = 64

    # Create a circle from the size of the earth watched at the satellite:
    ipix_disc = hp.query_disc(
        NSIDE,
        vec=vec,
        radius=np.radians(np.arcsin(R_earth / (R_earth + sat_distance)) * 180 / np.pi),
    )

    # RA and DEC of the pixels
    lon_list, lat_list = hp.pix2ang(nside=NSIDE, ipix=ipix_disc)
    ra_list, dec_list = indextoradec(NSIDE, ipix_disc)

    coords_list = SkyCoord(ra_list, dec_list, frame="icrs", unit="deg")

    # Coords of the pointing of the telescope in the healpix sphere:
    satellite_coords = SkyCoord(
        90 + sat_ra_dev, 0 + sat_dec_dev, frame="icrs", unit="deg"
    )

    list_detector_reduced = tools.detector_coordinates(
        satellite_coords, image_reduced, pixel_scale_reduced
    )

    separation_list = np.zeros(
        [len(coords_list), image_reduced.shape[0], image_reduced.shape[1]]
    )

    for i in tqdm(range(len(coords_list))):
        separation_list[i] = coords_list[i].separation(list_detector_reduced).deg

    separation_day = np.zeros(
        [len(coords_list), image_reduced.shape[0], image_reduced.shape[1]]
    )
    separation_night = np.zeros(
        [len(coords_list), image_reduced.shape[0], image_reduced.shape[1]]
    )

    for i in range(len(coords_list)):
        if coords_list.ra.deg[i] <= 180:
            separation_night[i] = separation_list[i]

        else:
            separation_day[i] = separation_list[i]

    separation_night = np.delete(
        separation_night, np.where(~separation_night.any(axis=1))[0], axis=0
    )
    separation_day = np.delete(
        separation_day, np.where(~separation_day.any(axis=1))[0], axis=0
    )

    solid_angle_pixel = hp.nside2pixarea(NSIDE, degrees=False)

    wv_beg = wave_begin * 10  # from nm to AA
    wave_end = wave_end * 10  # from nm to AA

    flux_earth_night, flux_earth_night_err = quad(
        lambda x: earth_spectrum_night(obs_date, x), wv_beg, wave_end
    )  # ph / s / cm^2

    flux_earth_day, flux_earth_day_err = quad(
        lambda x: earth_spectrum_day(x), wv_beg, wave_end
    )  # ph / s / cm^2

    print("Intensity received at the surface of Earth from Moon: ph / s / cm2 ")
    print(flux_earth_night)

    I_moon_sat = flux_earth_night * solid_angle_pixel / (4 * np.pi)  # ph / s / cm2

    print(
        "Intensity received at the satellite from Earth illuminated by Moon: ph / s / cm2 "
    )
    print(I_moon_sat)

    ##################
    I_day_sat = flux_earth_day * solid_angle_pixel / (4 * np.pi)  # ph / s / cm2

    print(
        "Intensity received at the satellite from Earth illuminated by Sun: ph / s / cm2 "
    )
    print(I_day_sat)

    separation_list_center = satellite_coords.separation(coords_list).deg

    separation_day_center_lst = []
    separation_night_center_lst = []

    for i in range(len(coords_list)):
        if coords_list.ra.deg[i] <= 180:
            separation_night_center_lst.append(separation_list_center[i])

        else:
            separation_day_center_lst.append(separation_list_center[i])

    separation_day_center = np.array(separation_day_center_lst)
    separation_night_center = np.array(separation_night_center_lst)

    list_index_day = []
    for i in tqdm(range(len(separation_day_center))):
        if separation_day_center[i] > 90.0:
            list_index_day.append(i)

    separation_day = np.delete(separation_day, list_index_day, 0)

    list_index_night = []
    for i in tqdm(range(len(separation_night_center))):
        if separation_night_center[i] > 90.0:
            list_index_night.append(i)

    separation_night = np.delete(separation_night, list_index_night, 0)

    flux_detector_day = np.zeros(
        [len(separation_day), image_reduced.shape[0], image_reduced.shape[1]]
    )
    for i in tqdm(range(len(separation_day))):
        flux_detector_day[i] = NDI_function(separation_day[i]) * I_day_sat

    flux_detector_night = np.zeros(
        [len(separation_night), image_reduced.shape[0], image_reduced.shape[1]]
    )
    for i in tqdm(range(len(separation_night))):
        flux_detector_night[i] = NDI_function(separation_night[i]) * I_moon_sat

    total_night = np.sum(flux_detector_night, axis=0)
    total_day = np.sum(flux_detector_day, axis=0)

    total = total_day + total_night

    grid = tools.detector_interpolation(
        coords=satellite_coords,
        image_reduced=image_reduced,
        pixel_scale_reduced=pixel_scale_reduced,
        image=image_amp,
        pixel_scale=pixel_scale,
        fluxes=total,
    )

    result = grid * (pix_size / 1e4) ** 2  # ph / s

    result_cropped = fit_into_array(
        array=result, output_shape=image.shape, align="center"
    )

    return result_cropped


##################################################
##### Coordinates of the moon as a extense object:
##################################################


def moon_coords(
    obs_date: Time, sat_distance: float, pixel_scale: float, image: np.ndarray
):
    """Calculate the coordinates of the Moon as an extenct object.

    Parameters
    ----------
    obs_date: Time object: scale='utc' format='iso'.
            Time of the observation.
    sat_distance: float (in km).
            Altitude of the satellite (orbit).
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    image: 2-d array.
            Image of the detector (just for the size)
    """

    coords_moon = [get_moon(obs_date)]
    distance_moon_earth = get_moon(obs_date).distance
    distance_moon_dunes = distance_moon_earth.to(u.km).value - sat_distance
    moon_angle_radius = (
        (moon_rad.value / distance_moon_dunes) * (180 / np.pi) * u.degree
    )

    sep_ang = angular_separation_list(coords_moon[0], coords_moon, pixel_scale, image)
    moon_surface = np.zeros([sep_ang.shape[1], sep_ang.shape[2]])

    for i in range(sep_ang.shape[1]):
        for j in range(sep_ang.shape[2]):
            if sep_ang[0][i][j] < moon_angle_radius.value:
                moon_surface[i][j] = 1

    n_grid_y = image.shape[0]
    n_grid_x = image.shape[1]

    data = np.zeros([n_grid_y, n_grid_x])

    xcenter = int(n_grid_x / 2)
    ycenter = int(n_grid_y / 2)

    x, y = tools.index_coords(data, origin=(xcenter, ycenter))

    cdelt = np.array([-1.0, 1.0]) / 3600 * pixel_scale

    w = wcs.WCS(naxis=2)

    pa = 0
    crpix = [0.0, 0.0]
    w.wcs.crpix = crpix
    w.wcs.crval = [coords_moon[0].ra.deg, coords_moon[0].dec.deg]
    w.wcs.cdelt = cdelt
    w.wcs.crota = [0, -pa]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    rac_det, dec_det = w.all_pix2world(x, y, 1)

    list_moon = SkyCoord(ra=rac_det, dec=dec_det, unit="deg", frame="icrs")

    map_moon_dec = list_moon.dec.deg * moon_surface
    map_moon_dec[map_moon_dec == 0] = np.nan

    map_moon_ra = list_moon.ra.deg * moon_surface
    map_moon_ra[map_moon_ra == 0] = np.nan

    list_moon_ra = map_moon_ra[~np.isnan(map_moon_ra)]
    list_moon_dec = map_moon_dec[~np.isnan(map_moon_dec)]

    moon_coords_list = SkyCoord(list_moon_ra, list_moon_dec, frame="icrs", unit="deg")
    return moon_coords_list


#############################
##### Straylight of the Moon:
#############################


def moon_straylight(
    NDI_function: Callable,
    sat_distance: float,
    image: np.ndarray,
    pixel_scale: float,
    coords_detector: SkyCoord,
    pix_size: float,
    wave_begin: float,
    wave_end: float,
    obs_date: Time,
):
    """Calculate the straylight between each coordinate of the moon and each pixel at the detector for a exposure time.

    Parameters
    ----------
    NDI_function: function.
            NDI function that is used.
    sat_distance: float (in km).
            Altitude of the satellite (orbit).
    image: 2-d array.
            Image of the detector (just for the size)
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope.
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    pix_size: float (in microns).
            Physical ize of the pixel of the detector.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    obs_date: Time object: scale='utc' format='iso'.
            Time of the observation.

    """
    image_amp = np.zeros([int(image.shape[0] + 500), int(image.shape[1] + 500)])
    image_reduced = np.zeros(
        [int((image_amp.shape[0] + 500) / 100), int((image_amp.shape[1] + 500) / 100)]
    )
    pixel_scale_reduced = pixel_scale * 100

    surface_pixel_rad = ((pixel_scale_reduced * u.arcsec) ** 2).to(u.rad**2).value

    list_moon_coords = moon_coords(
        obs_date, sat_distance, pixel_scale_reduced, image_reduced
    )

    sep_ang_moon_center = coords_detector.separation(list_moon_coords).deg
    print("Moon is at", sep_ang_moon_center[0], "degrees")

    flux, flux_err = moon_flux(obs_date, wave_begin, wave_end)

    photons_moon_per_exp = np.zeros(
        [len(sep_ang_moon_center), image_reduced.shape[0], image_reduced.shape[1]]
    )
    for i in tqdm(range(len(sep_ang_moon_center))):
        photons_moon_per_exp[i] = (
            NDI_function(x=sep_ang_moon_center[i])
            * flux
            * surface_pixel_rad
            / (4 * np.pi)
        )

    total_flux_moon = np.sum(photons_moon_per_exp, axis=0)

    grid = tools.detector_interpolation(
        coords=coords_detector,
        image_reduced=image_reduced,
        pixel_scale_reduced=pixel_scale_reduced,
        image=image,
        pixel_scale=pixel_scale,
        fluxes=total_flux_moon,
    )

    return grid * (pix_size / 1e4) ** 2


##########################################
##### Straylight of the Stars from EUCLID:
##########################################


def stars_straylight_external(
    NDI_function: Callable, coords_detector: SkyCoord, pix_size: float
):
    """Calculate the straylight of the stars with an angular distance higher than 3 degrees. Uses an external file.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    pix_size: float (in microns).
            Physical ize of the pixel of the detector.

    Note:
        The function returns a map in photons/s units.
    """

    data = pd.read_csv("Files/straylight/low_res_euclid_gaia_map_v2.csv", index_col=0)

    coords_stars = SkyCoord(data["ra_bary"], data["dec_bary"], frame="icrs", unit="deg")
    flux_photons_stars = data["flux_photons"].to_numpy()
    ang_sep = coords_detector.separation(coords_stars).deg

    list_index = []
    for i in tqdm(range(len(coords_stars))):
        if ang_sep[i] < 3.0:
            list_index.append(i)

    ang_sep = np.delete(ang_sep, list_index, 0)
    flux_photons_stars = np.delete(flux_photons_stars, list_index, 0)
    ndi_values_stars = NDI_function(ang_sep)

    total_irradiance = flux_photons_stars * ndi_values_stars
    flux_straylight_external = np.nansum(total_irradiance)

    return flux_straylight_external * (pix_size / 1e4) ** 2


def stars_straylight_nearby_center(
    NDI_function: Callable,
    coords_detector: SkyCoord,
    pix_size: float,
    band_var: str,
    wave_begin: float,
    wave_end: float,
):
    """Calculate the straylight of the planets of the solar system for every exposure.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    band_var: str.
            Name of the filter used in the simulation.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    pix_size: float (in microns).
            Physical ize of the pixel of the detector.

    Note:
        The function returns a map in photons/s units.
    """

    h_planck = 6.626075540e-34  # Planck constant in W s**2
    c_speed = 2.99792458e8  # speed of light in vaccuum in m/s

    wv_in = (wave_begin * u.nm).to(u.m).value
    wv_out = (wave_end * u.nm).to(u.m).value
    wv_lenght = (wv_in + wv_out) / 2  # m
    energy = h_planck * c_speed / wv_lenght

    #################
    ##### HST F475X
    #################

    if band_var == "HST_F475X":
        print("Getting data from GAIA")
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=3 * u.deg,
            columns=[
                "source_id",
                "ra",
                "dec",
                "phot_g_mean_mag",
                "phot_bp_mean_mag",
                "phot_rp_mean_mag",
            ],
        )

        file = result_gaia.to_pandas()

        file = file.dropna(subset=["phot_rp_mean_mag"], inplace=True)
        m_g = file["phot_g_mean_mag"].to_numpy()
        color_bp_rp = np.array(file["phot_bp_mean_mag"] - file["phot_rp_mean_mag"])

        m_V = m_g - (
            -0.02704
            + 0.01424 * color_bp_rp
            - 0.2156 * color_bp_rp**2
            + 0.01426 * color_bp_rp**3
        )
        m_I = m_g - (0.01753 + 0.76 * color_bp_rp - 0.0991 * color_bp_rp**2)
        m_g_sdss = m_g - (
            0.2199
            - 0.6365 * color_bp_rp
            - 0.1548 * color_bp_rp**2
            + 0.0064 * color_bp_rp**3
        )
        m_B = ((m_g_sdss - m_V) + 0.124) / 0.630 + m_V

        m_f475x = m_B - 0.201 * (m_B - m_I)

        flux_units_SI = (
            np.array(10 ** (-(m_f475x + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz

        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2

        file["flux_photons"] = (irradiance_stars / energy / 1e4).value  # ph/s/cm^2

    #################
    ##### VIS EUCLID
    #################

    elif band_var == "Euclid_VIS":
        print("Getting data from GAIA")
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=3 * u.deg,
            columns=[
                "source_id",
                "ra",
                "dec",
                "phot_g_mean_mag",
                "phot_bp_mean_mag",
                "phot_rp_mean_mag",
            ],
        )

        file = result_gaia.to_pandas()

        file.dropna(subset=["phot_rp_mean_mag"], inplace=True)
        m_g = file["phot_g_mean_mag"].to_numpy()
        color_bp_rp = np.array(file["phot_bp_mean_mag"] - file["phot_rp_mean_mag"])

        m_VIS = np.array(0.993 * m_g - 0.183)

        flux_units_SI = (
            np.array(10 ** (-(m_VIS + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz

        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2

        file["flux_photons"] = (irradiance_stars / energy / 1e4).value  # ph/s/cm^2

    ###############
    ##### Y EUCLID
    ###############

    elif band_var == "Euclid_Y":
        vv = Vizier(row_limit=-1)
        result = vv.query_region(
            coords_detector,
            radius=3 * u.deg,
            inner_radius=0.7 * u.deg,
            catalog="II/246",
        )
        result_2mass = result[0].to_pandas()

        m_Ye = (
            result_2mass["Hmag"]
            - 0.005
            + 1.134 * (result_2mass["Jmag"] - result_2mass["Hmag"])
        )
        flux_units_SI = (
            np.array(10 ** (-(m_Ye + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz
        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2
        result_2mass["flux_photons"] = (
            irradiance_stars / energy / 1e4
        ).value  # ph/s/cm^2
        file = result_2mass.rename(columns={"RAJ2000": "ra", "DEJ2000": "dec"})[
            ["ra", "dec", "flux_photons"]
        ]

    ###############
    ##### J EUCLID
    ###############

    elif band_var == "Euclid_J":
        vv = Vizier(row_limit=-1)
        result = vv.query_region(
            coords_detector,
            radius=3 * u.deg,
            inner_radius=0.7 * u.deg,
            catalog="II/246",
        )
        result_2mass = result[0].to_pandas()

        m_Je = (
            result_2mass["Hmag"]
            - 0.007
            + 0.786 * (result_2mass["Jmag"] - result_2mass["Hmag"])
        )
        flux_units_SI = (
            np.array(10 ** (-(m_Je + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz
        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2
        result_2mass["flux_photons"] = (
            irradiance_stars / energy / 1e4
        ).value  # ph/s/cm^2
        file = result_2mass.rename(columns={"RAJ2000": "ra", "DEJ2000": "dec"})[
            ["ra", "dec", "flux_photons"]
        ]

    print("..........................Applying NDI...........................")
    ra_stars, dec_stars = file["ra"].values, file["dec"].values
    flux_photons_stars = file["flux_photons"].values

    star_position = SkyCoord(ra_stars, dec_stars, unit="deg")
    ang_sep = coords_detector.separation(star_position).deg
    list_index = []
    for i in range(len(star_position)):
        if ang_sep[i] < 0.7:
            list_index.append(i)

    ang_sep = np.delete(ang_sep, list_index, 0)
    flux_photons_stars = np.delete(flux_photons_stars, list_index, 0)
    ndi_values_stars = NDI_function(ang_sep)

    total_irradiance = flux_photons_stars * ndi_values_stars
    flux_straylight_nearby = np.nansum(total_irradiance)

    return flux_straylight_nearby * (pix_size / 1e4) ** 2


#######################################################
##### TOTAL Straylight of the Stars from EUCLID + GAIA:
#######################################################


def stellar_straylight(
    NDI_function: Callable,
    coords_detector: SkyCoord,
    pix_size: float,
    band_var: str,
    wave_begin: float,
    wave_end: float,
) -> np.ndarray:
    """Calculate the straylight of the planets of the solar system for every exposure.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    pix_size: float (in microns).
            Physical ize of the pixel of the detector.
    band_var: str.
            Name of the filter used in the simulation.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.

    Note:
        The function returns a map in photons/s units.
    """
    ext_stray = stars_straylight_external(
        NDI_function=NDI_function, coords_detector=coords_detector, pix_size=pix_size
    )
    nearby_stray = stars_straylight_nearby_center(
        NDI_function=NDI_function,
        coords_detector=coords_detector,
        pix_size=pix_size,
        band_var=band_var,
        wave_begin=wave_begin,
        wave_end=wave_end,
    )
    total_stellar_straylight = ext_stray + nearby_stray
    return total_stellar_straylight


def straylight(
    detector: Detector,
    coords_detector: SkyCoord,
    sat_distance: float,
    pixel_scale: float,
    band_var: str,
    wave_begin: float,
    wave_end: float,
    obs_date: dict,
) -> None:
    """Calculate the stars inside the FOV.

    Parameters
    ----------
    detector
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    sat_distance: float (km).
            Satellite distance to the Earth surface.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope used.
    band_var: str.
            Name of the filter used in the simulation.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    obs_date: dict.
            Date of the observation.
    Note:
        The function returns an image in photons/s/cm2 units
    """
    earth_straylight_photon: np.ndarray = earth_straylight(
        NDI_function=NDI_iSIM170,
        sat_distance=sat_distance,
        image=detector.photon.array,
        pixel_scale=pixel_scale,
        pix_size=detector.geometry.pixel_horz_size,
        wave_begin=wave_begin,
        wave_end=wave_end,
        obs_date=Time(**obs_date),
        sat_ra_dev=0.0,
        sat_dec_dev=0.0,
    )

    moon_straylight_photon: np.ndarray = moon_straylight(
        NDI_function=NDI_iSIM170,
        sat_distance=sat_distance,
        image=detector.photon.array,
        pixel_scale=pixel_scale,
        coords_detector=SkyCoord(**coords_detector),
        pix_size=detector.geometry.pixel_horz_size,
        wave_begin=wave_begin,
        wave_end=wave_end,
        obs_date=Time(**obs_date),
    )

    stellar_straylight_photon: np.ndarray = stellar_straylight(
        NDI_function=NDI_iSIM170,
        coords_detector=SkyCoord(**coords_detector),
        pix_size=detector.geometry.pixel_horz_size,
        band_var=band_var,
        wave_begin=wave_begin,
        wave_end=wave_end,
    )

    total_straylight = (
        earth_straylight_photon + moon_straylight_photon + stellar_straylight_photon
    )
    detector.photon.array += total_straylight * detector.absolute_time
