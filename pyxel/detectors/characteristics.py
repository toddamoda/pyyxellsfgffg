"""TBW."""
import pyxel as pyx


@pyx.detector_class
class Characteristics:
    """Characteristical attributes of the detector."""

    qe = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='Quantum efficiency',
        metadata={'units': ''}
    )
    eta = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='Quantum yield',
        metadata={'units': 'e-/photon'}
    )
    sv = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='Sensitivity of CCD amplifier',
        metadata={'units': 'V/e-'}
    )
    amp = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='Output amplifier gain',
        metadata={'units': 'V/V'}
    )
    a1 = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='Gain of the signal processor',
        metadata={'units': 'V/V'}
    )
    a2 = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 65536)],
        doc='Gain of the Analog-Digital Converter',
        metadata={'units': 'ADU/V'}
    )
    fwc = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0., 1.e+7)],
        doc='Full well capacity',
        metadata={'units': 'e-'}
    )
    vg = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='Half pixel volume charges can occupy',      # TODO should be the full volume and not the half
        metadata={'units': 'cm^2'}
    )
    dt = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        doc='Pixel dwell time',
        metadata={'units': 's'}
    )
