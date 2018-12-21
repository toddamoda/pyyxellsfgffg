"""TBW."""
import pyxel
import esapy_config as om


@pyxel.detector_class
class Characteristics:
    """TBW."""

    qe = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='quantum efficiency'
    )

    eta = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='quantum yield'
    )

    sv = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='sensitivity of CCD amplifier',
        metadata={'units': 'V/-e'}
    )

    amp = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='output amplifier gain',
    )

    a1 = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 1.0, False),
        doc='gain of the signal processor',
    )

    a2 = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 65536.0, 1.0, False),
        doc='gain of the ADC',
    )

    fwc = om.attr_def(
        type=float,
        default=0,
        converter=float,
        validator=om.validate_range(0., 1.e+7, 1., False),
        doc='full well capacity',
        metadata={'units': 'electrons'}
    )

    vg = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0., 1., 1.e-8, False),
        doc='half pixel volume charges can occupy',
        metadata={'units': 'cm^2'}
    )
