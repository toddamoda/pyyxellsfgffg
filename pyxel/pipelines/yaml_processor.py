import functools
import typing as t

from pathlib import Path

import numpy as np
import yaml

from pyxel.pipelines import config
from pyxel.pipelines.config import CCDCharacteristics, Environment, Geometry, CCD, DetectionPipeline
from pyxel.util import util

from pyxel.pipelines import ccd_pipeline


class PipelineYAML(yaml.SafeLoader):
    pass


def _constructor_ccd_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

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
    config_path = Path(__file__).parent.parent.joinpath('settings.yaml')
    # cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # cfg = load_config(os.path.join(cwd, 'settings.yaml'))     # type: DetectionPipeline
    cfg = load_config(str(config_path))
    result = ccd_pipeline.run_pipeline(cfg)
    return result

if __name__ == '__main__':
    main()