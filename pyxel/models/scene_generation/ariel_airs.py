"""Pyxel photon generator models."""
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from pyxel.detectors import Detector

from .ariel_airs_calculation import (
    convert_flux,
    integrate_flux,
    project_psfs,
    read_psf_from_fits_file,
    read_star_flux_from_file,
)


# ------------------------------------------------------
def wavelength_dependence_airs(
    detector: Optional[Detector] = None,
    psf_filename: str = "CH1_big_cube_PSFs.fits",
    target_filename: str = "target_flux_SED_00005.dat",
    time_scale: float = 1.0,
) -> None:
    """Generate the photon over the array according to a specific dispersion pattern (ARIEL-AIRS).

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    psf_filename: string
        The location and the filename where the PSFs are located.
    target_filename: string
        The location and the filename of the target file used in the simulation.
    """
    # Extract information from the PSF
    psf_datacube, psf_wavelength, line_psf_pos, col_psf_pos = read_psf_from_fits_file(
        filename=psf_filename
    )
    # plt.figure()
    # plt.pcolormesh(psf_datacube[10, :, :])
    # plt.title(psf_wavelength[10])

    # Read flux from the fits file
    target_wavelength, target_flux = read_star_flux_from_file(filename=target_filename)

    # convert the flux by multiplying by the area of the detector
    telescope_diameter_m1, telescope_diameter_m2 = (
        1.1,
        0.7,
    )  # in m, TODO to be replaced by Telescope Class ?

    target_conv_flux = convert_flux(
        wavelength=target_wavelength,
        flux=target_flux,
        telescope_diameter_m1=telescope_diameter_m1,
        telescope_diameter_m2=telescope_diameter_m2,
    )
    # Integrate the flux over the PSF spectral bin
    integrated_flux = integrate_flux(
        target_wavelength, target_conv_flux, psf_wavelength
    )  # The flux is now sample similarly to the PSF

    # The Flux can be multiplied here by the optical elements
    # multiply_by_transmission(psf, transmission_dict)
    # #TODO add class to take into account the transmission of the instrument
    # Project the PSF onto the Focal Plane, to get the detector image
    row, col = 130, 64  # Could be replaced
    expend_factor = 18  # Expend factor used
    photon_incident, photo_electron_generated = project_psfs(
        psf_datacube=psf_datacube,
        line_psf_pos=line_psf_pos,
        col_psf_pos=col_psf_pos,
        flux=integrated_flux,
        row=row,
        col=col,
        expend_factor=expend_factor,
    )
    # Add the result to the photon array structure
    time_step = 1.0

    if detector:
        photon_array = photo_electron_generated * (time_step / time_scale)

        try:
            detector.photon.array += photon_array
        except ValueError as ex:
            raise ValueError("Shapes of arrays do not match") from ex

    # PLOT, to be deleted when implemented in Pyxel
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(target_wavelength, target_flux)
    ax.set_xlabel("target_wavelength")
    ax.set_ylabel("target_flux")

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(psf_wavelength, integrated_flux)
    ax.set_xlabel("psf_wavelength")
    ax.set_ylabel("integrated_flux")

    print(np.shape(photo_electron_generated))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(photo_electron_generated)
    ax.set_title("photo_electron_generated")
    ax.set_xlabel("Pixels")
    ax.set_ylabel("Pixels")


# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    psf_filename = "CH1_big_cube_PSFs.fits"
    target_filename = "Noodles_ch1/SED_004.dat"

    wavelength_dependence_airs(
        time_scale=1.0,
        psf_filename=psf_filename,
        target_filename=target_filename,
    )

    plt.show()
