"""Readout electronics model."""
import logging
from pyxel.detectors.detector import Detector
# from astropy import units as u


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def simple_amplifier(detector: Detector):
    """Amplify signal.

    amp - Gain of output amplifier, a1 - Gain of the signal processor

    :param detector: Pyxel Detector object
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    char = detector.characteristics
    detector.signal.array *= char.amp * char.a1
