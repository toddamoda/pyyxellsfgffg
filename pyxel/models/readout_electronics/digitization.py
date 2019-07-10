#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Readout electronics model."""
import logging
from pydoc import locate

import numpy as np

from pyxel.detectors.detector import Detector
# from astropy import units as u
from ...util import config, checkers, validators


@validators.validate
@config.argument(name='data_type', label='type of output data array', units='ADU',
                 validate=checkers.check_choices(['numpy.uint16', 'numpy.uint32', 'numpy.uint64',
                                                  'numpy.int32', 'numpy.int64']))
def simple_digitization(detector: Detector,
                        data_type: str = 'numpy.uint16'):
    """Digitize signal array mimicking readout electronics.

    :param detector: Pyxel Detector object
    :param data_type: numpy integer type: ``numpy.uint16``, ``numpy.uint32``, ``numpy.uint64``,
                                          ``numpy.int32``, ``numpy.int64``
    """
    logger = logging.getLogger('pyxel')
    logger.info('')

    d_type = locate(data_type)
    if d_type is None:
        raise TypeError('Can not locate the type defined as `data_type` argument in yaml file.')
    # Gain of the Analog-Digital Converter
    detector.signal.array *= detector.characteristics.a2
    # floor of signal values element-wise (quantization)
    detector.signal.array = np.floor(detector.signal.array)
    # convert floats to other datatype (e.g. 16-bit unsigned integers)
    detector.signal.array = np.clip(detector.signal.array, a_min=np.iinfo(d_type).min, a_max=np.iinfo(d_type).max)
    detector.image.array = detector.signal.array.astype(d_type)


def simple_processing(detector: Detector):
    """Create an image array from signal array.

    :param detector: Pyxel Detector object
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    detector.signal.array *= detector.characteristics.a2
    detector.image.array = detector.signal.array


def sar_adc(detector: Detector,
            adc_bits: int = 16,
            range_volt: tuple = (0, 5)):
    """Digitize signal array using SAR ADC logic.

    :param detector: Pyxel Detector object
    :param adc_bits: integer: Number of bits for the ADC
    :param range_volt: tuple with min anx max volt value
    """
    # import numpy as np
    logger = logging.getLogger('pyxel')
    logger.info('')
    # Extract the data to digitize
    data = detector.signal.array
    data_digitized = np.zeros((detector.geometry.row, detector.geometry.col))
    # First normalize the data to voltage since there is no model for
    # the conversion photogenerated carrier > volts in the model/charge_measure
    data = data*range_volt[1]/np.max(data)
    # steps = list()
    # Set the reference voltage of the ADC to half the max
    ref = range_volt[1]/2.
    # For each bits, compare the value of the ref to the capacitance value
    for i in np.arange(0, adc_bits):
        # digital value associated with this step
        digital_value = 2**(adc_bits-(i+1))
        # All data that is higher than the ref is equal to the dig. value
        data_digitized[data >= ref] += digital_value
        # Subtract ref value from the data
        data[data >= ref] -= ref
        # steps.append(ref)
        # Divide reference voltage by 2 for next step
        ref /= 2.

    detector.image.array = data_digitized
    # return data_digitized, steps
