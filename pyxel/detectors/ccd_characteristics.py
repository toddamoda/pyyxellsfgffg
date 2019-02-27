"""TBW."""
import pyxel as pyx
from pyxel.detectors.characteristics import Characteristics


@pyx.detector_class
class CCDCharacteristics(Characteristics):
    """Characteristical attributes of a CCD detector."""

    fwc_serial = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0., 1.e+7)],          # TODO test this
        doc='Full well capacity (serial register)',
        metadata={'units': 'electrons'}
    )
    svg = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='Half pixel volume charge can occupy (serial register)',  # TODO should be the full volume and not the half
        metadata={'units': 'cm^2'}
    )
    t = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        doc='Parallel transfer period',
        metadata={'units': 's'}
    )
    st = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        doc='Serial transfer period',
        metadata={'units': 's'}
    )
