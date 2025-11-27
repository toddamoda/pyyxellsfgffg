#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple models to generate charge due to dark current process."""

import warnings
from typing import Annotated

import numpy as np
from annotated_types import Ge, Interval, Unit

from pyxel.detectors import CCD, CMOS
from pyxel.util import set_random_seed

warnings.filterwarnings("once", category=RuntimeWarning, append=True)


def lambda_e(lambda_cutoff: float) -> float:
    """Compute the effective wavelength (lambda_e) based on a detector's wavelength cut-off."""
    lambda_scale = 0.200847413  # (µm)
    lambda_threshold = 4.635136423  # (µm)
    pwr = 0.544071282

    if lambda_cutoff < lambda_threshold:
        le = lambda_cutoff / (
            1
            - ((lambda_scale / lambda_cutoff) - (lambda_scale / lambda_threshold))
            ** pwr
        )
    else:
        le = lambda_cutoff

    return le


def average_dark_current_rule07(
    pitch: float,
    temperature: float,
    cut_off: float,
) -> float:
    """Compute the average dark current for a detector using the Rule07 empirical law."""
    c = 1.16
    q = 1.602e-19  # Charge of one electron (in A·s)
    k = 1.3806504e-23  # Boltzmann constant (m² kg s⁻² K⁻¹)

    j0 = 8367  # from experimental fit

    e_c = 1.24 / lambda_e(cut_off)

    rule07 = j0 * np.exp(-c * q * e_c / (k * temperature))

    amp_to_eps = 6.242e18  # A → e⁻/s
    um2_to_cm2 = 1.0e-8

    factor = amp_to_eps * pitch * pitch * um2_to_cm2
    return rule07 * factor


def compute_mct_dark_rule07(
    shape: tuple[int, int],
    pitch: float,
    time_step: float,
    temperature: float,
    cut_off: float,
    spatial_noise_factor: float | None = None,
    temporal_noise: bool = True,
) -> np.ndarray:
    """Compute 2D dark current array."""
    avg_dark_current_rule07 = average_dark_current_rule07(
        pitch=pitch,
        temperature=temperature,
        cut_off=cut_off,
    )

    dark_signal_2d_rule07 = np.ones(shape) * avg_dark_current_rule07 * time_step

    if temporal_noise:
        dark_current_2d_rule07 = np.random.poisson(dark_signal_2d_rule07).astype(float)
    else:
        dark_current_2d_rule07 = dark_signal_2d_rule07

    if spatial_noise_factor is not None:
        sigma = time_step * avg_dark_current_rule07 * spatial_noise_factor
        dark_current_2d_rule07 = dark_current_2d_rule07 * (
            1 + np.random.lognormal(sigma=sigma, size=shape)
        )

    if np.isinf(dark_current_2d_rule07).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise distribution.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dark_current_2d_rule07


def dark_current_rule07(
    detector: CCD | CMOS,
    cutoff_wavelength: Annotated[
        float,
        Interval(ge=1.7, le=15.0),
        Unit("um"),
    ] = 2.5,
    spatial_noise_factor: Annotated[float, Ge(0.0)] | None = None,
    seed: int | None = None,
    temporal_noise: bool = True,
) -> None:
    """Generate charge from dark current process using the Rule07 model."""
    if not isinstance(detector, CCD | CMOS):
        raise TypeError("Expecting a CCD or CMOS object for detector.")

    if not (1.7 <= cutoff_wavelength <= 15.0):
        raise ValueError("'cutoff' must be between 1.7 and 15.0.")

    geo = detector.geometry

    pitch = geo.pixel_vert_size
    temperature = detector.environment.temperature
    time_step = detector.time_step

    with set_random_seed(seed):
        dark_current_array_rule07 = compute_mct_dark_rule07(
            pitch=pitch,
            temperature=temperature,
            cut_off=cutoff_wavelength,
            shape=geo.shape,
            time_step=time_step,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
        )

    detector.charge.add_charge_array(dark_current_array_rule07)
