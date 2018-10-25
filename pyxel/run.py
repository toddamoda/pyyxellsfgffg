#   --------------------------------------------------------------------------
#   Copyright 2017 SRE-F, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PYXEL detector simulation framework.

PYXEL is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""
import argparse
import logging
from pathlib import Path
import numpy as np
import esapy_config as om
import pyxel
import pyxel.pipelines.processor
from pyxel import util
from pyxel.calibration.calibration import run_pipeline_calibration


def run(input_filename, output_file, random_seed: int = None):  # key=None, value=None
    """TBW.

    :param input_filename:
    :param output_file:
    :param random_seed:
    :param key:
    :param value:
    :return:
    """
    if random_seed:
        np.random.seed(random_seed)
    output = []

    cfg = om.load(Path(input_filename))
    simulation = cfg['simulation']
    processor = cfg['processor']
    detector = None

    # if key and value:
    #     processor.set(key, value)
    # simulation.debug(processor)

    if simulation.mode == 'single':
        detector = processor.pipeline.run_pipeline(processor.detector)

    elif simulation.mode == 'calibration':
        run_pipeline_calibration(simulation.calibration, processor)

    elif simulation.mode == 'parametric':
        configs = simulation.parametric_analysis.collect(processor)
        for config in configs:
            detector = config.pipeline.run_pipeline(config.detector)

    else:
        raise AttributeError

    if output_file and detector:
        save_to = util.apply_run_number(output_file)
        out = util.FitsFile(save_to)
        out.save(detector.image, header=None, overwrite=True)
        # todo: BUG creates new, fits file with random filename and without extension
        # ... when it can not save data to fits file (because it is opened/used by other process)
        output.append(output_file)

    print('Pipeline completed.')
    return output


def main():
    """Define the argument parser and run the pipeline."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'export'])

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file to load (YAML or INI)')

    parser.add_argument('-o', '--output',
                        help='output file')

    parser.add_argument('-s', '--seed',
                        help='Define random seed for the framework')

    opts = parser.parse_args()

    # Set logger
    log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    log_format = '%(asctime)s - %(name)s - %(funcName)s - %(thread)d - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    if opts.command == 'run':
        run(opts.config, opts.output, int(opts.seed))

    elif opts.command == 'export':
        if opts.type is None:
            print('Missing argument -t/--type')
            parser.print_help()
            return
        # run_export(opts.config, opts.output, opts.type)


if __name__ == '__main__':
    main()
