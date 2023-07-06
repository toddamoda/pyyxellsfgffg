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
"""Calculation of the position of stars and fluxes."""


# Suppress warnings. Comment this out if you wish to see the warning messages
import warnings

import astropy.units as u
import numpy as np
import pandas as pd
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from tqdm import tqdm

import pyxel.models.photon_collection.arrakihs_tools as tools
from pyxel.detectors import Detector

warnings.filterwarnings("ignore")
from astropy import wcs
from astropy.coordinates import SkyCoord  # High-level coordinates


def stars_frgnd_catalog(
    coords_detector: SkyCoord,
    image: np.ndarray,
    pixel_scale: float,
    band_var: str,
    wave_begin: float,
    wave_end: float,
) -> np.ndarray:
    """Calculate the stars inside the FOV.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    image: 2-d array.
            Image example to take the characteristics from.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope used.
    band_var: str.
            Name of the filter used in the simulation.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    Note:
        The function returns an image in photons/s/cm2 units
    """
    h_planck = 6.626075540e-34  # Planck constant in W s**2
    c_speed = 2.99792458e8  # speed of light in vaccuum in m/s

    wv_in = (wave_begin * u.nm).to(u.m).value
    wv_out = (wave_end * u.nm).to(u.m).value
    wv_lenght = (wv_in + wv_out) / 2  # m
    energy = h_planck * c_speed / (wv_lenght)

    #################
    ##### HST F475X
    #################

    if band_var == "HST_F475X":
        print("Getting data from GAIA")
        # we get the data from GAIA DR3 at the coordinates of tht pointing inside a FOV of radius = 0.7º
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=0.7 * u.deg,
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
        m_g_vega = file["phot_g_mean_mag"].to_numpy()
        zp_gaia_vega = 25.6884  # Source: GAIA collab
        zp_gaia_ab = 25.7934  # Source: GAIA collab
        # we transform VEGA mags to AB mags
        m_g_ab = m_g_vega + (zp_gaia_ab - zp_gaia_vega)
        # color GAIA_BP-GAIA_RP
        color_bp_rp = np.array(file["phot_bp_mean_mag"] - file["phot_rp_mean_mag"])

        # Transform GAIA to Johnson-V
        m_V = m_g_ab - (
            -0.02704
            + 0.01424 * color_bp_rp
            - 0.2156 * color_bp_rp**2
            + 0.01426 * color_bp_rp**3
        )
        # Transform GAIA to Johnson-Cousins-I
        m_I = m_g_ab - (0.01753 + 0.76 * color_bp_rp - 0.0991 * color_bp_rp**2)
        # Transform GAIA to SDSS-g
        m_g_sdss = m_g_ab - (
            0.2199
            - 0.6365 * color_bp_rp
            - 0.1548 * color_bp_rp**2
            + 0.0064 * color_bp_rp**3
        )
        # Transform SDSS-g,  Johnson-V to  Johnson-B
        m_B = ((m_g_sdss - m_V) + 0.124) / 0.630 + m_V
        # Transform Johnson-B, Johnson-Cousins-I to F475X
        m_f475x = m_B - 0.201 * (m_B - m_I)

        # Magnitudes to Flux (ph/s/cm2)
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
        # we get the data from GAIA DR3 at the coordinates of tht pointing inside a FOV of radius = 0.7º
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=0.7 * u.deg,
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
        m_g_vega = file["phot_g_mean_mag"].to_numpy()
        zp_gaia_vega = 25.6884  # Source: GAIA collab
        zp_gaia_ab = 25.7934  # Source: GAIA collab
        # we transform VEGA mags to AB mags
        m_g_ab = m_g_vega + (zp_gaia_ab - zp_gaia_vega)
        # Transform GAIA to Euclid-VIS (Borlaff et al, 21)
        m_VIS = np.array(0.993 * m_g_ab - 0.183)

        # Magnitudes to Flux (ph/s/cm2)
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
        print("Getting data from Vizier")
        # we get the data from 2MASS at the coordinates of tht pointing inside a FOV of radius = 0.7º
        vv = Vizier(row_limit=-1)
        result = vv.query_region(coords_detector, radius=0.7 * u.deg, catalog="II/246")
        result_2mass = result[0].to_pandas()
        # Transform 2mass to Euclid-Y
        m_Ye = (
            result_2mass["Hmag"]
            - 0.005
            + 1.134 * (result_2mass["Jmag"] - result_2mass["Hmag"])
        )
        # Magnitudes to Flux (ph/s/cm2)
        flux_units_SI = (
            np.array(10 ** (-(m_Ye + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz
        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2
        result_2mass["flux_photons"] = (
            irradiance_stars / energy / 1e4
        ).value  # ph/s/cm^2
        result_2mass_new = result_2mass.rename(
            columns={"RAJ2000": "ra", "DEJ2000": "dec"}
        )[["ra", "dec", "flux_photons"]]

        # we complement the data with GAIA DR3 at the coordinates of tht pointing inside a FOV of radius = 0.7º
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=0.7 * u.deg,
            columns=[
                "source_id",
                "ra",
                "dec",
                "phot_g_mean_mag",
                "phot_bp_mean_mag",
                "phot_rp_mean_mag",
            ],
        )
        result_gaia = result_gaia.to_pandas()
        # We drop the stars already in 2mass
        gaia_2mass_indexes = []
        for i in tqdm(range(len(result_2mass))):
            gaia_2mass_indexes.append(
                result_gaia[
                    (result_gaia["ra"] > result_2mass["RAJ2000"][i] - 2 / 3600)
                    & (result_gaia["ra"] < result_2mass["RAJ2000"][i] + 2 / 3600)
                    & (result_gaia["dec"] > result_2mass["DEJ2000"][i] - 2 / 3600)
                    & (result_gaia["dec"] < result_2mass["DEJ2000"][i] + 2 / 3600)
                ].index.values
            )

        new_result_gaia = result_gaia.drop(index=np.concatenate(gaia_2mass_indexes))

        m_g_vega = new_result_gaia["phot_g_mean_mag"].to_numpy()
        color_bp_rp = np.array(
            new_result_gaia["phot_bp_mean_mag"] - new_result_gaia["phot_rp_mean_mag"]
        )

        zp_gaia_vega = 25.6884
        zp_gaia_ab = 25.7934
        # we transform VEGA mags to AB mags
        m_g_ab = m_g_vega + (zp_gaia_ab - zp_gaia_vega)
        # Transform GAIA to 2mass-H
        color_g_H = -0.1621 + 1.968 * color_bp_rp - 0.1328 * color_bp_rp**2
        # Transform GAIA to 2mass-J
        color_g_J = -0.01883 + 1.394 * color_bp_rp - 0.07893 * color_bp_rp**2
        m_J = m_g_ab - color_g_J
        m_H = m_g_ab - color_g_H
        # Transform 2mass to Euclid-Y
        m_Ye = m_H - 0.005 + 1.134 * (m_J - m_H)

        # Magnitudes to Flux (ph/s/cm2)
        flux_units_SI = (
            np.array(10 ** (-(m_Ye + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz

        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2

        new_result_gaia["flux_photons"] = (
            irradiance_stars / energy / 1e4
        ).value  # ph/s/cm^2

        new_result_gaia = new_result_gaia[["ra", "dec", "flux_photons"]]

        file = pd.concat([result_2mass_new, new_result_gaia], ignore_index=True)

    ###############
    ##### J EUCLID
    ###############

    elif band_var == "Euclid_J":
        print("Getting data from Vizier")
        # we get the data from 2MASS at the coordinates of tht pointing inside a FOV of radius = 0.7º
        vv = Vizier(row_limit=-1)
        result = vv.query_region(coords_detector, radius=0.7 * u.deg, catalog="II/246")

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
        result_2mass_new = result_2mass.rename(
            columns={"RAJ2000": "ra", "DEJ2000": "dec"}
        )[["ra", "dec", "flux_photons"]]

        # we complement the data with GAIA DR3 at the coordinates of tht pointing inside a FOV of radius = 0.7º
        Gaia.ROW_LIMIT = -1
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        result_gaia = Gaia.query_object_async(
            coords_detector,
            radius=0.7 * u.deg,
            columns=[
                "source_id",
                "ra",
                "dec",
                "phot_g_mean_mag",
                "phot_bp_mean_mag",
                "phot_rp_mean_mag",
            ],
        )
        result_gaia = result_gaia.to_pandas()
        # We drop the stars already in 2mass
        gaia_2mass_indexes = []
        for i in tqdm(range(len(result_2mass))):
            gaia_2mass_indexes.append(
                result_gaia[
                    (result_gaia["ra"] > result_2mass["RAJ2000"][i] - 2 / 3600)
                    & (result_gaia["ra"] < result_2mass["RAJ2000"][i] + 2 / 3600)
                    & (result_gaia["dec"] > result_2mass["DEJ2000"][i] - 2 / 3600)
                    & (result_gaia["dec"] < result_2mass["DEJ2000"][i] + 2 / 3600)
                ].index.values
            )

        new_result_gaia = result_gaia.drop(index=np.concatenate(gaia_2mass_indexes))

        m_g_vega = new_result_gaia["phot_g_mean_mag"].to_numpy()
        color_bp_rp = np.array(
            new_result_gaia["phot_bp_mean_mag"] - new_result_gaia["phot_rp_mean_mag"]
        )

        zp_gaia_vega = 25.6884
        zp_gaia_ab = 25.7934
        # we transform VEGA mags to AB mags
        m_g_ab = m_g_vega + (zp_gaia_ab - zp_gaia_vega)
        # Transform GAIA to 2mass-H
        color_g_H = -0.1621 + 1.968 * color_bp_rp - 0.1328 * color_bp_rp**2
        # Transform GAIA to 2mass-J
        color_g_J = -0.01883 + 1.394 * color_bp_rp - 0.07893 * color_bp_rp**2
        m_J = m_g_ab - color_g_J
        m_H = m_g_ab - color_g_H
        # Transform 2mass to Euclid-J
        m_Je = m_H - 0.007 + 0.786 * (m_J - m_H)

        # Magnitudes to Flux (ph/s/cm2)
        flux_units_SI = (
            np.array(10 ** (-(m_Je + 56.1) / 2.5)) * u.W / u.m**2 / u.Hz
        )  # W/m^2/Hz

        irradiance_stars = (
            flux_units_SI * c_speed * (wv_out - wv_in) / (wv_out * wv_in)
        )  # W/m^2

        new_result_gaia["flux_photons"] = (
            irradiance_stars / energy / 1e4
        ).value  # ph/s/cm^2

        new_result_gaia = new_result_gaia[["ra", "dec", "flux_photons"]]

        file = pd.concat([result_2mass_new, new_result_gaia], ignore_index=True)

    # we project the stars in the FOV:
    stars_coords = SkyCoord(file["ra"], file["dec"], frame="icrs", unit="degree")

    cdelt = np.array([-1.0, 1.0]) / 3600 * pixel_scale
    crpix = np.array([image.shape[0] / 2, image.shape[1] / 2])
    pa = 0
    w = wcs.WCS(naxis=2)
    w.wcs.crpix = crpix
    w.wcs.crval = [coords_detector.ra.deg, coords_detector.dec.deg]
    w.wcs.cdelt = cdelt
    w.wcs.crota = [0, -pa]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    file["coords_in_det_ra"] = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[0]
    )
    file["coords_in_det_dec"] = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[1]
    )

    df_new = (
        file[
            (file["coords_in_det_ra"] > 0)
            & (file["coords_in_det_ra"] < image.shape[1])
            & (file["coords_in_det_dec"] > 0)
            & (file["coords_in_det_dec"] < image.shape[0])
        ]
    ).reset_index(drop=True)

    print("..........................Creating galaxy image...........................")

    model = np.zeros([image.shape[0], image.shape[1]])
    for name, group in tqdm(df_new.groupby("coords_in_det_ra")):
        for name_1, group_1 in group.groupby("coords_in_det_dec"):
            model[int(name_1), int(name)] = group_1["flux_photons"].sum()

    return model


def stars_foreground(
    detector: Detector,
    coords_detector: SkyCoord,
    pixel_scale: float,
    aperture: float,
    band_var: str,
    wave_begin: float,
    wave_end: float,
) -> None:
    """Calculate the stars inside the FOV.

    Parameters
    ----------
    coords_detector: SkyCoord (ICRS): (ra, dec) in deg.
            Coordinates of the pointing of the telescope.
    pixel_scale: float (in arcsec/pixel).
            Plate scale of the telescope used.
    band_var: str.
            Name of the filter used in the simulation.
    wave_begin: float, int (in nm).
            Wavelength at the beginning of the filter.
    wave_end: float, int (in nm).
            Wavelength at the end of the filter.
    Note:
        The function returns an image in photons/s/cm2 units
    """
    stars_flux: np.ndarray = stars_frgnd_catalog(
        coords_detector=SkyCoord(**coords_detector),
        image=detector.photon.array,
        pixel_scale=pixel_scale,
        band_var=band_var,
        wave_begin=wave_begin,
        wave_end=wave_end,
    )

    converted_photon = tools.flux2phot(
        flux=stars_flux, t_exp=detector.absolute_time, aperture=aperture
    )
    detector.photon.array += converted_photon
