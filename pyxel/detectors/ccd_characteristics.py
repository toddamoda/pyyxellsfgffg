

class CCDCharacteristics:

    def __init__(self, **kwargs):
        # self.k = kwargs.get('k', 0.0)   # * u.adu                   # camera gain constant in digital number (DN)
        # self.j = kwargs.get('j', 0.0)   # * u.ph                    # camera gain constant in photon number
        self.qe = kwargs.get('qe', 0.0)                             # quantum efficiency
        self.eta = kwargs.get('eta', 0.0)   # * u.electron / u.ph   # quantum yield
        self.sv = kwargs.get('sv', 0.0)     # * u.V / u.electron      # sensitivity of CCD amplifier [V/-e]
        self.accd = kwargs.get('accd', 0.0)     # * u.V / u.V         # output amplifier gain
        self.a1 = kwargs.get('a1', 0)   # * u.V / u.V               # gain of the signal processor
        self.a2 = kwargs.get('a2', 0)   # * u.adu / u.V             # gain of the ADC

    def __getstate__(self):
        return {
            # 'k': self.k,
            # 'j': self.j,
            'qe': self.qe,
            'eta': self.eta,
            'sv': self.sv,
            'accd': self.accd,
            'a1': self.a1,
            'a2': self.a2,
        }

    # TODO: create unittests for this method
    def __eq__(self, obj):
        assert isinstance(obj, CCDCharacteristics)
        return self.__getstate__() == obj.__getstate__()
