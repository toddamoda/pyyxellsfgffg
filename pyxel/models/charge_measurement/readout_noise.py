#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout noise model."""

from typing import Literal, Tuple

import numpy as np

from pyxel.detectors import APD, CMOS, Detector
from pyxel.util import (
    load_cropped_and_aligned_image,
    set_random_seed,
)


def output_node_noise(
    detector: Detector,
    std_deviation: float,
    seed: int | None = None,
) -> None:
    """Add noise to signal array of detector output node using normal random distribution.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    std_deviation : float
        Standard deviation. Unit: V
    seed : int, optional
        Random seed.

    Raises
    ------
    ValueError
        Raised if 'std_deviation' is negative
    """
    if std_deviation < 0.0:
        raise ValueError("'std_deviation' must be positive.")

    with set_random_seed(seed):
        noise_2d: np.ndarray = np.random.normal(
            scale=std_deviation,
            size=detector.signal.shape,
        )

    detector.signal.array += noise_2d


def compute_readout_noise_saphira(
    roic_readout_noise: float,
    avalanche_gain: float,
    shape: tuple[int, int],
    controller_noise: float = 0.0,
) -> np.ndarray:
    """Compute Saphira specific readout noise.

    Parameters
    ----------
    roic_readout_noise : float
        Readout integrated circuit noise in volts RMS. Unit: V
    avalanche_gain : float
        Avalanche gain.
    shape : tuple
        Shape of the output array.
    controller_noise : float
        Controller noise in volts RMS. Unit: V

    Returns
    -------
    ndarray
    """

    noise_factor = (((1.2 - 1.0) / np.log10(1000)) * np.log10(avalanche_gain)) + 1.0

    total_noise_level = np.sqrt(
        (roic_readout_noise * noise_factor) ** 2 + controller_noise**2
    )

    total_noise = np.random.normal(scale=total_noise_level, size=shape)

    return total_noise


def readout_noise_saphira(
    detector: APD,
    roic_readout_noise: float,
    controller_noise: float = 0.0,
    seed: int | None = None,
) -> None:
    """Apply Saphira specific readout noise to the APD detector.

    Parameters
    ----------
    detector : APD
        Pyxel APD object.
    roic_readout_noise : float
        Readout integrated circuit noise in volts RMS. Unit: V
    controller_noise : float
        Controller noise in volts RMS. Unit: V
    seed : int, optional

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`use_cases/APD/saphira`.
    """

    if not isinstance(detector, APD):
        raise TypeError("Expecting a 'APD' detector object.")

    with set_random_seed(seed):
        noise_2d = compute_readout_noise_saphira(
            roic_readout_noise=roic_readout_noise,
            avalanche_gain=detector.characteristics.avalanche_gain,
            shape=detector.geometry.shape,
            controller_noise=controller_noise,
        )

    detector.signal += noise_2d

def apply_noise_user_array(
        detector: Detector,
        noise: np.array
) -> None:
    detector.signal += noise

def readout_noise_user_array(
        detector: Detector,
        filename: str,
        position: tuple[int, int] = (0,0),
        align: (
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
        ) = None,
) -> None:
    """Apply the user-supplied readout noise array to the signal array.

    Parameters
    ----------
    detector : Detctor
        Detector object.
    filename : str
        Path to the array or image.
    position: tuple[int, int]
        Starting row and column of the fixed dark current.
    align: Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    """
    noise_user_array = load_cropped_and_aligned_image(
        shape=(detector.geometry.row,detector.geometry.col),
        filename=filename,
        position_x=position[0],
        position_y=position[1],
        align=align,
    )

    # and pass it of to the "pure" function that does the actual application
    apply_noise_user_array(detector, noise_user_array)

def create_output_node_noise_cmos_user_array(
    shape : Tuple[int, int],
    sigma : np.ndarray,
    offset : np.ndarray,
    charge_readout_sensitivity: float | np.ndarray,
    seed: np.random.Generator
) -> np.ndarray:
    
    # Create an array for sensitivities that matches the detector's shape
    if not isinstance(charge_readout_sensitivity, np.ndarray):
        sensitivity_2d = np.full(shape=shape, fill_value=charge_readout_sensitivity)
    else:
        sensitivity_2d = charge_readout_sensitivity

    # Draws a value for each pixel
    # Assumes offset, scale, and sensitivity are same size of array
    noise = seed.normal(loc=offset*sensitivity_2d, scale=sigma*sensitivity_2d)
    
    return noise

def output_node_noise_cmos_user_array(
    detector: CMOS,
    sigma_path: str,
    offset_path: str,
    seed: np.random.Generator = None
) -> None :
    """Applies readout noise with a normal distribution. Each pixel has its own
    sigma and offset (mean).
    
    Parameters
    ----------
    detector: CMOS
        Detector object.
    sigma_path : str
        Path to 2d array of sigma values for each pixel
    offset_path : str
        Path to 2d array of offset (mean) values for each pixel
    """

    try: # valid sigma array?
        sigma = np.load(sigma_path)
    except:
        raise ValueError("Sigma array is invalid.")
    
    try: # valid offset array?
        offset = np.load(offset_path)
    except:
        raise ValueError("Offset array is invalid.")
    
    if sigma.shape != offset.shape: # The arrays need to match up
        raise ValueError("Sigma and Offset arrays are different shapes.")
    
    if sigma.shape != detector.geometry.shape: # and they should be the same shape as the detector
        raise ValueError("Sigma array shape does not match detector geometry.")
    
    # use gain array. If no gain array, use charge to volt conv value
    try:
        if detector.characteristics.gain_array is not None:
            vr_min = detector.characteristics.adc_voltage_range[0]
            vr_max = detector.characteristics.adc_voltage_range[1]
            gain_array = detector.characteristics.gain_array
            bit_res = detector.characteristics.adc_bit_resolution
            # save as shorter names for readability
            charge_readout_sensitivity = ((vr_max - vr_min) / (2**bit_res) / gain_array)
    except AttributeError:
        charge_readout_sensitivity = detector.characteristics.charge_to_volt_conversion

    if seed is None:
        seed = np.random.default_rng()
    
    noise = create_output_node_noise_cmos_user_array(
        shape=detector.geometry.shape,
        sigma=sigma,
        offset=offset,
        charge_readout_sensitivity=charge_readout_sensitivity,
        seed=seed
    )
    
    detector.signal.array += noise