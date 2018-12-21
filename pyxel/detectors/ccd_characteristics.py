"""TBW."""
import pyxel
import esapy_config as om

from pyxel.detectors.characteristics import Characteristics


@pyxel.detector_class
class CCDCharacteristics(Characteristics):
    """TBW."""

    fwc_serial = om.attr_def(
        type=float,
        default=0,
        converter=float,
        validator=om.validate_range(0., 1.e+7, 1., False),
        doc='full well capacity (serial)',
        metadata={'units': 'electrons'}
    )
    svg = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0., 1., 1.e-8, False),
        doc='half pixel volume charges can occupy (serial)',
        metadata={'units': 'cm^2'}
    )
    t = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0., 10., 1.e-9, False),
        doc='parallel transfer period',
        metadata={'units': 's'}
    )
    st = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0., 10., 1.e-9, False),
        doc='serial transfer period',
        metadata={'units': 's'}
    )
