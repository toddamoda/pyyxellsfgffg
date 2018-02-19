"""TBW."""

from pyxel.detectors.characteristics import Characteristics


class CCDCharacteristics(Characteristics):
    """TBW."""

    def __init__(self,
                 fwc_serial: int = None,
                 **kwargs) -> None:
        """TBW.

        :param fwc_serial:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.fwc_serial = fwc_serial   # * u.electrons

    def __getstate__(self):
        """TBW.

        :return:
        """
        states = super().__getstate__()
        ccd_states = {
            'fwc_serial': self.fwc_serial,
        }
        return {**states, **ccd_states}
