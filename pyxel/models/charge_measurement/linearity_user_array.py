#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np

from pyxel.detectors import CMOS, Detector

def compute_poly_linearity_user_array(
    array_2d: np.ndarray,
    coefficients: np.ndarray,
) -> np.ndarray:
    """Add non-linearity to an array of values following an array of polynomial
    coeffieicents. This will create and then apply the functions.

    Parameters
    ----------
    array_2d : ndarray
        Input array.
    coefficients : 2D np array of floats
        List of coefficients of each polynomial function arranged by row and
        column.

    Returns
    -------
    np.ndarray
        Signal.
    """
    # for every set of coefficients, create the polynomial function
    signal = []
    for i in range(0, len(coefficients)):
        row = []
        for j in range(0, len(coefficients[i])):
            polynomial_function = np.polynomial.polynomial.Polynomial(coefficients[i][j])
            row.append(polynomial_function(array_2d[i][j]))
        signal.append(row)

    return np.array(signal)

def output_node_linearity_poly_user_array(
    detector: Detector,
    path: str,
) -> None:
    """Add non-linearity to signal array to simulate the non-linearity of the output node circuit.

    The non-linearity is simulated by a polynomial function per pixel. The user specifies the
    polynomial coefficients with each array element.

    detector Signal unit: Volt

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    path : str
        Path to file containing coefficients for each of the polynomial functions.

    """
    # parse the user array
    try:
        array = np.load(path)
    except:
        raise ValueError("Invalid path given.")
    
    try:
        vr_min = detector.characteristics.adc_voltage_range[0]
        vr_max = detector.characteristics.adc_voltage_range[1]
        gain_array = detector.characteristics.gain_array
        bit_res = detector.characteristics.adc_bit_resolution
        # save as shorter names for readability
        array = array * ((vr_max - vr_min) / (2**bit_res) / gain_array)
    except AttributeError:
        array = array * detector.characteristics.charge_to_volt_conversion

    signal_mean_array = detector.signal.array.astype("float64")
    signal_non_linear = compute_poly_linearity_user_array(
        array_2d=signal_mean_array, coefficients=array
    )

    signal_non_linear = signal_non_linear.clip(min=0.0)
    detector.signal.array = signal_non_linear