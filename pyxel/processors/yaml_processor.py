import astropy.units as u
import yaml

from pyxel.detectors.ccd import CCDDetector


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

    def __init__(self, ccd: CCD, doc=None):
        self.ccd = ccd
        self.doc = doc


class PipelineYAML(yaml.SafeLoader):
    pass


def _constructor_ccd_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node)      # type: dict

    obj = DetectionPipeline(**mapping)

    return obj


def _constructor_ccd(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    signal = mapping.get('signal', None)
    charge = mapping.get('charge', None)

    obj = CCD(photons=photons,
              signal=signal,
              charge=charge,
              geometry=geometry,
              environment=environment,
              characteristics=characteristics)

    return obj


PipelineYAML.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PipelineYAML.add_constructor('!CCD', _constructor_ccd)

#
# def run_pipeline(obj):
#     ccd_params = obj.ccd
#
#     # Create the CCD object
#     ccd = CCD(dict(obj.ccd))
#
#     # Start the CCD pipeline
#
#     # Apply Optics Model (if necessary)
#     if obj.optics:
#         for cfg_optics in obj.optics.item():
#             assert isinstance(cfg_optics, OPTICS_MODEL)
#
#             params = cfg_optics.params  # type: dict
#             func = cfg_optcs.func  # type: callable
#
#             ccd.p = func(photons=self.ccd.p, **params)
#             # ccd.p = cfg_optics.apply(photons=self.ccd.p, **params)
#
#     # Apply Charge Generation Model (if necessary)
#     params = obj.charge_generation
#     qe = params['qe']
#     eta = params['eta']
#
#     # calculate charges per pixel
#     ccd.compute_charge(**params)
#
#     if obj.charge_generation.extra_models:


# FIXED PATTERN NOISE
# if self.model.fix_pattern_noise:
#     self.ccd.charge = self.model.add_fix_pattern_noise(self.ccd.charge, self.model.noise_file)


def load_config(yaml_file):

    with open(yaml_file, 'r') as file_obj:
        cfg = yaml.load(file_obj, Loader=PipelineYAML)

    return cfg


def main():
    # Get the pipeline configuration
    cfg = load_config(r'settings.yaml')     # type: DetectionPipeline

    # # Create the CCD object
    # params = {'photons': cfg.ccd.photons,
    #           'signal': cfg.ccd.signal,
    #           'charge': cfg.ccd.charge,
    #           **vars(cfg.ccd.geometry),
    #           **vars(cfg.ccd.environment),
    #           **vars(cfg.ccd.characteristics)}
    #
    # ccd = CCDDetector(**params)

    ccd = CCDDetector.from_ccd(cfg.ccd)     # type: CCDDetector
    pass


if __name__ == '__main__':
    main()