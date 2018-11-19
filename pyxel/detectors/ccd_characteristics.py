"""TBW."""
import esapy_config as om

from pyxel.detectors.characteristics import Characteristics


@om.attr_class
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

    def copy(self):
        """TBW."""
        return CCDCharacteristics(**self.__getstate__())

    def __getstate__(self):
        """TBW.

        :return:
        """
        states = super().__getstate__()
        ccd_states = {
            'fwc_serial': self.fwc_serial,
            'svg': self.svg,
            't': self.t,
            'st': self.st,
        }
        return {**states, **ccd_states}
