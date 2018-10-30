"""TBW."""
import pygmo as pg
from astropy.io import fits
from pyxel.calibration.fitting import ModelFitting
# from pyxel.calibration.inputdata import read_plato_data


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
    # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    # injection_profile, target_output, target_error = read_plato_data(       # TODO
    #     data_path=calib.args['target_data'],
    #     data_files=data_files, start=None, end=None)

    weighting_func = calib.args['weighting_func']               # TODO read wf from a file as 1d np.array

    # target_output = target_output[0]
    target_output = fits.getdata('pyxel/results.fits')      # 100 x 100 pixels

    # config.detector.charge_injection_profile = injection_profile
    config.detector.target_output_data = target_output
    config.detector.weighting_function = weighting_func

    fitting = ModelFitting(detector=config.detector, pipeline=config.pipeline)

    if 'population_size' in calib.args:
        population_size = calib.args['population_size']
    else:
        raise AttributeError('Missing "population_size" from YAML config')

    fitting.configure(model_names=calib.args['model_names'],
                      variables=calib.args['variables'],
                      var_arrays=calib.args['var_arrays'],
                      var_log=calib.args['var_log'],
                      params_per_variable=calib.args['params_per_variable'],
                      target_output=target_output,
                      population_size=population_size,
                      target_fit_range=calib.args['target_fit_range'],
                      out_fit_range=calib.args['output_fit_range'],
                      fitness_mode=calib.args['fitness_mode'],
                      simulation_output=calib.args['output'],
                      sort_by_var=calib.args['sort_by_var'])

    # fitting.set_normalization()                                       # TODO

    fitting.set_bound(low_val=calib.args['lower_boundary'],
                      up_val=calib.args['upper_boundary'])

    fitting.save_champions_in_file()
    if weighting_func is not None:
        fitting.set_weighting_function(weighting_func)

    prob = pg.problem(fitting)
    print('evolution started ...')

    alg_set = AlgorithmSettings(calib)
    opt_algorithm = alg_set.set_algorithm()
    fitting.generations = alg_set.generations
    algo = pg.algorithm(opt_algorithm)
    pop = pg.population(prob, size=population_size)
    pop = algo.evolve(pop)

    champion_f = pop.champion_f
    champion_x = fitting.split_and_update(pop.champion_x)
    print('\nchampion_f: ', champion_f[0])
    print('champion_x:', *champion_x, sep="\n")


class AlgorithmSettings:
    """TBW.

    :return:
    """

    def __init__(self, calib: Calibration) -> None:
        """TBW."""
        self.algo_type = calib.args['algorithm']    # type: str
        self.generations = None

        if self.algo_type == 'sade':
            self.generations = 1                    # type: int
            self.variant = 2                        # type: int
            self.variant_adptv = 1                  # type: int
            self.ftol = 1e-06                       # type: float
            self.xtol = 1e-06                       # type: float
            self.memory = False                     # type: bool

        elif self.algo_type == 'sga':
            self.generations = 1                    # type: int
            self.cr = 0.9                           # type: float
            self.eta_c = 1.0                        # type: float
            self.m = 0.02                           # type: float
            self.param_m = 1.0                      # type: float
            self.param_s = 2                        # type: int
            self.crossover = 'exponential'          # type: str
            self.mutation = 'polynomial'            # type: str
            self.selection = 'tournament'           # type: str

        elif self.algo_type == 'nlopt':
            self.nlopt_solver = 'neldermead'        # type: str
            self.maxtime = 0                        # type: int
            self.maxeval = 0                        # type: int
            self.xtol_rel = 1.e-8                   # type: float
            self.xtol_abs = 0.                      # type: float
            self.ftol_rel = 0.                      # type: float
            self.ftol_abs = 0.                      # type: float
            self.stopval = float('-inf')            # type: float
            self.local_optimizer = None             # type: None
            self.replacement = 'best'               # type: str
            self.selection = 'best'                 # type: str

        names = ['generations',
                 'variant', 'variant_adptv', 'ftol', 'xtol', 'memory',
                 'cr', 'crossover', 'm', 'mutation', 'param_s', 'selection', 'eta_c', 'param_m',
                 'maxtime', 'maxeval', 'xtol_rel', 'xtol_abs', 'ftol_rel', 'ftol_abs', 'stopval',
                 'local_optimizer', 'replacement', 'selection', 'nlopt_solver']
        for name in names:
            if name in calib.args:
                value = calib.args[name]
                setattr(self, name, value)

    def set_algorithm(self):
        """TBW.

        :return:
        """
        if self.algo_type == 'sade':
            opt_algorithm = pg.sade(gen=self.generations,
                                    variant=self.variant,
                                    variant_adptv=self.variant_adptv,
                                    ftol=self.ftol, xtol=self.xtol,
                                    memory=self.memory)
        elif self.algo_type == 'sga':
            opt_algorithm = pg.sga(gen=self.generations,
                                   cr=self.cr,                      # crossover probability
                                   crossover=self.crossover,        # single, exponential, binomial, sbx
                                   m=self.m,                        # mutation probability
                                   mutation=self.mutation,          # uniform, gaussian, polynomial
                                   param_s=self.param_s,            # number of best ind. in 'truncated'/tournament
                                   selection=self.selection,        # tournament, truncated
                                   eta_c=self.eta_c,                # distribution index for sbx crossover
                                   param_m=self.param_m)            # mutation parameter
        elif self.algo_type == 'nlopt':
            opt_algorithm = pg.nlopt(self.nlopt_solver)
            opt_algorithm.maxtime = self.maxtime        # stop when the optimization time (in seconds) exceeds maxtime
            opt_algorithm.maxeval = self.maxeval        # stop when the number of function evaluations exceeds maxeval
            opt_algorithm.xtol_rel = self.xtol_rel      # relative stopping criterion for x
            opt_algorithm.xtol_abs = self.xtol_abs      # absolute stopping criterion for x
            opt_algorithm.ftol_rel = self.ftol_rel
            opt_algorithm.ftol_abs = self.ftol_abs
            opt_algorithm.stopval = self.stopval
            opt_algorithm.local_optimizer = self.local_optimizer
            opt_algorithm.replacement = self.replacement
            opt_algorithm.selection = self.selection
        else:
            raise NotImplementedError

        return opt_algorithm
