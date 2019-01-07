"""TBW."""
import pyxel as pyx


@pyx.detector_class
class Characteristics:
    """TBW."""

    qe = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='quantum efficiency',
        metadata={'units': ''}
    )

    eta = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='quantum yield',
        metadata={'units': 'e-/photon'}
    )

    sv = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='sensitivity of CCD amplifier',
        metadata={'units': 'V/e-'}
    )

    amp = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='output amplifier gain',
        metadata={'units': 'V/V'}
    )

    a1 = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        doc='gain of the signal processor',
        metadata={'units': 'V/V'}
    )

    a2 = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 65536)],
        doc='gain of the ADC',
        metadata={'units': 'ADU/V'}
    )

    fwc = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0., 1.e+7)],
        doc='full well capacity',
        metadata={'units': 'e-'}
    )

    vg = pyx.attribute(
        type=float,
        default=0.,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.)],
        doc='half pixel volume charges can occupy',
        metadata={'units': 'cm^2'}
    )
