# Copyright or © or Copr. Antoine Kaszczyc and Aurelien Jarno, Centre de Recherche Astrophysique de Lyon (CRAL)  (2025)
#
# Antoine Kaszczyc <antoine.kaszczyc@univ-lyon1.fr>
#
# This file is part of the Pyxel general simulator framework.
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import numpy as np
from astropy.units import Quantity

import pyxel
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
from pyxel.util import PinkNoiseGenerator, set_random_seed


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


def test_exposure_uncorrelated_pink_noise_cmos():
    s = """
exposure:
  readout:
    times: [1,2,3]
    non_destructive:  true
cmos_detector:
  geometry:
    row: 4 # [px]
    col: 4 # [px]
  characteristics:
    charge_to_volt_conversion: 1.0e-6 # [V/e]
    adc_voltage_range: [0,6] # [V,V]
    adc_bit_resolution: 16   # [bit]
    quantum_efficiency: 1
pipeline:
  photon_collection:
    - name: illumination
      func: pyxel.models.photon_collection.illumination
      arguments:
        level: 0
  charge_generation:
    - name: simple_conversion
      func: pyxel.models.charge_generation.simple_conversion
  charge_collection:
    - name: simple_collection
      func: pyxel.models.charge_collection.simple_collection
  charge_measurement:
    - name: uncorrelated_pink_noise_cmos
      func: pyxel.models.charge_measurement.uncorrelated_pink_noise_cmos
      arguments:
        nb_pixels_overhead_after_row: 0
        nb_rows_overhead_after_frame: 0
        seed: 1234
"""
    config = pyxel.loads(s)
    result = pyxel.run_mode(config)
    configseed = (
        config.pipeline.charge_measurement.uncorrelated_pink_noise_cmos.arguments.seed
    )
    configrow = config.detector.geometry.row
    configcol = config.detector.geometry.col
    configtimes = config.exposure.readout.times
    with set_random_seed(configseed):
        sd = np.random.randint(10_000)
        refgen = PinkNoiseGenerator(sd)
        lennoise = configrow * configcol * len(configtimes)
        refnoise = refgen.get(lennoise)
        # test that the 3 samples combined is equal to the noise sequence
        assert np.all(np.ravel(result.bucket.pixel.data) == refnoise)
