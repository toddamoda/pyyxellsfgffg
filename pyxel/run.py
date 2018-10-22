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
from pyxel.calibration.problem import ModelFitting
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
    # what we have in the beginning:
    # - settings (which is the "parametric" object)
    # - config.pipeline
    # - config.detector

    # read data you want to fit with your models:
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(
        data_path=r'C:/dev/work/cdm/data/better-plato-target-data/', data_files=data_files, start=None, end=None)

    # create and initialize your calibration class (setting params based on config):
    # calibration = Calibration(settings, config)
    # calibration.set_data(model_input_data=injection_profile,
    #                      target_output=target_output)
    #                      input_data=model_input_data, target=target_output, variables=parameters,
    #                      gen=generations, pop=population_size)
    fitting = ModelFitting(detector=config.detector,
                           pipeline=config.pipeline)
    prob = pg.problem(fitting)
    # prob = pg.problem(pg.rosenbrock())
    print('evolution')
    opt_algorithm = pg.sade(gen=10)
    algo = pg.algorithm(opt_algorithm)
    pop = pg.population(prob, size=10)
    pop = algo.evolve(pop)
    uda = algo.extract(pg.sade)
    uda.get_log()
    champion_x = pop.champion_x  # TODO: select the best N champions and fill pop2 with them
    champion_f = pop.champion_f
    print(champion_x, champion_f)

    # fitting.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    # fitting.set_target_fit_range((target_start_fit, target_end_fit))
    # fitting.set_uniformity_scales(sc_tr=tr_scale, sc_nt=nt_scale, sc_sig=sigma_scale,
    #                                    sc_be=beta_scale)
    # fitting.set_bound(low_val=lb, up_val=ub)
    # fitting.set_normalization()
    # fitting.save_champions_in_file()
    # if weighting_func is not None:
    #     fitting.set_weighting_function(weighting_func)
    # # #################################################
    # # Model specific input arguements:
    # traps = 4  # TODO read these from YAML config automatically
    # number_of_transfers = 1552
    # t = 947.22e-6  # s
    # fwc = 1.e6  # e-
    # vg = 1.62e-10  # cm**3 (half volume!)
    # # # vth = 1.2175e7            # cm/s, from Alex's code
    # vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
    # # sigma = 5.e-16              # cm**2 (for all traps)
    # sigma = None  # cm**2 (for all traps)
    # fitting.charge_injection(True)  # TODO set these from YAML config automatically
    # fitting.set_parallel_parameters(traps=traps, t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    # fitting.set_dimensions(para_transfers=number_of_transfers)

    # aa, bb = calibration.evolutionary_algorithm()
    # # calibration.nonlinear_optimization_algorithm()


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
