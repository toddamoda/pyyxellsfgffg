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
from pyxel import util


def single_output(detector, output_file):    # TODO
    """TBW."""
    # if output_file:
    save_to = util.apply_run_number(output_file)
    out = util.FitsFile(save_to)
    out.save(detector.image.array, header=None, overwrite=True)
    # todo: BUG creates new, fits file with random filename and without extension when it can not open file


def calibration_output(results):        # TODO
    """TBW."""
    pass


def parametric_output(config, detector):        # TODO
    """TBW."""
    pass


def run(input_filename, output_file: str = None, random_seed: int = None):
    """TBW.

    :param input_filename:
    :param output_file:
    :param random_seed:
    :return:
    """
    start_time = time.time()
    if random_seed:
        np.random.seed(random_seed)

    cfg = io.load(Path(input_filename))
    simulation = cfg['simulation']
    detector = cfg['detector']
    pipeline = cfg['pipeline']
    processor = Processor(detector, pipeline)

    if simulation.mode == 'single':
        detector = processor.pipeline.run_pipeline(processor.detector)
        single_output(detector, output_file)           # TODO implement

    elif simulation.mode == 'calibration':
        simulation.calibration.run_calibration(processor)
        # calibration_results = simulation.calibration.run_calibration(processor)
        # TODO: return the optimal model/detector parameters as dict or obj
        # calibration_output(calibration_results)      # TODO implement

    elif simulation.mode == 'parametric':
        configs = simulation.parametric.collect(processor)
        for config in configs:
            detector = config.pipeline.run_pipeline(config.detector)
            # parametric_output(config, detector)      # TODO implement
            single_output(detector, "outputs/image_generated_??.fits")       # TODO temporarily

    else:
        raise ValueError

    print('\nPipeline completed.')
    print("Running time: %.3f seconds" % (time.time() - start_time))
    # return output


def main():
    """Define the argument parser and run Pyxel."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity')

    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s (version {version})'.format(version=pyxel.__version__))

    parser.add_argument('-g', '--gui', default=False, type=bool, help='run Graphical User Interface')

    parser.add_argument('-c', '--config', type=str, help='Configuration file to load (YAML)')

    parser.add_argument('-o', '--output', type=str, help='output file')

    parser.add_argument('-s', '--seed', type=int, help='Random seed for the framework')

    parser.add_argument('-p', '--port', default=9999, type=int, help='The port to run the web server on')

    opts = parser.parse_args()

    # Set logger
    logging_level = logging.INFO  # logging.DEBUG
    # log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
    del logging.root.handlers[:]
    log_format = '%(asctime)s - %(funcName)s \t\t\t %(message)s'   # %(name)s - %(threadName)s -
    logging.basicConfig(level=logging_level, format=log_format)
    logging.info('\n*** Pyxel ***\n')

    if opts.gui:
        # run_web_server(opts.port)
        raise NotImplementedError
    elif opts.config:
        run(opts.config, opts.output, opts.seed)
    else:
        print('Either define a YAML config file or use the GUI')


if __name__ == '__main__':
    main()
