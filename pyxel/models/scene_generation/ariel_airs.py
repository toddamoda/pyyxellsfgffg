"""Pyxel photon generator models."""
# Add Licence from CEA/ TPichon

# import matplotlib.pyplot as plt
import numpy as np

from pyxel.detectors import Detector
from pyxel.models.scene_generation.ariel_airs_calculation import (
    convert_flux,
    integrate_flux,
    project_psfs,
    read_psf_from_fits_file,
    read_star_flux_from_file,
)


def wavelength_dependence_airs(
    detector: Detector,
    psf_filename: str,
    target_filename: str,
    telescope_diameter_m1: float,
    telescope_diameter_m2: float,
    expand_factor: int,
    time_scale: float = 1.0,
) -> None:
    """Generate the photon over the array according to a specific dispersion pattern (ARIEL-AIRS).

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    psf_filename : string
        The location and the filename where the PSFs are located.
    target_filename : string
        The location and the filename of the target file used in the simulation.
    telescope_diameter_m1 : float
        Diameter of the M1 mirror of the TA in m.
    telescope_diameter_m2 : float
        Diameter of the M2 mirror of the TA in m.
    expand_factor : int
        Expansion factor used.
    time_scale : float
        Time scale in seconds.
    """
    if not isinstance(expand_factor, int):
        raise TypeError("Expecting a 'int' type for 'expand_factor'.")

    if expand_factor <= 0:
        raise ValueError("Expecting a positive value for 'expand_factor'.")

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
    # telescope_diameter_m1, telescope_diameter_m2 = (
    #     1.1,
    #     0.7,
    # )  # in m, TODO to be replaced by Telescope Class ?

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

    # row, col = 130, 64  # Could be replaced
    # Expend factor used: expand_factor = 18
    photon_incident, photo_electron_generated = project_psfs(
        psf_datacube_3d=psf_datacube,
        line_psf_pos_1d=line_psf_pos,
        col_psf_pos=col_psf_pos,
        flux=integrated_flux,
        row=detector.geometry.row,
        col=detector.geometry.col,
        expand_factor=expand_factor,
    )
    # Add the result to the photon array structure
    time_step = 1.0  # ?

    photon_array = photo_electron_generated * (time_step / time_scale)
    assert photon_array.unit == "electron"

    detector.photon.array += np.array(photon_array)
