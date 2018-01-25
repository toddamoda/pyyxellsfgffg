

class CCDCharacteristics:

    def __init__(self, **kwargs):
        self.k = kwargs.get('k', 0.0)   # * u.adu                   # camera gain constant in digital number (DN)
        self.j = kwargs.get('j', 0.0)   # * u.ph                    # camera gain constant in photon number
        self.qe = kwargs.get('qe', 0.0)                             # quantum efficiency
        self.eta = kwargs.get('eta', 0.0)   # * u.electron / u.ph   # quantum yield
        self.sv = kwargs.get('sv', 0.0)     # * u.V / u.electron      # sensitivity of CCD amplifier [V/-e]
        self.accd = kwargs.get('accd', 0.0)     # * u.V / u.V         # output amplifier gain
        self.a1 = kwargs.get('a1', 0)   # * u.V / u.V               # gain of the signal processor
        self.a2 = kwargs.get('a2', 0)   # * u.adu / u.V             # gain of the ADC
        self.fwc = kwargs.get('fwc', 0)     # * u.electron            # full well capacity
        # self.pix_non_uniformity = kwargs.get('pix_non_uniformity', None)  # 2d array
