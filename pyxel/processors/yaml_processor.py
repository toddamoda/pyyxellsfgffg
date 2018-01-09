import functools
import typing as t

import numpy as np
import yaml

from pyxel.detectors.ccd import CCDDetector
from pyxel.processors import config
from pyxel.processors.config import CCDCharacteristics, Environment, Geometry, CCD, DetectionPipeline
from pyxel.util import util


class PipelineYAML(yaml.SafeLoader):
    pass


def _constructor_ccd_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    # if 'optics' in mapping:
    #     optics = Optics(**mapping['optics'])
    # else:
    #     optics = None

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

# class Function:
#
#     def __init__(self, name, *args, **kwargs):
#         self.name = name
#         self.args = args
#         self.kwarg


def _constructor_from_file(loader: PipelineYAML, node: yaml.ScalarNode):
    noise_file = loader.construct_scalar(node)
    result = np.fromfile(noise_file, dtype=float, sep=' ')
    return result


def _constructor_models(loader: PipelineYAML, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    return config.Models(mapping)


def _constructor_function(loader: PipelineYAML, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    function_name = mapping['name']                      # type: str
    kwargs = mapping.get('kwargs', {})

    func = util.evaluate_reference(function_name)        # type: t.Callable
    return functools.partial(func, **kwargs)


PipelineYAML.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PipelineYAML.add_constructor('!CCD', _constructor_ccd)
PipelineYAML.add_constructor('!from_file', _constructor_from_file)
PipelineYAML.add_constructor('!function', _constructor_function)
PipelineYAML.add_constructor('!models', _constructor_models)


def load_config(yaml_file):

    with open(yaml_file, 'r') as file_obj:
        cfg = yaml.load(file_obj, Loader=PipelineYAML)

    return cfg


def main():
    # Get the pipeline configuration
    cfg = load_config(r'settings.yaml')     # type: DetectionPipeline
    ccd = CCDDetector.from_ccd(cfg.ccd)     # type: CCDDetector

    steps = ['shot_noise', 'ray_tracing', 'diffraction']
    for step in steps:
        func = cfg.optics.models.get(step)
        if func:
            ccd = func(ccd)

    # calculate charges per pixel
    ccd.compute_charge()

    steps = ['fixed_pattern_noise', 'tars', 'xray', 'snowballs', 'darkcurrent', 'hotpixel']
    for step in steps:
        func = cfg.charge_generation.models.get(step)
        if func:
            ccd = func(ccd)

    # limiting charges per pixel due to Full Well Capacity
    ccd.charge_excess()

    # Signal with shot and fix pattern noise
    ccd.compute_signal()

    steps = ['readout_noise']
    for step in steps:
        func = cfg.charge_readout.models.get(step)
        if func:
            ccd = func(ccd)

    return ccd


if __name__ == '__main__':
    main()