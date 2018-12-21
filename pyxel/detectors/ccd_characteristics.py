"""TBW."""
import pyxel as pyx
from pyxel.detectors.characteristics import Characteristics


@pyx.detector_class
class CCDCharacteristics(Characteristics):
    """TBW."""

    fwc_serial = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0., 1.e+7)],          # TODO test this
        doc='full well capacity (serial)',
        metadata={'units': 'electrons'}
    )
    svg = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='half pixel volume charges can occupy (serial)',
        metadata={'units': 'cm^2'}
    )
    t = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        doc='parallel transfer period',
        metadata={'units': 's'}
    )
    st = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        doc='serial transfer period',
        metadata={'units': 's'}
    )
