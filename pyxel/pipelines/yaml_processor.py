import functools
from pathlib import Path

import numpy as np
import yaml

import pyxel.detectors.ccd_characteristics
import pyxel.detectors.geometry
import pyxel.detectors.environment
from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.pipelines import detection_pipeline
from pyxel.util import fitsfile
from pyxel.util import util


class PipelineYAML(yaml.SafeLoader):
    pass


def _constructor_processor(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.Processor(**mapping)

    return obj


def _constructor_ccd_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CCDDetectionPipeline(**mapping)

    return obj


def _constructor_cmos_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = detection_pipeline.CMOSDetectionPipeline(**mapping)

    return obj


def _constructor_ccd(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = pyxel.detectors.geometry.Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = pyxel.detectors.environment.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = pyxel.detectors.ccd_characteristics.CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    image = mapping.get('image', None)

    obj = CCD(photons=photons,
              image=image,
              geometry=geometry,
              environment=environment,
              characteristics=characteristics)

    return obj


def _constructor_cmos(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = pyxel.detectors.geometry.Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = pyxel.detectors.environment.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = pyxel.detectors.ccd_characteristics.CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    image = mapping.get('image', None)

    obj = CMOS(photons=photons,
               image=image,
               geometry=geometry,
               environment=environment,
               characteristics=characteristics)

    return obj


def _constructor_from_file(loader: PipelineYAML, node: yaml.ScalarNode):
    filename = Path(loader.construct_scalar(node))
    if filename.suffix.lower().startswith('.fit'):
        result = fitsfile.FitsFile(str(filename)).data
    else:
        result = np.fromfile(str(filename), dtype=float, sep=' ')
    return result


def _constructor_models(loader: PipelineYAML, node: yaml.ScalarNode):

    if isinstance(node, yaml.ScalarNode):
        # OK: no kwargs provided
        mapping = {}  # type: dict
    else:
        mapping = loader.construct_mapping(node, deep=True)

    return detection_pipeline.Models(mapping)


def _constructor_function(loader: PipelineYAML, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    function_name = mapping['name']                      # type: str
    kwargs = mapping.get('kwargs', {})
    args = mapping.get('args', {})

    func = util.evaluate_reference(function_name)

    return functools.partial(func, *args, **kwargs)


PipelineYAML.add_constructor('!PROCESSOR', _constructor_processor)

PipelineYAML.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PipelineYAML.add_constructor('!CMOS_PIPELINE', _constructor_cmos_pipeline)
# PipelineYAML.add_constructor('!PIPELINE', _constructor_detector_pipeline)

PipelineYAML.add_constructor('!CCD', _constructor_ccd)
PipelineYAML.add_constructor('!CMOS', _constructor_cmos)

PipelineYAML.add_constructor('!from_file', _constructor_from_file)
PipelineYAML.add_constructor('!function', _constructor_function)
PipelineYAML.add_constructor('!models', _constructor_models)


def load_config(yaml_file):

    with open(yaml_file, 'r') as file_obj:
        cfg = yaml.load(file_obj, Loader=PipelineYAML)

    return cfg
