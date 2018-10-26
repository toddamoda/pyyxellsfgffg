"""TBW."""
import pygmo as pg
from astropy.io import fits
from pyxel.calibration.fitting import ModelFitting
from pyxel.calibration.inputdata import read_plato_data


class Calibration:
    """TBW.

    :return:
    """

    def __init__(self,
                 calibration_mode: str,
                 arguments: dict,
                 ) -> None:
        """TBW."""
        self.calibration_mode = calibration_mode
        self.args = arguments


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

    # target_output = fits.getdata(calib.args['target_data'])
    target_output = fits.getdata('pyxel/results.fits')      # 100 x 100 pixels

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
