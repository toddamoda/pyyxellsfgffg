#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel detector simulation framework.

Pyxel is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""
import argparse
import logging
import time
from pathlib import Path
import numpy as np
import esapy_config.io as io
import pyxel
from pyxel.pipelines.processor import Processor


def run(input_filename, random_seed: int = None):
    """TBW.

    :param input_filename:
    :param random_seed:
    :return:
    """
    logger = logging.getLogger('pyxel')
    logger.info('Pipeline started.')
    start_time = time.time()
    if random_seed:
        np.random.seed(random_seed)

    cfg = io.load(Path(input_filename))
    simulation = cfg['simulation']
    processor = Processor(cfg['detector'],
                          cfg['pipeline'])
    out = simulation.outputs
    out.set_input_file(input_filename)

    if simulation.mode == 'single':
        logger.info('Mode: Single')
        processor.pipeline.run_pipeline(processor.detector)
        out.single_output(detector=processor.detector)

    elif simulation.mode == 'calibration' and simulation.calibration:
        logger.info('Mode: Calibration')
        files = out.create_files()
        detector, results = simulation.calibration.run_calibration(processor, files)
        logger.info('Champion fitness:   %1.5e' % results['fitness'])
        out.calibration_output(detector=detector, results=results)

    elif simulation.mode == 'parametric' and simulation.parametric:
        logger.info('Mode: Parametric')
        configs = simulation.parametric.collect(processor)
        for processor in configs:
            processor.pipeline.run_pipeline(processor.detector)
            out.add_parametric_step(processor=processor,
                                    parametric=simulation.parametric)
        out.parametric_output()
    else:
        raise ValueError

    logger.info('Pipeline completed.')
    logger.info('Running time: %.3f seconds' % (time.time() - start_time))


def main():
    """Define the argument parser and run Pyxel."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-v', '--verbosity', action='count', default=0, help='Increase output verbosity (-v/-vv/-vvv)')
    parser.add_argument('-V', '--version', action='version',
                        version='Pyxel, version {version}'.format(version=pyxel.__version__))
    parser.add_argument('-c', '--config', type=str, required=True, help='Configuration file to load (YAML)')
    parser.add_argument('-s', '--seed', type=int, help='Random seed for the framework')

    # parser.add_argument('-o', '--output', type=str, default='outputs', help='Path for output folder')
    # parser.add_argument('-g', '--gui', default=False, type=bool, help='run Graphical User Interface')
    # parser.add_argument('-p', '--port', default=9999, type=int, help='The port to run the web server on')

    opts = parser.parse_args()

    logging_level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][min(opts.verbosity, 3)]
    log_format = '%(asctime)s - %(name)s - %(funcName)20s \t %(message)s'
    logging.basicConfig(level=logging_level, format=log_format, datefmt='%d-%m-%Y %H:%M:%S')

    if opts.config:
        run(input_filename=opts.config, random_seed=opts.seed)   # output_directory=opts.output,
    else:
        print('Define a YAML configuration file!')


if __name__ == '__main__':
    main()
