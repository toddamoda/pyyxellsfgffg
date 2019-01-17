#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Charge readout model."""
import logging
# import pyxel
from pyxel.detectors.detector import Detector
# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def simple_amplifier(detector: Detector):
    """Amplify signal.

    amp - Gain of output amplifier
    a1 - Gain of the signal processor
    detector Signal unit: Volt

    :param detector: Pyxel Detector object
    """
    logging.info('')
    char = detector.characteristics
    detector.signal.array *= char.amp * char.a1
