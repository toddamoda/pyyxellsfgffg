

class CCDCharacteristics:

    def __init__(self,
                 qe: float = None,
                 eta: float = None,
                 sv: float = None,
                 accd: float = None,
                 a1: float = None,
                 a2: float = None) -> None:
        """
        :param qe:
        :param eta:
        :param sv:
        :param accd:
        :param a1:
        :param a2:
        """

        self.qe = qe        # quantum efficiency
        self.eta = eta      # * u.electron / u.ph       # quantum yield
        self.sv = sv        # * u.V / u.electron        # sensitivity of CCD amplifier [V/-e]
        self.accd = accd    # * u.V / u.V               # output amplifier gain
        self.a1 = a1        # * u.V / u.V               # gain of the signal processor
        self.a2 = a2        # * u.adu / u.V             # gain of the ADC

    def __getstate__(self):
        return {'qe': self.qe,
                'eta': self.eta,
                'sv': self.sv,
                'accd': self.accd,
                'a1': self.a1,
                'a2': self.a2}

    # TODO: create unittests for this method
    def __eq__(self, obj):
        assert isinstance(obj, CCDCharacteristics)
        return self.__getstate__() == obj.__getstate__()
