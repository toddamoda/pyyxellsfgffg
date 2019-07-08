"""TBW."""
from ..util import config, validators


@config.detector_class
class Characteristics:
    """Characteristical attributes of the detector."""

    qe = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 1.)],
        doc='Quantum efficiency',
        metadata={'units': ''}
    )
    eta = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 1.)],
        doc='Quantum yield',
        metadata={'units': 'e-/photon'}
    )
    sv = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 100.)],
        doc='Sensitivity of charge readout',
        metadata={'units': 'V/e-'}
    )
    amp = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 100.)],
        doc='Gain of output amplifier',
        metadata={'units': 'V/V'}
    )
    a1 = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 100.)],
        doc='Gain of the signal processor',
        metadata={'units': 'V/V'}
    )
    a2 = config.attribute(
        type=int,
        default=0,
        validator=[validators.validate_type(int),
                   validators.validate_range(0, 65536)],
        doc='Gain of the Analog-Digital Converter',
        metadata={'units': 'ADU/V'}
    )
    fwc = config.attribute(
        type=int,
        default=0,
        validator=[validators.validate_type(int),
                   validators.validate_range(0., 1.e+7)],
        doc='Full well capacity',
        metadata={'units': 'e-'}
    )
    vg = config.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 1.)],
        doc='Half pixel volume charge can occupy',      # TODO should be the full volume and not the half
        metadata={'units': 'cm^2'}
    )
    dt = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0., 10.)],
        doc='Pixel dwell time',
        metadata={'units': 's'}
    )
