from astropy import units as u


class CCDCharacteristics:

    def __init__(self, **kwargs):
        self.k = kwargs.get('k', 0.0) * u.adu        # camera gain constant in digital number (DN)
        self.j = kwargs.get('j', 0.0) * u.ph       # camera gain constant in photon number
        self.qe = kwargs.get('qe', 0.0)      # quantum efficiency
        self.eta = kwargs.get('eta', 0.0)    # quantum yield
        self.sv = kwargs.get('sv', 0.0) * u.V / u.electron      # sensitivity of CCD amplifier [V/-e]
        self.accd = kwargs.get('accd', 0.0)  # output amplifier gain
        self.a1 = kwargs.get('a1', 0)        # is the gain of the signal processor
        self.a2 = kwargs.get('a2', 0)        # gain of the ADC
        self.fwc = kwargs.get('fwc', 0) * u.electron      # full well compacity


class Environment:

    def __init__(self, temperature: float = None):
        self.temperature = temperature          # unit: K


class Geometry:

    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col


class CCD:

    def __init__(self,
                 geometry: Geometry = None,
                 environment: Environment = None,
                 characteristics: CCDCharacteristics = None,
                 photons=None, signal=None, charge=None):
        self.photons = photons      # unit: photons
        self.signal = signal        # unit: ADU
        self.charge = charge        # unit: electrons

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics


class DetectionPipeline:

    def __init__(self, ccd: CCD, optics: list, doc=None):
        self.ccd = ccd
        self.doc = doc
        self.optics = optics