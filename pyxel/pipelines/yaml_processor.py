import functools
import typing as t
from pathlib import Path

import numpy as np
import yaml

from pyxel.util import fitsfile
from pyxel.detectors.ccd import CCDDetector
from pyxel.pipelines import ccd_pipeline
from pyxel.pipelines import config
from pyxel.util import util
from pyxel.util.fitsfile import FitsFile


# from pyxel.pipelines.ccd_transfer_function import CCDTransferFunction

class PipelineYAML(yaml.SafeLoader):
    pass


def _constructor_ccd_pipeline(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)     # type: dict

    obj = config.DetectionPipeline(**mapping)

    return obj


def _constructor_ccd(loader: PipelineYAML, node: yaml.MappingNode):
    mapping = loader.construct_mapping(node, deep=True)  # type: dict

    if 'geometry' in mapping:
        geometry = config.Geometry(**mapping['geometry'])
    else:
        geometry = None

    if 'environment' in mapping:
        environment = config.Environment(**mapping['environment'])
    else:
        environment = None

    if 'characteristics' in mapping:
        characteristics = config.CCDCharacteristics(**mapping['characteristics'])
    else:
        characteristics = None

    photons = mapping.get('photons', None)
    signal = mapping.get('signal', None)
    charge = mapping.get('charge', None)

    obj = config.CCD(photons=photons,
                     signal=signal,
                     charge=charge,
                     geometry=geometry,
                     environment=environment,
                     characteristics=characteristics)

    return obj


def _constructor_from_file(loader: PipelineYAML, node: yaml.ScalarNode):
    noise_filename = Path(loader.construct_scalar(node))
    if noise_filename.suffix.lower().startswith('.fit'):
        result = fitsfile.FitsFile(str(noise_filename)).data
    else:
        result = np.fromfile(str(noise_filename), dtype=float, sep=' ')
    return result


def _constructor_models(loader: PipelineYAML, node: yaml.ScalarNode):
    try:
        mapping = loader.construct_mapping(node)             # type: dict
    except:
    # except yaml.construtor.ConstructorError:
        mapping = {}

    return config.Models(mapping)


def _constructor_function(loader: PipelineYAML, node: yaml.ScalarNode):
    mapping = loader.construct_mapping(node)             # type: dict

    function_name = mapping['name']                      # type: str
    kwargs = mapping.get('kwargs', {})
    args = mapping.get('args', {})

    func = util.evaluate_reference(function_name)        # type: t.Callable
    return functools.partial(func, *args, **kwargs)


PipelineYAML.add_constructor('!CCD_PIPELINE', _constructor_ccd_pipeline)
PipelineYAML.add_constructor('!CCD', _constructor_ccd)
PipelineYAML.add_constructor('!from_file', _constructor_from_file)
PipelineYAML.add_constructor('!function', _constructor_function)
PipelineYAML.add_constructor('!models', _constructor_models)


def load_config(yaml_file):

    with open(yaml_file, 'r') as file_obj:
        cfg = yaml.load(file_obj, Loader=PipelineYAML)

    return cfg


def save_signal(ccd: CCDDetector, output_filename: Path):
    """ Save the 'signal' from a `CCDDetector` object into a FITS file.

    :param ccd:
    :param output_filename:
    """
    data = ccd.signal.value         # remove the unit

    # creating new fits file with new data
    new_fits_file = FitsFile(output_filename)
    new_fits_file.save(data)

    # # writing ascii output file
    # if opts.output.data:
    #     out_file = get_data_dir(opts.output.data)
    #     with open(out_file, 'a+') as file_obj:
    #         data = [
    #             '{:6d}'.format(opts.ccd.photons),
    #             '{:8.2f}'.format(signal_mean),
    #             '{:7.2f}'.format(signal_sigma)
    #         ]
    #         out_str = '\t'.join(data) + '\n'
    #         file_obj.write(out_str)


def main():
    # Step 1: Get the pipeline configuration
    config_path = Path(__file__).parent.parent.joinpath('settings.yaml')
    # cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # cfg = load_config(os.path.join(cwd, 'settings.yaml'))     # type: DetectionPipeline
    cfg = load_config(str(config_path))

    # Step 2: Run the pipeline
    result = ccd_pipeline.run_pipeline(cfg)         # type: CCDDetector
    print('Pipeline completed.')

    # Step 3: Save the result(s) in FITS, ASCII, Jupyter Notebook(s), ...
    save_signal(ccd=result, output_filename='result.fits')


if __name__ == '__main__':
    main()
