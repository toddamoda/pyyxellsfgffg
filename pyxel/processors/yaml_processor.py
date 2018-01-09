import yaml

from pyxel.detectors.ccd import CCDDetector
from pyxel.processors.config import CCDCharacteristics, Environment, Geometry, CCD, DetectionPipeline


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

    # Create the CCD object
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