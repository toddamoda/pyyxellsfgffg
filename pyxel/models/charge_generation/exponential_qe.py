#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to calculate the QE based on the characteristics of the detector (Front/Back Illumination, Charge Collection Efficiency, Absorption coefficient, Reflectivity, Epilayer thickness, Poly gate thickness)."""

import logging
import math
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import xarray as xr
from astropy.units import Quantity

if TYPE_CHECKING:
    from pyxel.detectors import Detector


# TODO: Decrease complexity
# ruff: noqa: C901
def exponential_qe(
    detector: "Detector",
    filename: str | Path,
    x_epi: float,
    detector_type: str,  # BI: Back-Illuminated, FI: Front-Illuminated
    default_wavelength: str | float | None = None,  # User must provide a value
    x_poly: float = 0.0,  # Default x_poly to 0.0, change only if the detector is front-illuminated
    delta_t: float = 0.0,  # Temperature difference from 300 K
    cce: float = 1.0,  # Default Charge Collection Efficiency (CCE)
) -> None:
    """
    Apply QE with temperature correction for absorptivity using a provided or backup coefficient `c`.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        Path to the CSV file containing reflectivity, absorptivity, and c.
    x_epi : float
        Thickness of the epitaxial layer in cm.
    detector_type : str
        Type of detector ("BI" for Back-Illuminated, "FI" for Front-Illuminated).
    default_wavelength : str or float
        Wavelength in nm for 2D photon arrays, or 'multi' for multiple wavelengths (no default value).
    x_poly : float
        Thickness of the poly layer in cm.
    delta_t : float
        Temperature difference from 300 K (default: 0.0).
    cce : float
        Charge Collection Efficiency (default: 1.0).
    """
    # Validate delta_t to ensure resulting temperature is 300 K
    resulting_temperature = detector.environment.temperature - delta_t
    # Validate if resulting_temperature is close to 300 K
    if not math.isclose(resulting_temperature, 300, abs_tol=0.01):
        raise ValueError(
            "The temperature provided does not match with the environment."
        )
    # Ensure default_wavelength is provided
    if default_wavelength is None:
        raise ValueError(
            "You must specify a `default_wavelength` value in nm or use 'multi' for multiple wavelengths."
        )

    # Define valid wavelength range for the equation
    valid_wavelength_range = (250.0, 1450.0)  # Range in nm

    # Validate default_wavelength for single-wavelength mode
    if isinstance(default_wavelength, int | float) and not (
        valid_wavelength_range[0] <= default_wavelength <= valid_wavelength_range[1]
    ):
        raise ValueError("Wavelength is out of the valid range " "for the equation.")

    # Validate detector_type
    if detector_type not in ["BI", "FI"]:
        raise ValueError(
            "Invalid detector type. Choose 'BI' (Back-Illuminated) or 'FI' (Front-Illuminated)."
        )

    # Enforce x_poly = 0 for Back-Illuminated detectors
    if detector_type == "BI" and x_poly != 0.0:
        logging.warning(
            "Warning: x_poly should be 0 for Back-Illuminated detectors. Setting x_poly to 0."
        )
        x_poly = 0.0

    # Validate non-negative thickness values
    if x_epi < 0 or x_poly < 0:
        raise ValueError(
            "Epitaxial thickness (x_epi) and poly layer thickness (x_poly) must be non-negative."
        )

    # Step 1: Detect the shape of the photon array
    if detector.photon.ndim == 2:
        photon_2d: np.ndarray = detector.photon.array_2d

        if default_wavelength == "multi":
            raise ValueError(
                "Photon array is 2D, but you specified 'multi' for `default_wavelength`. Ensure the photon array matches your wavelength input."
            )
        elif isinstance(default_wavelength, int | float):
            logging.info(
                "Photon array is 2D. Transforming it into a 3D array with a single wavelength slice."
            )
            dummy_wavelength = np.array([default_wavelength])  # Single wavelength value

            # Generate coordinates for x and y
            y_coords = np.arange(photon_2d.shape[0])  # Row indices
            x_coords = np.arange(photon_2d.shape[1])  # Column indices

            # Create 3D xarray DataArray
            photon_array_3d = xr.DataArray(
                np.expand_dims(photon_2d, axis=0),  # Add wavelength as a new dimension
                coords={"wavelength": dummy_wavelength, "y": y_coords, "x": x_coords},
                dims=["wavelength", "y", "x"],
            )
        else:
            raise ValueError(
                "Invalid `default_wavelength` value. Must be a numeric value in nm or 'multi' for multiple wavelengths."
            )

    elif detector.photon.ndim == 3:
        if default_wavelength != "multi":
            print(
                "Photon array is 3D, but `default_wavelength` is not 'multi'. Proceeding with the existing wavelength data."
            )
        print("Photon array is 3D. Proceeding normally.")
        photon_array_3d = detector.photon.array_3d

    else:
        raise ValueError(
            f"Unexpected photon array dimensions: {detector.photon.shape}. Expected 2D or 3D."
        )

    # Convert x_epi to Quantity
    x_epi_cm = Quantity(x_epi, unit="cm")
    x_poly_cm = Quantity(x_poly, unit="cm")

    # Read total detector thickness from the detector object
    total_thickness = Quantity(detector.geometry.total_thickness, unit="um")
    if x_epi_cm > total_thickness.to("cm"):
        raise ValueError("x_epi cannot be greater than the total detector thickness.")

    # Load data from the provided CSV file
    qe_data = pd.read_csv(filename)

    # Check for required columns
    required_columns = ["reflectivity", "absorptivity", "wavelength"]
    if not set(required_columns).issubset(qe_data.columns):
        raise ValueError(
            f"CSV file must contain the columns: {', '.join(required_columns)}"
        )

    # Validate that no NaN values exist in the required columns
    nan_columns = [col for col in required_columns if qe_data[col].isna().any()]
    if nan_columns:
        raise ValueError(
            "NaN values found in the file. All values for 'wavelength', 'reflectivity', and 'absorptivity' must be present."
        )

    # Validate that no negative values exist in the required columns
    negative_columns = [col for col in required_columns if (qe_data[col] < 0).any()]
    if negative_columns:
        raise ValueError(
            f"Negative values found in the following columns: {', '.join(negative_columns)}. "
            f"All values for 'wavelength', 'reflectivity', and 'absorptivity' must be non-negative."
        )

    # Extract data
    reflectivity = qe_data["reflectivity"].values
    absorptivity = Quantity(qe_data["absorptivity"].values, unit="1/cm")
    wavelength = Quantity(qe_data["wavelength"].values, unit="nm")

    # Embedded full-range `c` values provided by the developers
    embedded_c_values = Quantity(
        [
            -9.00e-05,
            -1.50e-04,
            -3.10e-04,
            -3.30e-04,
            8.00e-05,
            2.50e-04,
            3.20e-04,
            1.50e-04,
            7.00e-05,
            3.00e-05,
            0.00e00,
            -1.40e-04,
            4.20e-04,
            9.10e-04,
            2.60e-03,
            3.30e-03,
            3.10e-03,
            2.90e-03,
            2.90e-03,
            2.80e-03,
            2.80e-03,
            2.90e-03,
            2.90e-03,
            3.00e-03,
            3.00e-03,
            3.10e-03,
            3.10e-03,
            3.20e-03,
            3.30e-03,
            3.30e-03,
            3.30e-03,
            3.40e-03,
            3.40e-03,
            3.40e-03,
            3.40e-03,
            3.40e-03,
            3.50e-03,
            3.50e-03,
            3.50e-03,
            3.50e-03,
            3.50e-03,
            3.50e-03,
            3.60e-03,
            3.60e-03,
            3.60e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.70e-03,
            3.80e-03,
            4.00e-03,
            4.10e-03,
            4.20e-03,
            4.40e-03,
            4.50e-03,
            4.60e-03,
            4.70e-03,
            4.90e-03,
            5.10e-03,
            5.20e-03,
            5.40e-03,
            5.60e-03,
            5.70e-03,
            5.90e-03,
            6.20e-03,
            6.50e-03,
            6.90e-03,
            7.30e-03,
            7.80e-03,
            8.30e-03,
            9.00e-03,
            9.70e-03,
            1.05e-02,
            1.12e-02,
            1.20e-02,
            1.35e-02,
            1.45e-02,
            1.55e-02,
            1.60e-02,
            1.65e-02,
            1.75e-02,
            1.80e-02,
            1.85e-02,
            1.90e-02,
            2.00e-02,
            2.10e-02,
            2.30e-02,
            2.60e-02,
            3.20e-02,
            3.45e-02,
            3.55e-02,
            3.80e-02,
            3.90e-02,
            4.05e-02,
            4.10e-02,
            4.30e-02,
            4.40e-02,
            4.55e-02,
            4.70e-02,
            5.00e-02,
            5.25e-02,
            5.50e-02,
            5.80e-02,
            6.10e-02,
            6.50e-02,
            6.70e-02,
            6.75e-02,
            6.80e-02,
            6.85e-02,
            6.90e-02,
            7.00e-02,
            7.10e-02,
            7.20e-02,
            7.30e-02,
            7.40e-02,
            7.50e-02,
        ],
        unit="1/K",
    )  # Embedded c-values

    embedded_absorptivity_values = Quantity(
        [
            1840219.313,
            1970020.255,
            2180032.591,
            2370107.258,
            2290112.714,
            1770182.741,
            1460131.192,
            1299833.96,
            1180096.44,
            1099927.028,
            1059883.602,
            1039867.168,
            737000.655,
            313001.8365,
            142998.8533,
            92991.14255,
            69513.48428,
            52688.99679,
            40212.38597,
            30701.92821,
            24099.50631,
            19499.72901,
            16600.97769,
            14398.96633,
            12599.70996,
            11101.1318,
            9700.745315,
            8798.87604,
            7850.425114,
            7051.130178,
            6390.570656,
            5780.530483,
            5319.76356,
            4879.218383,
            4489.815128,
            4174.129439,
            3800.812096,
            3520.610606,
            3279.224332,
            3029.673415,
            2789.734276,
            2570.393989,
            2389.485994,
            2199.114858,
            2039.758708,
            1890.34118,
            1780.530822,
            1680.053938,
            1539.982897,
            1419.999879,
            1309.918473,
            1190.002228,
            1099.965428,
            1029.959068,
            928.0026097,
            849.9578924,
            774.9261879,
            706.9349713,
            646.9409836,
            590.0210203,
            533.9968313,
            478.9832892,
            431.012068,
            382.9887044,
            342.9630811,
            302.9891581,
            270.9364741,
            239.9903605,
            209.0341434,
            183.0144827,
            155.9552732,
            134.0412866,
            112.9936954,
            96.00450693,
            79.00312192,
            64.00052554,
            51.09909318,
            39.90438669,
            30.19589055,
            22.59530101,
            16.30037788,
            11.09989887,
            8.000197815,
            6.200573056,
            4.700283761,
            3.500305415,
            2.700071524,
            2.000521322,
            1.500179996,
            1.000018546,
            0.680004559,
            0.419998439,
            0.219965188,
            0.065004344,
            0.035998956,
            0.022001621,
            0.013002559,
            0.008200072,
            0.004699618,
            0.002399771,
            0.000999982,
            0.000360036,
            0.000199974,
            0.00011997,
            7.1e-05,
            4.5e-05,
            2.7e-05,
            1.6e-05,
            8e-06,
            3.5e-06,
            1.7e-06,
            9.5e-07,
            6e-07,
            3.8e-07,
            2.3e-07,
            1.4e-07,
            8.5e-08,
            5e-08,
            2.5e-08,
            1.8e-08,
            1.2e-08,
        ],
        unit="1/cm",
    )

    embedded_wavelengths = Quantity(
        np.arange(250, 1460, 10), unit="nm"
    )  # Wavelengths for embedded `c` values

    # Check if the 'c' column exists, otherwise use embedded values
    if "c" in qe_data.columns:
        # Check for NaN values in the 'c' column
        if qe_data["c"].isna().any():
            raise ValueError(
                "NaN values found in the 'c' column. All values must be present."
            )
        c_values = Quantity(qe_data["c"].values, unit="1/K")
    else:
        c_values = (
            np.interp(
                x=wavelength.value,  # Use the numeric values of wavelength
                xp=embedded_wavelengths.value,  # Use the numeric values of embedded wavelengths
                fp=embedded_c_values.value,  # Use the numeric values of embedded c-values
            )
            * embedded_c_values.unit
        )  # Add the unit back to the interpolated result
        absorptivity = (
            np.interp(
                x=wavelength.value,  # Use the numeric values of wavelength
                xp=embedded_wavelengths.value,  # Use the numeric values of embedded wavelengths
                fp=embedded_absorptivity_values.value,  # Use the numeric values of embedded c-values
            )
            * embedded_c_values.unit
        )  # Add the unit back to the interpolated result

    # Correct absorptivity for temperature, if delta_t != 0
    if delta_t != 0:
        delta_t = Quantity(delta_t, unit="K")
        absorptivity = absorptivity * np.exp(c_values * delta_t)

    # Define the QE formula based on the detector type
    if detector_type == "BI":
        qe = cce * (1 - reflectivity) * (1 - np.exp(-x_epi_cm * absorptivity))
    elif detector_type == "FI":
        qe = (
            cce
            * (1 - reflectivity)
            * np.exp(-x_poly_cm * absorptivity)
            * (1 - np.exp(-x_epi_cm * absorptivity))
        )
    else:
        raise ValueError("Invalid detector type. Choose 'BI' or 'FI'.")

    # Create an xarray Dataset for QE, aligned to wavelength
    qe_dataset = xr.Dataset(
        {"QE": (["wavelength"], qe)},
        coords={"wavelength": wavelength},
    )

    qe_interpolated = qe_dataset.interp(wavelength=photon_array_3d["wavelength"])
    charge_array = photon_array_3d * qe_interpolated["QE"]
    # Check the number of wavelengths in charge_array
    if len(charge_array["wavelength"]) == 1:
        # If only one wavelength, squeeze the wavelength dimension
        charges = charge_array.squeeze(dim="wavelength")
        print("Single wavelength detected. Skipping integration over wavelength.")
    else:
        # Otherwise, integrate over the wavelength
        charges = charge_array.integrate(coord="wavelength")
        print("Multiple wavelengths detected. Performing integration over wavelength.")

    # Add charges to the detector
    detector.charge.add_charge_array(np.asarray(charges))
