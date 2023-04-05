"""Pyxel photon generator models."""
import os
from typing import Tuple

import numpy as np
import pandas as pd

# import scipy.constants as cst
from astropy import units as u
from astropy.io import ascii, fits
from astropy.units import Quantity
from numpy import ndarray
from scipy.integrate import cumtrapz


# ---------------------------------------------------------------------------------------------
def read_star_flux_from_file(
    filename: str,
    verbose: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Read star flux file.
    # TODO: Read the unit from the text file.

    Parameters
    ----------
    filename: type string,
        Name of the target file. Different extension can be considered.
    verbose : bool
        If True information is displayed. Default False.

    Returns
    -------
    wavelength: type array 1D
        Wavelength associated with the flux of the star.
    flux: type array 1D
        Flux of the target considered, in  ph/s/m2/µm.
    """
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
        print("ERROR while converting, extension not readable", verbose)

    return wavelength, flux


# ---------------------------------------------------------------------------------------------
def convert_flux(
    wavelength: np.ndarray,
    flux: np.ndarray,
    telescope_diameter_m1: float,
    telescope_diameter_m2: float,
    verbose: bool = False,
) -> np.ndarray:
    """
    Convert the flux of the target in ph/s/µm.

    Parameters
    ----------
    wavelength: 1D array
        Wavelength sampling of the considered target.
    flux: 1D array
        Flux of the target considered in ph/s/m2/µm.
    telescope_diameter_m1: float
        Diameter of the M1 mirror of the TA.
    telescope_diameter_m2: float
        Diameter of the M2 mirror of the TA.
    verbose : bool
        If True information is displayed. Default False.

    Returns
    --------
    conv_flux: 1D array
        Flux of the target considered in ph/s/µm.
    """
    if verbose:
        print("Incident photon flux is being converted into ph/s/um.")
    # use of astropy code
    flux.to(
        u.photon / u.m**2 / u.micron / u.s,
        equivalencies=u.spectral_density(wavelength),
    )

    diameter_m2 = (
        telescope_diameter_m2 * u.meter
    )  # TODO: define a class to describe the optic of the telescope ?
    diameter_m1 = telescope_diameter_m1 * u.meter
    collecting_area = np.pi * diameter_m1 * diameter_m2 / 4
    conv_flux = np.copy(flux) * collecting_area
    return conv_flux


# ---------------------------------------------------------------------------------------------
def compute_bandwidth(
    psf_wavelength,
) -> tuple[Quantity, Quantity]:
    """
    Compute the bandwidth for non even distributed values.
    First we put the poles, each pole is at the center of the previous wave and the next wave.
    We add the first pole and the last pole using symmetry. We get nw+1 poles

    Parameters
    ----------
    psf_wavelength:
       PSF object.

    Returns
    -------
    bandwidth : quantity array
        Bandwidth. Usually in microns.
    all_poles : quantity array
        Pole wavelengths. Dimension: nw
    """
    poles = (psf_wavelength[1:] + psf_wavelength[:-1]) / 2
    first_pole = psf_wavelength[0] - (psf_wavelength[1] - psf_wavelength[0]) / 2
    last_pole = psf_wavelength[-1] + (psf_wavelength[-1] - psf_wavelength[-2]) / 2
    all_poles = np.concatenate(([first_pole], poles, [last_pole]))
    bandwidth = all_poles[1:] - all_poles[:-1]

    return bandwidth, all_poles


# ---------------------------------------------------------------------------------------------
def integrate_flux(
    wavelength: Quantity,
    flux: Quantity,
    psf_wavelength: Quantity,
    verbose: bool = False,
) -> Quantity:
    """
     Integrate flux on each bin around the psf.
     The trick is to integrate first, and interpolate after (and not vice-versa).

     Parameters
     ----------
     wavelength : quantity array
         Wavelength. Unit: usually micron. Dimension: small_n.
     flux : quantity array
         Flux. Unit: ph/s/m2/micron. Dimension: big_n.
     psf_wavelength : quantity array
         Point Spead Function per wavelength.
    verbose : bool
         If True information is displayed. Default False.

     Returns
     -------
     flux : quantity array
         Flux. UNit: photon/s. Dimension: nw.
    """
    if verbose:
        print("Integrate flux on each bin around the psf...")

    bandwidth, all_poles = compute_bandwidth(
        psf_wavelength
    )  # Set the parameters of the function

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
# def multiply_by_transmission(psf, transmission_dict: Mapping[str, Any]) -> None:
#     """The goal of this function is to take into account the flux of the incident star"""
#     for t in transmission_dict.keys():
#         if "M" in t:
#             f = interpolate.interp1d(
#                 transmission_dict[t]["wavelength"],
#                 transmission_dict[t]["reflectivity_eol"],
#             )
#         else:
#             f = interpolate.interp1d(
#                 transmission_dict[t]["wavelength"],
#                 transmission_dict[t]["transmission_eol"],
#             )
#         flux = np.copy(flux) * f(psf.psf_wavelength)
#


# ---------------------------------------------------------------------------------------------
def read_psf_from_fits_file(
    filename: str,
    verbose: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Read psf files depending on simulation and instrument parameters.

    Parameters
    ----------
    filename : str
        Name of the .fits file.
    verbose : bool
        If True information is displayed. Default False.

    Returns
    -------
    psf_datacube : ndarray
        3D array, PSF for each wavelength saved as array, one for each wavelength
        waves (1D array) wavelength. Unit: um.
    psf_wavelength : ndarray
        1D array, wavelengths. Unit: um.
    line_pos_psf : ndarray
        1D array, x position of the PSF at each wavelength.
    col_pos_psf : ndarray
        1D array, y position of the PSF at each wavelength.
    """
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
    if verbose:
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
    psf_datacube: np.ndarray,
    line_psf_pos: Quantity,
    col_psf_pos,
    flux,
    row,
    col,
    expend_factor: float,
) -> tuple[ndarray, ndarray]:
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
def rebin_2d(
    data: np.ndarray,
    expand_factor: float,
    verbose: bool = False,
) -> np.ndarray:
    """
    Rebin as idl.
    Each pixel of the returned image is the sum of zy by zx pixels of the input image.

    Based on:       Rene Gastaud, 13 January 2016
    https://codedump.io/share/P3pB13TPwDI3/1/resize-with-averaging-or-rebin-a-numpy-2d-array
    2017-11-17 : RG and Alan O'Brien  compatibility with python 3 bug452

    Parameters
    ----------
    data : ndarray
        Data with 2 dimensions (image): ny, nx.
    expand_factor : tuple
        Expansion factor is a tuple of 2 integers: zy, zx.
    verbose : bool
        If True information is displayed. Default False.

    Returns
    -------
    result : ndarray
        Shrunk in dimension ny/zy, nx/zx.


    Example
    -------
    a = np.arange(48).reshape((6,8))
               rebin2d( a, [2,2])


    """

    zoom = [expand_factor, expand_factor]  # In case asymmetrical zoom is used
    final_shape = (
        int(data.shape[0] // zoom[0]),
        zoom[0],
        int(data.shape[1] // zoom[1]),
        zoom[1],
    )
    if verbose:
        print("final_shape ", final_shape)
    result = data.reshape(final_shape).sum(3).sum(1)
    return result
