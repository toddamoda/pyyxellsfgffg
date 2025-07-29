#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
import numpy as np
import pytest

from pyxel.detectors import (
    APD,
    CCD,
    CMOS,
    APDCharacteristics,
    APDGeometry,
    CCDGeometry,
    Channels,
    Characteristics,
    CMOSGeometry,
    Environment,
)
from pyxel.detectors.channels import Matrix, ReadoutPosition
from pyxel.models.charge_measurement import (
    output_node_noise,
    output_node_noise_cmos,
    readout_noise_saphira,
    fixed_readout_noise
)


@pytest.fixture
def ccd_2x3() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=2,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector


@pytest.fixture
def cmos_2x3() -> CMOS:
    """Create a valid CMOS detector."""
    detector = CMOS(
        geometry=CMOSGeometry(
            row=2,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(charge_to_volt_conversion=0.01),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector


@pytest.fixture
def apd_2x3() -> APD:
    """Create a valid CCD detector."""
    detector = APD(
        geometry=APDGeometry(
            row=2,
            col=3,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=APDCharacteristics(
            quantum_efficiency=1.0,
            adc_voltage_range=(0.0, 10.0),
            adc_bit_resolution=16,
            full_well_capacity=100000,
            avalanche_gain=1.0,
            pixel_reset_voltage=5.0,
            roic_gain=0.8,
        ),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)
    return detector


@pytest.mark.parametrize("detector_type", ["ccd", "cmos"])
@pytest.mark.parametrize(
    "std_deviation",
    [pytest.param(1.0, id="std positive"), pytest.param(0.0, id="std null")],
)
def test_output_node_noise(
    ccd_2x3: CCD,
    cmos_2x3: CMOS,
    detector_type: str,
    std_deviation: float,
):
    """Test model 'output_node_noise' with valid inputs."""
    if detector_type == "ccd":
        detector: CCD | CMOS = ccd_2x3
    elif detector_type == "cmos":
        detector = cmos_2x3
    else:
        raise NotImplementedError

    seed = 12345
    rng = np.random.default_rng(seed=seed)
    signal_2d = rng.random(size=(2, 3), dtype=float)
    detector.signal.array = signal_2d.copy()

    output_node_noise(
        detector=detector,
        std_deviation=std_deviation,
        seed=seed,
    )

    new_signal = detector.signal.array

    if std_deviation == 1.0:
        exp_signal = np.array(
            [[0.02262836, 0.79570168, 0.27792674], [0.12052437, 2.35689012, 1.72621976]]
        )
    else:
        exp_signal = signal_2d

    np.testing.assert_allclose(actual=new_signal, desired=exp_signal, rtol=1e-6)


@pytest.mark.parametrize("detector_type", ["ccd", "cmos"])
def test_output_node_noise_bad_std(ccd_2x3: CCD, cmos_2x3: CMOS, detector_type: str):
    """Test model 'output_node_noise' with invalid input(s)."""
    if detector_type == "ccd":
        detector: CCD | CMOS = ccd_2x3
    elif detector_type == "cmos":
        detector = cmos_2x3
    else:
        raise NotImplementedError

    with pytest.raises(ValueError, match="'std_deviation' must be positive."):
        output_node_noise(detector=detector, std_deviation=-1.0)


def test_output_node_noise_cmos(cmos_2x3: CMOS):
    """Test model 'output_node_noise_cmos' with valid inputs."""
    seed = 12345
    rng = np.random.default_rng(seed=seed)

    detector = cmos_2x3
    detector.signal.array = rng.random(size=(2, 3), dtype=float)

    output_node_noise_cmos(
        detector=detector,
        readout_noise=1.0,
        readout_noise_std=0.1,
        seed=seed,
    )

    new_signal = detector.signal.array

    exp_signal = np.array(
        [[0.228246, 0.319711, 0.804656], [0.688026, 0.403161, 0.318046]]
    )
    np.testing.assert_allclose(actual=new_signal, desired=exp_signal, rtol=1e-5)


@pytest.fixture
def cmos_2x3_with_channels():
    """Fixture to create a CMOS detector with different gains for each channel."""
    cmos = CMOS(
        geometry=CMOSGeometry(
            row=2,
            col=3,
            channels=Channels(
                matrix=Matrix([["OP1", "OP2", "OP3"], ["OP4", "OP5", "OP6"]]),
                readout_position=ReadoutPosition(
                    {
                        "OP1": "top-left",
                        "OP2": "top-right",
                        "OP3": "top-right",
                        "OP4": "bottom-left",
                        "OP5": "bottom-left",
                        "OP6": "bottom-right",
                    }
                ),
            ),
        ),
        characteristics=Characteristics(
            charge_to_volt_conversion={
                "OP1": 1.0,
                "OP2": 1.5,
                "OP3": 2.0,
                "OP4": 2.5,
                "OP5": 3.0,
                "OP6": 3.5,
            }
        ),
        environment=Environment(),
    )
    cmos.signal.array = np.zeros(cmos.geometry.shape, dtype=float)
    return cmos


def test_output_node_noise_cmos_with_channels(cmos_2x3_with_channels: CMOS):
    """Test model 'output_node_noise_cmos' with channel-specific conversions."""
    seed = 12345

    detector = cmos_2x3_with_channels
    # Create a test pattern based on channel-specific gains:
    test_pattern = np.array([[1, 1, 1], [1, 1, 1]])
    # Apply gains to the initial test pattern:
    for channel, gain in detector.characteristics.charge_to_volt_conversion.items():
        slice_y, slice_x = detector.geometry.get_channel_coord(channel)
        # Apply gain to specific pixels based on the channel coordinates
        detector.signal.array[slice_y, slice_x] = test_pattern[slice_y, slice_x] * gain

    output_node_noise_cmos(
        detector=detector,
        readout_noise=1.0,
        readout_noise_std=0.1,
        seed=seed,
    )

    new_signal = detector.signal.array

    exp_signal = np.array(
        [[1.09100598, 1.9428603, 3.45815312], [5.44291645, 6.61554205, -1.6689306]]
    )
    np.testing.assert_allclose(actual=new_signal, desired=exp_signal, rtol=1e-5)


def test_output_node_noise_with_ccd(ccd_2x3: CCD):
    """Test model 'output_node_noise_ccd' with a 'CCD'."""
    detector = ccd_2x3

    with pytest.raises(TypeError, match="Expecting a 'CMOS' detector object."):
        output_node_noise_cmos(
            detector=detector,
            readout_noise=1.0,
            readout_noise_std=2.0,
        )


def test_output_node_noise_readout_noise_low_charge_to_volt():
    """Test model 'output_node_noise_ccd' with low charge to volt conversion."""
    detector = CMOS(
        geometry=CMOSGeometry(
            row=100,
            col=100,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
            pixel_scale=0.01,
        ),
        environment=Environment(),
        characteristics=Characteristics(
            charge_to_volt_conversion=1e-6,  # This value is used in 'output_node_noise_cmos'
        ),
    )
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)

    # Add output node noise
    output_node_noise_cmos(
        detector,
        readout_noise=10.0,
        readout_noise_std=5,
        seed=12345,
    )


def test_output_node_noise_invalid_noise(cmos_2x3: CMOS):
    """Test model 'output_node_noise_ccd' with a 'CCD'."""
    detector = cmos_2x3

    with pytest.raises(ValueError, match="'readout_noise_std' must be positive."):
        output_node_noise_cmos(
            detector=detector,
            readout_noise=1.0,
            readout_noise_std=-1.0,
        )


def test_readout_noise_saphira_with_ccd(ccd_2x3: CCD):
    """Test model 'readout_noise_saphira' with a 'CCD'."""
    detector = ccd_2x3

    with pytest.raises(TypeError, match="Expecting a 'APD' detector object."):
        readout_noise_saphira(
            detector=detector,
            roic_readout_noise=0.1,
            controller_noise=0.1,
        )


def test_readout_noise_saphira(apd_2x3: APD):
    """Test model 'readout_noise_saphira' with valid inputs."""
    detector = apd_2x3

    readout_noise_saphira(
        detector=detector,
        roic_readout_noise=0.1,
        controller_noise=0.1,
    )

def test_fixed_readout_noise(cmos_2x3: CMOS):
    """Test 'fixed_readout_noise' with a 2x3 'CMOS' and a valid noise file"""

    filename = "test_fixed_readout_noise.txt"
    seed = 12345
    rng = np.random.default_rng(seed=seed)

    # set detector signal array with predictable values
    detector = cmos_2x3
    detector.signal.array = rng.random(size=(2, 3), dtype=float)

    # define the fixed noise array to see if it applies correctly
    noise = np.array([
        0.00011344897101509484,
        -0.00019597840677601492,
        -3.055019262471055e-05,
        0.0003243648264931221,
        8.574005489058888e-05,
        0.00023433405048968554
    ])
    noise.tofile(filename, sep=",") # and kick it to a file

    # This is the predictable signal array modified by the noise array that we would expect
    exp_signal = np.array([
        [0.22744947143818475, 0.3165623613029769, 0.7973349071401095],
        [0.6765790355774677, 0.3911952906567996, 0.3330482619168742],
    ])

    # Test func
    fixed_readout_noise(
        detector=detector,
        filename=filename
    )
    new_signal = detector.signal.array # retireve result

    os.remove(filename) # delete the temporary noise file

    np.testing.assert_allclose(actual=new_signal, desired=exp_signal, rtol=1e-5)

def test_fixed_readout_noise_invalid_file(cmos_2x3: CMOS):
    """Test 'fixed_readout_noise' with a 2x3 'CMOS' and an invalid noise file"""

    filename = "test_fixed_readout_noise.txt"
    seed = 12345
    rng = np.random.default_rng(seed=seed)

    # set detector signal array with predictable values
    detector = cmos_2x3
    detector.signal.array = rng.random(size=(2, 3), dtype=float)

    # ensure that the file doesn't actually exist rather than just assume it doesn't
    if os.path.isfile(filename):
        os.remove(filename)

    # Test func with non-existant noise file
    with pytest.raises(FileNotFoundError, match="Fixed noise file not found."):
        fixed_readout_noise(
            detector=detector,
            filename=filename
        )

def test_fixed_readout_noise_malformed_file(cmos_2x3: CMOS):
    """Test 'fixed_readout_noise' with a 2x3 'CMOS' and a malformed/invalid noise file"""

    filename = "test_fixed_readout_noise.txt"
    seed = 12345
    rng = np.random.default_rng(seed=seed)

    # set detector signal array with predictable values
    detector = cmos_2x3
    detector.signal.array = rng.random(size=(2, 3), dtype=float)

    # define the fixed noise array to see if it applies correctly
    noise = np.array([
        0.00011344897101509484,
        -0.00019597840677601492,
        -3.055019262471055e-05,
        0.0003243648264931221,
        8.574005489058888e-05,
        0.00023433405048968554
    ])
    noise.tofile(filename, sep="/") # and kick it to a file using the incorrect separator

    # This is the predictable signal array modified by the noise array that we would expect
    exp_signal = np.array([
        [0.22744947143818475, 0.3165623613029769, 0.7973349071401095],
        [0.6765790355774677, 0.3911952906567996, 0.3330482619168742],
    ])

    # Test func
    with pytest.raises(ValueError, match="Noise file is incorrect format. Use single-line C-style comma-separated floats."):
        fixed_readout_noise(
            detector=detector,
            filename=filename
        )

    os.remove(filename)