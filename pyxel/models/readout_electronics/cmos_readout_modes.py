#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Non-Destructive Readout modes for CMOS-based detectors."""
import logging
import pyxel
from pyxel.detectors.cmos import CMOS
from pyxel import check_choices


@pyxel.validate
@pyxel.argument(name='mode', label='', units='',
                validate=check_choices(['uncorrelated', 'CDS', 'Fowler-N', 'UTR']))
def non_destructive_readout(detector: CMOS,
                            mode: str,
                            fowler_samples: int = 1):
    """Non-Destructive Readout modes for CMOS-based detectors.

    :param detector: Pyxel Detector object
    :param mode:
    :param fowler_samples:
    """
    logger = logging.getLogger('pyxel')
    logger.info('')
    if not detector.is_non_destructive_readout or not detector.is_dynamic:
        raise ValueError()

    detector.read_out = False
    if mode == 'uncorrelated':
        if detector.time == detector.end_time:
            detector.read_out = True
    elif mode == 'CDS':
        if detector.time == detector.start_time + detector.last_time_step or detector.time == detector.end_time:
            detector.read_out = True
    elif mode == 'Fowler-N':
        nt = fowler_samples * detector.last_time_step
        detector.read_out = True
        if detector.start_time + nt < detector.time <= detector.end_time - nt:
            detector.read_out = False
    elif mode == 'UTR':
        detector.read_out = True
