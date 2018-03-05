"""TBW."""


class Characteristics:
    """TBW."""

    def __init__(self,
                 qe: float = None,
                 eta: float = None,
                 sv: float = None,
                 amp: float = None,
                 a1: float = None,
                 a2: float = None,
                 fwc: int = None,
                 ) -> None:
        """TBW.

        :param qe:
        :param eta:
        :param sv:
        :param amp:
        :param a1:
        :param a2:
        :param fwc:
        """
        self.qe = qe                            # quantum efficiency
        self.eta = eta                          # * u.electron / u.ph       # quantum yield
        self.sv = sv                            # * u.V / u.electron        # sensitivity of CCD amplifier [V/-e]
        self.amp = amp                          # * u.V / u.V               # output amplifier gain
        self.a1 = a1                            # * u.V / u.V               # gain of the signal processor
        self.a2 = a2                            # * u.adu / u.V             # gain of the ADC
        self.fwc = fwc                          # * u.electrons             # full well capacity (parallel)

    def copy(self):
        """TBW."""
        return Characteristics(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        return {'qe': self.qe,
                'eta': self.eta,
                'sv': self.sv,
                'amp': self.amp,
                'a1': self.a1,
                'a2': self.a2,
                'fwc': self.fwc}

    # TODO: create unittests for this method
    def __eq__(self, obj):
        """TBW."""
        assert isinstance(obj, Characteristics)
        return self.__getstate__() == obj.__getstate__()
