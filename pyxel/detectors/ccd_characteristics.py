"""TBW."""
import esapy_config as om

from pyxel.detectors.characteristics import Characteristics


@om.attr_class
class CCDCharacteristics(Characteristics):
    """TBW."""

    fwc_serial = om.attr_def(
        type=int,
        default=0.0,
        converter=int,
        validator=om.validate_range(0, 1000000, 1, False),
        doc='full well capacity (serial)',
        metadata={'units': 'electrons'}
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
        }
        return {**states, **ccd_states}
