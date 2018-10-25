#   --------------------------------------------------------------------------
#   Copyright 2017 SRE-F, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PYXEL detector simulation framework.

PYXEL is a detector simulation framework, that can simulate a variety of
detector effects (e.g., cosmics, radiation-induced CTI  in CCDs, persistency
in MCT, diffusion, cross-talk etc.) on a given image.
"""
import logging
import argparse
from pathlib import Path
import numpy as np
import typing as t   # noqa: F401

import esapy_config as om
import pyxel
from pyxel import util
import pyxel.pipelines.processor
from pyxel.calibration.inputdata import read_plato_data
from pyxel.calibration.fitting import ModelFitting
import pygmo as pg


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


def run_pipeline_calibration(calib, config):
    """TBW.

    :param calib:
    :param config:
    :return:
    """
    # TODO these are still CDM SPECIFIC!!!
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(       # TODO
        data_path=calib.args['target_data'],
        data_files=data_files, start=None, end=None)
    weighting_func = calib.args['weighting_func']

    config.detector.charge_injection_profile = injection_profile
    config.detector.target_output_data = target_output
    config.detector.weighting_function = weighting_func

    fitting = ModelFitting(detector=config.detector, pipeline=config.pipeline)

    fitting.configure(model_names=calib.args['model_names'],
                      variables=calib.args['variables'],
                      var_arrays=calib.args['var_arrays'],
                      var_log=calib.args['var_log'],
                      params_per_variable=calib.args['params_per_variable'],
                      model_input=injection_profile,
                      target_output=target_output,
                      generations=calib.args['generations'],
                      population_size=calib.args['population_size'],
                      target_fit_range=calib.args['target_fit_range'],
                      out_fit_range=calib.args['output_fit_range']
                      )

    fitting.set_bound(low_val=calib.args['lower_boundary'],
                      up_val=calib.args['upper_boundary'])

    # fitting.set_normalization()                                       # TODO

    fitting.save_champions_in_file()
    if weighting_func is not None:
        fitting.set_weighting_function(weighting_func)

    prob = pg.problem(fitting)
    print('evolution started ...')
    opt_algorithm = pg.sade(gen=calib.args['generations'])
    algo = pg.algorithm(opt_algorithm)
    pop = pg.population(prob, size=calib.args['population_size'])
    pop = algo.evolve(pop)
    champion_x = pop.champion_x
    champion_f = pop.champion_f
    print('champion_x: ', champion_x,           # TODO log
          '\nchampion_f: ', champion_f)


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
