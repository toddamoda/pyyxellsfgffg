#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import numpy as np
from astropy.units import Quantity

from pyxel.detectors import (
    CMOS,
    Channels,
    Characteristics,
    ChargeToVoltSettings,
    CMOSGeometry,
    Environment,
    Matrix,
    ReadoutPosition,
)
from pyxel.models.charge_measurement.uncorrelated_pink_noise_cmos import (
    create_pink_noise_cmos,
    create_uncorrelated_pink_noise_cmos_by_chan,
    uncorrelated_pink_noise_cmos,
)
from pyxel.util import PinkNoiseGenerator


def test_create_pink_noise_cmos():
    # first test
    nb_pixels_overhead_after_row = 4
    nb_rows_overhead_after_frame = 1
    generator = PinkNoiseGenerator()
    shape = (8, 4)
    std = Quantity(1, unit="electron")
    c = create_pink_noise_cmos(
        nb_pixels_overhead_after_row,
        nb_rows_overhead_after_frame,
        generator,
        shape,
        std,
    )
    assert isinstance(c, np.ndarray)
    assert c.shape == (8, 4)
    assert c.unit == "electron"


def test_create_uncorrelated_pink_noise_cmos_by_chan():
    channels = Channels(
        matrix=Matrix([["OP9", "OP13"], ["OP1", "OP5"]]),
        readout_position=ReadoutPosition(
            {
                "OP9": "top-left",
                "OP13": "top-left",
                "OP1": "bottom-left",
                "OP5": "bottom-left",
            }
        ),
    )
    nb_pixels_overhead_after_row = 4
    nb_rows_overhead_after_frame = 1
    generator_by_chan = dict(
        [
            ("OP9", PinkNoiseGenerator()),
            ("OP13", PinkNoiseGenerator()),
            ("OP1", PinkNoiseGenerator()),
            ("OP5", PinkNoiseGenerator()),
        ]
    )
    detector_shape = (8, 4)
    std_by_chan = dict(
        [
            ("OP9", Quantity(1, unit="electron")),
            ("OP13", Quantity(1, unit="electron")),
            ("OP1", Quantity(1, unit="electron")),
            ("OP5", Quantity(1, unit="electron")),
        ]
    )
    c = create_uncorrelated_pink_noise_cmos_by_chan(
        channels,
        nb_pixels_overhead_after_row,
        nb_rows_overhead_after_frame,
        generator_by_chan,
        detector_shape,
        std_by_chan,
    )
    assert isinstance(c, np.ndarray)
    assert c.shape == (8, 4)
    assert c.unit == "electron"
    # check different pink noise for each channel
    slop9 = channels.get_channel_slices(detector_shape, "OP9")
    slop1 = channels.get_channel_slices(detector_shape, "OP1")
    slop5 = channels.get_channel_slices(detector_shape, "OP5")
    slop13 = channels.get_channel_slices(detector_shape, "OP13")
    assert np.all(c[slop9] != c[slop1])
    assert np.all(c[slop9] != c[slop13])
    assert np.all(c[slop9] != c[slop5])
    assert np.all(c[slop1] != c[slop13])
    assert np.all(c[slop1] != c[slop5])
    assert np.all(c[slop5] != c[slop13])


def test_uncorrelated_pink_noise_cmos():
    cmos = CMOS(
        geometry=CMOSGeometry(
            row=100,
            col=120,
            total_thickness=123.1,
            pixel_horz_size=12.4,
            pixel_vert_size=34.5,
            pixel_scale=1.5,
            channels=Channels(
                matrix=Matrix([["OP9", "OP13"], ["OP1", "OP5"]]),
                readout_position=ReadoutPosition(
                    {
                        "OP9": "top-left",
                        "OP13": "top-left",
                        "OP1": "bottom-left",
                        "OP5": "bottom-left",
                    }
                ),
            ),
        ),
        environment=Environment(temperature=100.1),
        characteristics=Characteristics(
            quantum_efficiency=0.1,
            charge_to_volt=ChargeToVoltSettings(value=0.2),
            pre_amplification=3.3,
            full_well_capacity=4.4,
            adc_bit_resolution=16,
            adc_voltage_range=(0.0, 10.0),
        ),
    )
    nb_pixels_overhead_after_row = 4
    nb_rows_overhead_after_frame = 1
    std = 1
    seed = 1234
    uncorrelated_pink_noise_cmos(
        cmos, nb_pixels_overhead_after_row, nb_rows_overhead_after_frame, std, seed
    )
    c = cmos.pixel.volatile.array
    assert np.sum(c) > 0
    # check different pink noise for each channel
    slop9 = cmos.geometry.channels.get_channel_slices(cmos.geometry.shape, "OP9")
    slop1 = cmos.geometry.channels.get_channel_slices(cmos.geometry.shape, "OP1")
    slop5 = cmos.geometry.channels.get_channel_slices(cmos.geometry.shape, "OP5")
    slop13 = cmos.geometry.channels.get_channel_slices(cmos.geometry.shape, "OP13")
    assert np.all(c[slop9] != c[slop1])
    assert np.all(c[slop9] != c[slop13])
    assert np.all(c[slop9] != c[slop5])
    assert np.all(c[slop1] != c[slop13])
    assert np.all(c[slop1] != c[slop5])
    assert np.all(c[slop5] != c[slop13])
