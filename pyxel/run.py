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
# from pyxel.calibration.calibration import Calibration
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
    parametric = cfg['parametric']      # todo: "parametric" should be renamed e.g. to "simulation"
    processor = cfg['processor']
    detector = None

    # if key and value:
    #     processor.set(key, value)

    # parametric.debug(processor)
    configs = parametric.collect(processor)

    for config in configs:
        # "model calibration" mode
        if parametric.mode == 'calibration':        # todo: call pygmo applicaiton, multi-processing
            run_pipeline_calibration(parametric, config)
        # "single run" or "parametric/sensitivity analysis" mode
        else:
            detector = config.pipeline.run_pipeline(config.detector)

    if output_file and detector:
        save_to = util.apply_run_number(output_file)
        out = util.FitsFile(save_to)
        out.save(detector.image, header=None, overwrite=True)
        # todo: BUG creates new, fits file with random filename and without extension
        # ... when it can not save data to fits file (because it is opened/used by other process)
        output.append(output_file)

    print('Pipeline completed.')
    return output


def run_pipeline_calibration(settings, config):
    """TBW.

    :param settings:
    :param config:
    :return:
    """
    # read data you want to fit with your models:
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(
        data_path=r'C:/dev/work/cdm/data/better-plato-target-data/',
        data_files=data_files, start=None, end=None)
    weighting_func = None
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    generations = 3
    population_size = 10

    # # FUNC TO ADD MODEL INPUT DATA AND TARGET DATA TO DETECTOR OBJ:
    # add_data_to_detector_object(injection_profile,    # TODO
    #                             target_output,
    #                             weighting_func
    #                             )

    fitting = ModelFitting(detector=config.detector,
                           pipeline=config.pipeline)

    # # #################################################
    # # Model specific input arguements:
    # traps = 4                           # TODO read these from YAML config automatically
    # number_of_transfers = 1552
    # ptp = 947.22e-6  # s
    # fwc = 1.e6  # e-
    # vg = 1.62e-10  # cm**3 (half volume!)
    # # # vth = 1.2175e7            # cm/s, from Alex's code
    # vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
    # # sigma = 5.e-16              # cm**2 (for all traps)
    # sigma = None  # cm**2 (for all traps)
    # fitting.charge_injection(True)
    # fitting.set_parallel_parameters(traps=traps, t=ptp, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    # fitting.set_dimensions(para_transfers=number_of_transfers)

    fitting.configure(model_names=['cdm', 'tars'],
                      params_per_model=[[4, 4, 4, 1], [1]],
                      variables=[['tr_p', 'nt_p', 'sigma_p', 'beta_p'], ['initial_energy']],
                      var_arrays=[[True, True, True, False], [False]],
                      var_log=[[True, True, True, False], [False]],
                      model_input=injection_profile,                    # TODO should be added to detector obj
                      target_output=target_output,                      # TODO should be added to detector obj
                      generations=generations,
                      population_size=population_size)

    fitting.set_bound(low_val=[[1.e-3, 1.e-2, 1.e-20, 0.], [1.]],
                      up_val=[[2., 1.e+1, 1.e-15, 1.], [10.]])

    fitting.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    fitting.set_target_fit_range((target_start_fit, target_end_fit))
    fitting.set_normalization()
    fitting.save_champions_in_file()
    if weighting_func is not None:
        fitting.set_weighting_function(weighting_func)

    prob = pg.problem(fitting)
    print('evolution started ...')
    opt_algorithm = pg.sade(gen=generations)
    algo = pg.algorithm(opt_algorithm)
    pop = pg.population(prob, size=population_size)
    pop = algo.evolve(pop)
    champion_x = pop.champion_x
    champion_f = pop.champion_f
    print('champion_x: ', champion_x,
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
