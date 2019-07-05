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
import sys
import time
from pathlib import Path
import numpy as np
import pyxel.io as io
from pyxel.pipelines.processor import Processor
from pyxel.detectors.ccd import CCD
# from pyxel import __version__ as pyxel_version


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
    if 'ccd_detector' in cfg:
        detector = cfg['ccd_detector']
    elif 'cmos_detector' in cfg:
        detector = cfg['cmos_detector']
    else:
        detector = cfg['ccd_detector']
    processor = Processor(detector, cfg['pipeline'])
    out = simulation.outputs
    if out:
        out.set_input_file(input_filename)
    else:
        logger.warning('Output is not defined! No output files will be saved!')
    detector.set_output_dir(out.output_dir)

    if simulation.mode == 'single':
        logger.info('Mode: Single')
        processor.pipeline.run_pipeline(detector)
        if out:
            out.single_output(processor)

    elif simulation.mode == 'calibration' and simulation.calibration:
        logger.info('Mode: Calibration')
        processor, results = simulation.calibration.run_calibration(processor, out)
        logger.info('Champion fitness:   %1.5e' % results['fitness'])
        if out:
            out.calibration_output(processor=processor, results=results)

    elif simulation.mode == 'parametric' and simulation.parametric:
        logger.info('Mode: Parametric')
        configs = simulation.parametric.collect(processor)
        for proc in configs:
            proc.pipeline.run_pipeline(proc.detector)
            if out:
                out.add_parametric_step(processor=proc,
                                        parametric=simulation.parametric)
        if out:
            out.parametric_output()

    elif simulation.mode == 'dynamic' and simulation.dynamic:
        logger.info('Mode: Dynamic')
        if 'non_destructive_readout' not in simulation.dynamic or isinstance(detector, CCD):
            simulation.dynamic['non_destructive_readout'] = False
        if 't_step' in simulation.dynamic and 'steps' in simulation.dynamic:
            detector.set_dynamic(steps=simulation.dynamic['steps'],
                                 time_step=simulation.dynamic['t_step'],
                                 ndreadout=simulation.dynamic['non_destructive_readout'])
        while detector.elapse_time():
            logger.info('time = %.3f s' % detector.time)
            if detector.is_non_destructive_readout:
                detector.initialize(reset_all=False)
            else:
                detector.initialize(reset_all=True)
            processor.pipeline.run_pipeline(detector)
            if out and detector.read_out:
                out.single_output(processor)

    else:
        raise ValueError

    logger.info('Pipeline completed.')
    logger.info('Running time: %.3f seconds' % (time.time() - start_time))
    # Closing the logger in order to be able to move the file in the output dir
    logging.shutdown()
    out.save_log_file()


# TODO: Remove this. Get the current version from '__version__' in 'pyxel/__init__.py'
def get_pyxel_version():
    """Extract 'pyxel_version' from 'setup.cfg'."""
    from setuptools.config import read_configuration

    parent_folder = Path(__file__).parent
    setup_cfg_filename = parent_folder.joinpath('../setup.cfg').resolve(strict=True)
    metadata = read_configuration(setup_cfg_filename)['metadata']  # type: dict

    return metadata['version']


def main():
    """Define the argument parser and run Pyxel."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument('-v', '--verbosity', action='count', default=0, help='Increase output verbosity (-v/-vv/-vvv)')
    parser.add_argument('-V', '--version', action='version',
                        version='Pyxel, version {version}'.format(version=get_pyxel_version()))
    parser.add_argument('-c', '--config', type=str, required=True, help='Configuration file to load (YAML)')
    parser.add_argument('-s', '--seed', type=int, help='Random seed for the framework')

    # parser.add_argument('-o', '--output', type=str, default='outputs', help='Path for output folder')
    # parser.add_argument('-g', '--gui', default=False, type=bool, help='run Graphical User Interface')
    # parser.add_argument('-p', '--port', default=9999, type=int, help='The port to run the web server on')

    opts = parser.parse_args()

    logging_level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][min(opts.verbosity, 3)]
    log_format = '%(asctime)s - %(name)s - %(funcName)30s \t %(message)s'
    logging.basicConfig(filename='pyxel.log',
                        level=logging_level,
                        format=log_format,
                        datefmt='%d-%m-%Y %H:%M:%S')
    # If user wants the log in stdout AND in file, use the three lines below
    stream_stdout = logging.StreamHandler(sys.stdout)
    stream_stdout.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_stdout)

    if opts.config:
        run(input_filename=opts.config, random_seed=opts.seed)   # output_directory=opts.output,
    else:
        print('Define a YAML configuration file!')


if __name__ == '__main__':
    main()
