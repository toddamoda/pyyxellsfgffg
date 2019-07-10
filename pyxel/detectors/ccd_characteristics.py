"""TBW."""
from pyxel.detectors.characteristics import Characteristics
from ..util import config, validators


@config.detector_class
class CCDCharacteristics(Characteristics):
    """Characteristical attributes of a CCD detector."""

    fwc_serial = config.attribute(
        type=int,
        default=0,
        validator=[validators.validate_type(int),
                   validators.validate_range(0., 1.e+7)],          # TODO test this
        doc='Full well capacity (serial register)',
        metadata={'units': 'electrons'}
    )
    svg = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 1.)],
        doc='Half pixel volume charge can occupy (serial register)',  # TODO should be the full volume and not the half
        metadata={'units': 'cm^2'}
    )
    t = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 10.)],
        doc='Parallel transfer period',
        metadata={'units': 's'}
    )
    st = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 10.)],
        doc='Serial transfer period',
        metadata={'units': 's'}
    )
