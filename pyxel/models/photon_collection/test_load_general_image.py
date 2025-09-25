import numpy as np
import pandas as pd
import pytest
from pyxel.detectors import Detector, ReadoutProperties
from pyxel.models.photon_collection import load_general_image


def make_test_detector():
    """Create a minimal CCD detector with initialized photon container."""
    columns = [
        "charge", "number", "init_energy", "energy",
        "init_pos_ver", "init_pos_hor", "init_pos_z",
        "position_ver", "position_hor", "position_z",
        "velocity_ver", "velocity_hor", "velocity_z"
    ]

    detector = Detector.from_dict({
        "type": "CCD",
        "version": 1,
        "properties": {
            "geometry": {
                "row": 10,
                "col": 10,
                "total_thickness": 40.0,
                "pixel_vert_size": 12.0,
                "pixel_horz_size": 12.0,
                "pixel_scale": 1.0,
            },
            "environment": {"temperature": 150.0, "wavelength": 600.0},
            "characteristics": {
                "adc_bit_resolution": 16,
                "adc_voltage_range": [0.0, 10.0],
                "charge_to_volt_conversion": 1e-6,
                "full_well_capacity": 100000,
                "pre_amplification": 100.0,
                "quantum_efficiency": 0.8,
            },
        },
        "data": {
            "photon": {"array": np.zeros((10, 10))},
            "digital": {"array": np.zeros((10, 10))},
            "voltage": {"array": np.zeros((10, 10))},
            "charge": {
                "array": np.zeros((10, 10)),
                "frame": pd.DataFrame(columns=columns),
            },
        },
    })

    # Add readout properties
    detector._readout_properties = ReadoutProperties(times=[1.0])

    # Explicitly initialize photon container
    detector.photon._array = np.zeros((10, 10), dtype=float)

    return detector


def test_load_general_image_png(tmp_path):
    """Test that a PNG image can be loaded as xarray."""
    import imageio.v2 as iio

    detector = make_test_detector()

    # Create dummy PNG image
    img_path = tmp_path / "dummy.png"
    iio.imwrite(img_path, np.ones((10, 10), dtype=np.uint8) * 50)

    result = load_general_image(
        detector, str(img_path),
        convert_to_photons=False,
        return_as="xarray"
    )

    assert result.shape == (10, 10)
    assert np.all(result.values == 50.0)


def test_load_general_image_fits(tmp_path):
    """Test that a FITS image can be loaded as xarray."""
    from astropy.io import fits

    detector = make_test_detector()

    # Create dummy FITS image
    fits_path = tmp_path / "dummy.fits"
    hdu = fits.PrimaryHDU(np.ones((10, 10), dtype=np.float32) * 42)
    hdu.writeto(fits_path)

    result = load_general_image(
        detector, str(fits_path),
        convert_to_photons=False,
        return_as="xarray"
    )

    assert result.shape == (10, 10)
    assert np.all(result.values == 42.0)
