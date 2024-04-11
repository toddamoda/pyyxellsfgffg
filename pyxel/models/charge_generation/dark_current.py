#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Models to generate charge due to dark current process."""
import warnings
from typing import Literal, Optional

import numpy as np
from astropy import constants as const
from astropy.units import Quantity, Unit

from pyxel.detectors import APD, Detector
from pyxel.util import set_random_seed


def calculate_band_gap_varshni(
    band_gap_0: Quantity,
    alpha: Quantity,
    beta: Quantity,
    temperature: Quantity,
) -> Quantity:
    """Return band gap based on Varshni empirical expression.

    Parameters
    ----------
    band_gap_0 : Quantity
        Parameter E_0. Unit: eV
    alpha : Quantity
        Alpha parameter. Unit: eV/K
    beta : Quantity
        Beta parameter. Unit: K
    temperature : Quantity
        Temperature. Unit K

    Notes
    -----
    This function is based on :cite:p:`VARSHNI1967149`

    Returns
    -------
    Quantity
        Band gap value. Unit: eV
    """

    gap = band_gap_0 - (alpha * temperature**2) / (temperature + beta)

    return gap.to("eV")


def calculate_band_gap(
    temperature: Quantity,
    material: Literal["silicon"],
) -> Quantity:
    """Estimate the band gap based on Varshni empirical expression.

    This function calculates the band of a specified semiconductor material.

    Parameters
    ----------
    temperature : Quantity
        The temperature at which the band gap is to be estimated.
        Unit: Kelvin

    material : str
        The material for which the band gap is to be estimated.
        Currently, only 'silicon' is supported.

    Returns
    -------
    Quantity
        The estimated band gap value.
        Unit: electron volts (eV)

    Raises
    ------
    ValueError
        If an unsupported material is specified.

    Notes
    -----
    The Varshni empirical expression (sis given by:
    Eg(T) = Eg(0) - α * T^2 / (T + β)
    where:
        - Eg(T) is the band gap at temperature T,
        - Eg(0) is the band gap at absolute zero temperature,
        - α is a temperature coefficient,
        - β is a fitting parameter.
    """
    if material == "silicon":
        # Constants for silicon based on literature values
        band_gap_0 = Quantity(1.1557, unit="eV")
        alpha = Quantity(7.021e-4, unit="eV / K")
        beta = Quantity(1108.0, unit="K")
    else:
        raise ValueError(f"Unknown 'material': {material:r}")

    # Calculate band gap using Varshni empirical expression
    return calculate_band_gap_varshni(
        band_gap_0=band_gap_0,
        alpha=alpha,
        beta=beta,
        temperature=temperature,
    )


def simulate_dark_signal(
    temperature: Quantity,
    pixel_area: Quantity,
    figure_of_merit: Quantity,
    band_gap: Quantity,
    band_gap_room_temperature: Quantity,
) -> Quantity:
    """Compute average dark current.

    Parameters
    ----------
    temperature : Quantity
        Temperature. Unit: K
    pixel_area : Quantity
        Pixel area. Unit: um^2/pix
    figure_of_merit : Quantity
        Dark current figure of merit. Unit: nA/cm^2
    band_gap : Quantity
        Semiconductor band_gap. Unit: eV
    band_gap_room_temperature : Quantity
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV

    Returns
    -------
    Quantity
        Average dark current. Unit: e-/pixel/s
    """

    # boltzmann constant (in J / K)
    k_b: Quantity = Quantity(const.k_B)

    # electron charge (in C / electron)
    e_0: Quantity = Quantity(const.e) / Unit("electron")

    room_temperature = Quantity(300, unit="K")
    room_temperature_factor: Quantity = (room_temperature ** (3 / 2)) * np.exp(
        -band_gap_room_temperature / (2 * k_b * room_temperature)
    )  # unit: K^{3/2}

    temperature_factor: Quantity = temperature ** (3 / 2) * np.exp(
        -band_gap / (2 * k_b * temperature)
    )  # unit: K^{3/2}

    cste_dark_signal: Quantity = ((figure_of_merit * pixel_area) / e_0).to(
        "electron / (pix s)"
    )

    avg_dark_current: Quantity = (
        cste_dark_signal * temperature_factor / room_temperature_factor
    )  # unit: electron / (pix s)

    return avg_dark_current.to("electron / (pix s)")


def compute_dark_current(
    shape: tuple[int, int],
    time_step: Quantity,
    temperature: Quantity,
    pixel_area: Quantity,
    figure_of_merit: Quantity,
    band_gap: Quantity,
    band_gap_room_temperature: Quantity,
    spatial_noise_factor: Optional[float] = None,
    temporal_noise: bool = True,
) -> np.ndarray:
    """Compute dark current.

    Based on:
    Konnik, Mikhail V. and James S. Welsh.
    “High-level numerical simulations of noise in CCD and CMOS photosensors: review and tutorial.”
    ArXiv abs/1412.4031 (2014): n. pag.

    Parameters
    ----------
    shape : tuple
        Output array shape.
    time_step : Quantity
        Time step. Unit: s
    temperature : Quantity
        Temperature. Unit: K
    pixel_area : Quantity
        Pixel area. Unit: um^2
    figure_of_merit : Quantity
        Dark current figure of merit. Unit: nA/cm^2
    band_gap : Quantity
        Semiconductor band_gap. Unit: eV
    band_gap_room_temperature : Quantity
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV
    spatial_noise_factor: float
        Dark current fixed pattern noise factor.
    temporal_noise: bool
        Shot noise.

    Returns
    -------
    ndarray
        Dark current values. Unit: e-
    """
    # Simulation of dark signal (in electron / pixel)
    avg_dark_current: Quantity = simulate_dark_signal(
        temperature=temperature,
        pixel_area=pixel_area,
        figure_of_merit=figure_of_merit,
        band_gap=band_gap,
        band_gap_room_temperature=band_gap_room_temperature,
    )  # unit: electron / s

    dark_signal_2d: Quantity = (
        np.ones(shape) * avg_dark_current * time_step
    )  # unit: electron / pix

    # Simulation of dark current shot noise (in electron / pixel)
    if temporal_noise:
        # dark current shot noise
        # TODO: Use function 'calculate_simple_dark_current'
        dark_current_shot_noise_2d = np.random.poisson(np.asarray(dark_signal_2d))
        dark_current_2d = Quantity(dark_current_shot_noise_2d, unit="electron / pix")
    else:
        dark_current_2d = dark_signal_2d

    # Simulation of dark current fixed pattern noise (in electron / pixel)
    if spatial_noise_factor is not None:
        # sigma of fixed pattern noise distribution
        dark_current_fpn_sigma = time_step * avg_dark_current * spatial_noise_factor

        with np.errstate(all="ignore"):
            dark_current_fpn_2d = np.random.lognormal(
                sigma=np.asarray(dark_current_fpn_sigma),
            )

        dark_current_2d = dark_current_2d * (1 + dark_current_fpn_2d)

    if np.isinf(dark_current_2d).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise"
            " distribution will result in inf values. Enable a FWC model to ensure a"
            " physical limit.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dark_current_2d


def dark_current(
    detector: Detector,
    figure_of_merit: float,
    spatial_noise_factor: Optional[float] = None,
    band_gap: Optional[float] = None,
    band_gap_room_temperature: Optional[float] = None,
    seed: Optional[int] = None,
    temporal_noise: bool = True,
) -> None:
    """Add dark current to the detector charge.

    Based on:
    Konnik, Mikhail V. and James S. Welsh.
    “High-level numerical simulations of noise in CCD and CMOS photosensors: review and tutorial.”
    ArXiv abs/1412.4031 (2014): n. pag.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    figure_of_merit : float
        Dark current figure of merit. Unit: nA/cm^2
    spatial_noise_factor : float
        Dark current fixed pattern noise factor.
    band_gap : float, optional
        Semiconductor band_gap. If none, the one for silicon is used. Unit: eV
    band_gap_room_temperature : float, optional
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV
    seed : int, optional
        Random seed.
    temporal_noise : bool, optional
        Shot noise.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/dark_current/dark_current_Si`.
    """
    geo = detector.geometry
    pixel_vert_size = Quantity(geo.pixel_vert_size, unit="um")
    pixel_horz_size = Quantity(geo.pixel_horz_size, unit="um")

    pixel_area = (pixel_vert_size * pixel_horz_size) / Unit("pix")  # unit: um^2/pix
    temperature = Quantity(detector.environment.temperature, unit="K")
    time_step = Quantity(detector.time_step, unit="s")

    if band_gap and band_gap_room_temperature:
        final_band_gap = Quantity(band_gap, unit="eV")
        final_band_gap_room_temperature = Quantity(band_gap_room_temperature, unit="eV")
    elif band_gap or band_gap_room_temperature:
        raise ValueError(
            "Both parameters 'band_gap' and 'band_gap_room_temperature' must be defined."
        )
    else:
        final_band_gap = calculate_band_gap(temperature, material="silicon")  # unit: eV

        room_temperature = Quantity(300, unit="K")
        final_band_gap_room_temperature = calculate_band_gap(
            temperature=room_temperature,
            material="silicon",
        )  # unit: eV

    with set_random_seed(seed):
        with warnings.catch_warnings():
            warnings.filterwarnings(action="ignore", category=RuntimeWarning)

            dark_current_2d = compute_dark_current(
                shape=geo.shape,
                time_step=time_step,
                temperature=temperature,
                pixel_area=pixel_area,
                figure_of_merit=Quantity(figure_of_merit, unit="nA / cm2"),
                band_gap=final_band_gap,
                band_gap_room_temperature=final_band_gap_room_temperature,
                spatial_noise_factor=spatial_noise_factor,
                temporal_noise=temporal_noise,
            )  # unit: electron / pix

    detector.charge.add_charge_array(np.asarray(dark_current_2d))


def calculate_simple_dark_current(
    num_rows: int, num_cols: int, current: float, exposure_time: float
) -> np.ndarray:
    """Simulate dark current in a :term:`CCD`.

    This function generates a simulated detector image by dark current noise.

    Parameters
    ----------
    num_rows : int
        Number of rows for the generated image.
    num_cols : int
        Number of columns for the generated image.
    current : float
        Dark current, in e⁻/pixel/second
    exposure_time : float
        Length of the simulated exposure, in seconds.

    Returns
    -------
    ndarray
        An array the same shape and dtype as the input containing dark counts
        in units of charge (e-).
    """
    # Calculate mean dark charge for every pixel
    mean_dark_charge = current * exposure_time

    # Generate dark current noise using poisson distribution
    # This random number generation should change on each call.
    dark_im_array_2d = np.random.poisson(mean_dark_charge, size=(num_rows, num_cols))
    return dark_im_array_2d


def simple_dark_current(
    detector: Detector, dark_rate: float, seed: Optional[int] = None
) -> None:
    """Simulate dark current in a detector.

    Parameters
    ----------
    detector : Detector
        Any detector object.
    dark_rate : float
        Dark current, in e⁻/pixel/second, which is the way
        manufacturers typically report it.
    seed : int, optional
    """

    exposure_time = detector.time_step
    geo = detector.geometry

    with set_random_seed(seed):
        dark_current_array: np.ndarray = calculate_simple_dark_current(
            num_rows=geo.row,
            num_cols=geo.col,
            current=dark_rate,
            exposure_time=exposure_time,
        ).astype(float)

    detector.charge.add_charge_array(dark_current_array)


def calculate_dark_current_saphira(
    temperature: float,
    avalanche_gain: float,
    shape: tuple[int, int],
    exposure_time: float,
) -> np.ndarray:
    """Simulate dark current in a Saphira :term:`APD`.

    From: I. M. Baker et al., Linear-mode avalanche photodiode arrays in HgCdTe at Leonardo, UK: the
    current status, in Image Sensing Technologies: Materials, Devices, Systems, and Applications VI,
    2019, vol. 10980, no. May, p. 20.

    Parameters
    ----------
    temperature
    avalanche_gain
    shape
    exposure_time : float
        Length of the simulated exposure, in seconds.

    Returns
    -------
    ndarray
        An array the same shape and dtype as the input containing dark counts
        in units of charge (e-).
    """

    # We can split the dark current vs. gain vs. temp plot ([5] Fig. 3) into three linear
    # 'regimes': 1) low-gain, low dark current; 2) nominal; and 3) trap-assisted tunneling.
    # The following ignores (1) for now since this only applies at gains less than ~2.

    dark_nominal = (15.6e-12 * np.exp(0.2996 * temperature)) * (
        avalanche_gain
        ** ((-5.43e-4 * (temperature**2)) + (0.0669 * temperature) - 1.1577)
    )
    dark_tunnel = 3e-5 * (avalanche_gain**3.2896)

    # The value we want is the maximum of the two regimes (see the plot):
    dark = max(dark_nominal, dark_tunnel)

    # dark current for every pixel
    mean_dark_charge = dark * exposure_time

    # This random number generation should change on each call.
    dark_im_array_2d = np.random.poisson(mean_dark_charge, size=shape)

    return dark_im_array_2d


def dark_current_saphira(detector: APD, seed: Optional[int] = None) -> None:
    """Simulate dark current in a Saphira APD detector.

    Reference: I. M. Baker et al., Linear-mode avalanche photodiode arrays in HgCdTe at Leonardo, UK: the
    current status, in Image Sensing Technologies: Materials, Devices, Systems, and Applications VI,
    2019, vol. 10980, no. May, p. 20.

    Parameters
    ----------
    detector : APD
        An APD detector object.
    seed : int, optional

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`use_cases/APD/saphira`.
    """

    if not isinstance(detector, APD):
        raise TypeError("Expecting an APD object for detector.")
    if detector.environment.temperature > 100:
        raise ValueError(
            "Dark current estimation is inaccurate for temperatures more than 100 K!"
        )
    if detector.characteristics.avalanche_gain < 2:
        raise ValueError("Dark current is inaccurate for avalanche gains less than 2!")

    exposure_time = detector.time_step

    with set_random_seed(seed):
        dark_current_array: np.ndarray = calculate_dark_current_saphira(
            temperature=detector.environment.temperature,
            avalanche_gain=detector.characteristics.avalanche_gain,
            shape=detector.geometry.shape,
            exposure_time=exposure_time,
        ).astype(float)

    detector.charge.add_charge_array(dark_current_array)
