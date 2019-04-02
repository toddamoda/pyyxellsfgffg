"""TBW."""
import pyxel as pyx
from pyxel.detectors.characteristics import Characteristics


@pyx.detector_class
class CMOSCharacteristics(Characteristics):
    """Characteristical attributes of a CMOS-based detector."""

    cutoff = pyx.attribute(
        type = float,
        default = 2.5,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(1.7, 15)],
        doc = 'Cutoff wavelength',
        metadata = {'units': 'um'}
    )

    vbiaspower = pyx.attribute(
        type = float,
        default = 3.350,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(0.0, 3.4)],
        doc = 'VBIASPOWER',
        metadata = {'units': 'V'}
    )

    dsub = pyx.attribute(
        type = float,
        default = 0.500,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(0.3, 1.0)],
        doc = 'DSUB',
        metadata = {'units': 'V'}
    )

    vreset = pyx.attribute(
        type = float,
        default = 0.250,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(0.0, 0.3)],
        doc = 'VRESET',
        metadata = {'units': 'V'}
    )

    biasgate = pyx.attribute(
        type = float,
        default = 2.300,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(1.8, 2.6)],
        doc = 'BIASGATE',
        metadata = {'units': 'V'}
    )

    preampref = pyx.attribute(
        type = float,
        default = 1.700,
        converter = float,
        validator = [pyx.validate_type(float),
                   pyx.validate_range(0.0, 4.0)],
        doc = 'PREAMPREF',
        metadata = {'units': 'V'}
    )