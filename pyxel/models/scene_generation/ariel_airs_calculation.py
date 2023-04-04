"""Pyxel photon generator models."""
import os
from typing import Literal, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import scipy.constants as cst
from astropy import units as u
from astropy.io import ascii, fits
from scipy.integrate import cumtrapz


# ---------------------------------------------------------------------------------------------
def read_star_flux_from_file(filename):
    """
    Read star flux file.
    TODO: Read the unit from the text file

    :param:
        filename type string,
                name of the target file. Different extension can be considered
    :return:
        wavelength: type array 1D
                Wavelength associated with the flux of the star
        flux: type array 1D
                Flux of the target considered, in  ph/s/m2/µm
    """
    BOOL_verbose = True
    extension = os.path.splitext(filename)[1]
    if extension == ".txt":
        wavelength, flux = np.loadtxt(filename).T
        wavelength = wavelength * u.micron  # set appropriate unit here um
        flux = flux * u.photon / u.s / u.m / u.m / u.micron  # set appropriate units

    elif extension == ".ecsv":
        data = ascii.read(filename)
        flux = data["flux"].data * data["flux"].unit
        wavelength = data["wavelength"].data * data["wavelength"].unit

    elif extension == ".dat":
        """ExoNoodle file"""
        df_topex = pd.read_csv(filename, header=11)
        wavelength, flux = np.zeros(len(df_topex["wavelength flux "])), np.zeros(
            len(df_topex["wavelength flux "])
        )
        for i in range(len(df_topex["wavelength flux "])):
            wavelength[i] = float(df_topex["wavelength flux "][i].split("        ")[0])
            conv = 1.51 * 1e3 * 1e4 / wavelength[i]
            flux[i] = (
                float(df_topex["wavelength flux "][i].split("        ")[1])
                * conv
                * 1e-6
            )  # Attention aux unités
        wavelength = wavelength * u.micron
        flux = flux * u.photon / u.s / u.m / u.m / u.micron
    else:
        message("ERROR while convering, extension not readable", BOOL_verbose)

    return wavelength, flux


# ---------------------------------------------------------------------------------------------
def convert_flux(wavelength, flux, telescope_diameter_m1, telescope_diameter_m2):
    """
    Convert the flux of the target in ph/s/µm

    Parameters
    ----------
    wavelength: 1D array
        Wavelength sampling of the considered target
    flux: 1D array
        Flux of the target considered in ph/s/m2/µm
    telescope_diameter_m1: float
        Diamater of the M1 mirror of the TA
    telescope_diameter_m2: float
        Diamater of the M2 mirror of the TA

    Returns
    --------
    conv_flux: 1D array
        Flux of the target considered in ph/s/µm

    """
    BOOL_verbose = False
    if BOOL_verbose:
        print("Incident photon flux is being converted into ph/s/um")
    # use of astropy code
    flux.to(
        u.photon / u.m**2 / u.micron / u.s,
        equivalencies=u.spectral_density(wavelength),
    )

    diameter = (
        telescope_diameter_m2 * u.meter
    )  # TODO: define a class to describe the optic of the telescope ?
    Diameter = telescope_diameter_m1 * u.meter
    collecting_area = np.pi * diameter * Diameter / 4
    conv_flux = np.copy(flux) * collecting_area
    return conv_flux


# ---------------------------------------------------------------------------------------------
def compute_bandwidth(psf_wavelength):
    """
    Computes the bandwidth for non even distributed values
    First we put the poles, each pole is at the center of the previous wave and the next wave.
    We add the first pole and the last pole using symmetry. We get nw+1 poles

    :param psf:   PSF object
    :return:        bandwidth (usually in microns) and the pole wavelengths
    :rtype:         type quantity array,dimension nw
    """
    poles = (psf_wavelength[1:] + psf_wavelength[:-1]) / 2
    first_pole = psf_wavelength[0] - (psf_wavelength[1] - psf_wavelength[0]) / 2
    last_pole = psf_wavelength[-1] + (psf_wavelength[-1] - psf_wavelength[-2]) / 2
    all_poles = np.concatenate(([first_pole], poles, [last_pole]))
    bandwidth = all_poles[1:] - all_poles[:-1]

    return bandwidth, all_poles


# ---------------------------------------------------------------------------------------------
def integrate_flux(wavelength, flux, psf_wavelength):
    """
    Integrate flux on each bin around the psf.
    The trick is to integrate first, and interpolate after (and not vice-versa).

    :param flux:        type quantity array, unit ph/s/m2/micron dimension big_n
    :param  wavelength:   type quantity array, unit usually micron, dimension small_n

    :return: flux integrated in photon/s
    :rtype: type quantity array, dimension nw
    """
    BOOL_verbose = True
    if BOOL_verbose:
        print("Integrate flux on each bin around the psf...")

    bandwidth, all_poles = compute_bandwidth(
        psf_wavelength
    )  # Mettre les paramètres de la fonction
    cum_sum = cumtrapz(flux.value, wavelength.value, initial=0.0)  # Cumulative count
    # self.wavelength has to quantity: value and units
    cum_sum_interp = np.interp(
        all_poles, wavelength, cum_sum
    )  # interpolate over psf wavelength
    flux_int = (
        cum_sum_interp[1:] - cum_sum_interp[:-1]
    )  # Compute flux over psf spectral bin
    flux_int = flux_int * flux.unit * wavelength.unit
    flux = np.copy(flux_int)  # Update flux matrix

    return flux


# ------------------------------------------------------------------------------
def multiply_by_transmission(psf, transmission_dict):
    """The goal of this function is to take into account the flux of the incident star"""
    for t in transmission_dict.keys():
        if "M" in t:
            f = interpolate.interp1d(
                transmission_dict[t]["wavelength"],
                transmission_dict[t]["reflectivity_eol"],
            )
        else:
            f = interpolate.interp1d(
                transmission_dict[t]["wavelength"],
                transmission_dict[t]["transmission_eol"],
            )
        flux = np.copy(flux) * f(psf.psf_wavelength)


# ---------------------------------------------------------------------------------------------
def read_psf_from_fits_file(filename):
    """
    Read psf files depending on simulation and instrument parameters

    :param:     filename : type string, name of the .fits file
                verbose : type bool, if True information are displayed. Default False

    :return:    cube : (3D array) PSF for each wavelength saved as (360,360) array, one for each wavelengh
                waves (1D array) wavelength in um
                line_pos_psf, col_pos_psf : 1D array, position of the PSF at each wavelength
    """
    BOOL_verbose = True
    hdu = fits.open(filename)  # Open fits
    psf_datacube, table = hdu[0].data, hdu[1].data
    line_psf_pos = (table["x_centers"]).astype(
        int
    )  # Position of the PSF on AIRS window along line
    col_psf_pos = (table["y_centers"]).astype(
        int
    )  # Position of the PSF on AIRS window along col
    psf_wavelength = table["waves"] * u.micron  # Wavelength
    hdu.close()  # Close fits
    if BOOL_verbose:
        print(
            "PSF Datacube", psf_datacube.shape, psf_datacube.min(), psf_datacube.max()
        )
        print(
            "PSF Wavelength",
            psf_wavelength.shape,
            psf_wavelength.min(),
            psf_wavelength.max(),
        )

    return psf_datacube, psf_wavelength, line_psf_pos, col_psf_pos


# ---------------------------------------------------------------------------------------------
def project_psfs(
    psf_datacube, line_psf_pos, col_psf_pos, flux, row, col, expend_factor
):
    """
    Project each psf on a (n_line_final * self.zoom, n_col_final * self.zoom) pixel image
    n_line_final, n_col_final = corresponds to window size. It varies with the channel

    :param psfs:          type numpy array, dimension (nw, n_line, n_col)
    :param flux:          type quantity array, unit electron/s dimension big_n
    :param col_center:    type numpy array, column position of the center of PSF along AIRS window
    :param line_center:   type numpy array, line position of the center of the PSF along AIRS window

    :return:            type quantity array,dimension ny, nx, spectral image in e-/s. Shape = detector shape
    """
    nw, n_line, n_col = psf_datacube.shape  # Extract shape of the PSF
    half_size_col, half_size_line = n_col // 2, n_line // 2  # Half size of the PSF

    # photon_incident = np.zeros((detector.geometry.row * expend_factor, detector.geometry.col * expend_factor))
    # photoelectron_generated = np.zeros((detector.geometry.row * expend_factor, detector.geometry.col * expend_factor))
    photon_incident = np.zeros((row * expend_factor, col * expend_factor))
    photoelectron_generated = np.zeros((row * expend_factor, col * expend_factor))

    col_win_middle, line_win_middle = int(col_psf_pos.mean()), int(line_psf_pos.mean())

    for i in np.arange(nw):  # Loop over the wavelength
        # Resize along line dimension
        line1 = (
            line_psf_pos[i]
            - line_win_middle
            + row * expend_factor // 2
            - half_size_line
        )
        line2 = (
            line_psf_pos[i]
            - line_win_middle
            + row * expend_factor // 2
            + half_size_line
        )
        # Resize along col dimension
        col1 = (
            col_psf_pos[i] - col_win_middle + col * expend_factor // 2 - half_size_col
        )
        col2 = (
            col_psf_pos[i] - col_win_middle + col * expend_factor // 2 + half_size_col
        )
        # Derive the amount of photon incident on the detector
        photon_incident[line1:line2, col1:col2] = (
            photon_incident[line1:line2, col1:col2]
            + psf_datacube[i, :, :] * flux[i].value
        )

        # TODO: Here take into account the QE map of the detector, and its dependence with wavelength
        # QE of the detector has to be sampled with the same resolution as the PSF is sampled
        qe = 0.65
        photoelectron_generated[line1:line2, col1:col2] = (
            photon_incident[line1:line2, col1:col2].copy() * qe
        )  # qe_detector[i]

    photon_incident = (
        photon_incident * flux.unit
    )  # This is the amount of photons incident on the detector
    photoelectron_generated = (
        photoelectron_generated * u.electron
    )  # This is the amount of photons incident on the detector

    return rebin_2d(photon_incident, expend_factor), rebin_2d(
        photoelectron_generated, expend_factor
    )


# ---------------------------------------------------------------------------------------------
def rebin_2d(data, expend_factor):
    """
    rebin as idl
    Each pixel of the returned image is the sum of zy by zx pixels of the input image.

    Parameters :   data: numpy.array of 2 dimensions (image), ny, nx
                   expend_factor: tuple of 2 integers, zy, zx
                   beware ny must be a multiple of zy, and nx multiple of zx
    verbose: bool, displays the final shape

    Return :       result: numpy array shrinked, dimension ny/zy, nx/zx

    Example :      a = np.arange(48).reshape((6,8))
                   rebin2d( a, [2,2])

    HISTORY:       Rene Gastaud, 13 January 2016
    https://codedump.io/share/P3pB13TPwDI3/1/resize-with-averaging-or-rebin-a-numpy-2d-array
    2017-11-17 : RG and Alan O'Brien  compatibility with python 3 bug452
    """
    BOOL_verbose = True
    zoom = [expend_factor, expend_factor]  # In case assymetrical zoom is used
    final_shape = (
        int(data.shape[0] // zoom[0]),
        zoom[0],
        int(data.shape[1] // zoom[1]),
        zoom[1],
    )
    if BOOL_verbose:
        print("final_shape ", final_shape)
    result = data.reshape(final_shape).sum(3).sum(1)
    return result
