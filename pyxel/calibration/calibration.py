"""TBW."""
import numpy as np
import pygmo as pg
import typing as t      # noqa: F401
import esapy_config as om
from astropy.io import fits
from pyxel.calibration.fitting import ModelFitting


@om.attr_class
class Calibration:
    """TBW.

    :return:
    """

    calibration_mode = om.attr_def(
        type=str,
        validator=om.validate_choices(['pipeline', 'single_model']),
        default='pipeline',
        doc=''
    )
    output = om.attr_def(
        type=str,
        validator=om.validate_choices(['image', 'signal', 'charge']),
        default='image',
        doc=''
    )
    output_fit_range = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    target_data_path = om.attr_def(
        type=list,
        default=None,
        doc=''
    )
    target_fit_range = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    fitness_mode = om.attr_def(
        type=str,
        validator=om.validate_choices(['residuals', 'least-squares', 'custom']),
        default='residuals',
        doc=''
    )
    # fitness_func_path = om.attr_def(
    #     type=str,
    #     validator=om.validate_choices([]),
    #     default='image',
    #     doc='output'
    # )
    algorithm = om.attr_def(
        type=str,
        validator=om.validate_choices(['sade', 'sga', 'nlopt']),
        default='sade',
        doc=''
    )
    seed = om.attr_def(
        type=int,
        validator=om.validate_range(0, 100000),
        default=0,
        doc=''
    )
    generations = om.attr_def(
        type=int,
        validator=om.validate_range(1, 100000),
        default=1,
        doc=''
    )
    population_size = om.attr_def(
        type=int,
        validator=om.validate_range(1, 100000),
        default=1,
        doc=''
    )
    model_names = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    variables = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    params_per_variable = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    var_log = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    lower_boundary = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    upper_boundary = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    sort_var = om.attr_def(
        type=str,
        # validator=
        default=None,
        doc=''
    )

    ###### SADE
    variant = om.attr_def(type=int, validator=om.validate_range(1, 18), default=2, doc='')
    variant_adptv = om.attr_def(type=int, validator=om.validate_range(1, 2), default=1, doc='')
    ftol = om.attr_def(type=float, default=1e-06, doc='')  # validator=om.validate_range(1, 18),
    xtol = om.attr_def(type=float, default=1e-06, doc='')  # validator=om.validate_range(1, 18),
    memory = om.attr_def(type=bool, default=False, doc='')
    ###### SADE

    ###### SGA
    cr = om.attr_def(type=float, validator=om.validate_range(0, 1), default=0.9, doc='')
    eta_c = om.attr_def(type=float, default=1.0, doc='')    # validator=om.validate_range(0, 1),
    m = om.attr_def(type=float, validator=om.validate_range(0, 1), default=0.02, doc='')
    param_m = om.attr_def(type=float, default=1.0, doc='')   # validator=om.validate_range(1, 2),
    param_s = om.attr_def(type=int, default=2, doc='')  # validator=om.validate_range(1, 2),
    crossover = om.attr_def(type=str, default='exponential', doc='')  # validator=om.validate_choices(),
    mutation = om.attr_def(type=str, default='polynomial', doc='')  # validator=om.validate_choices(),
    selection = om.attr_def(type=str, default='tournament', doc='')   # validator=om.validate_choices(),
    ###### SGA

    # TODO other attributes from __init__
    # TODO custom fitness_func

    # def __init__(self,
    #              arguments: dict) -> None:
    #     """TBW."""
    #     # arguments = {}
    #     self.args = arguments                               # type: dict
    #     self.mode = 'pipeline'
    #     self.algo_type = None
    #     self.generations = None                             # type: t.Optional[int]
    #
    #     if self.args:
    #         self.mode = self.args['calibration_mode']       # type: str
    #         self.algo_type = self.args['algorithm']         # type: str
    #
    #     if self.algo_type == 'sade':
    #         self.generations = 1                            # type: int
    #         self.variant = 2                                # type: int
    #         self.variant_adptv = 1                          # type: int
    #         self.ftol = 1e-06                               # type: float
    #         self.xtol = 1e-06                               # type: float
    #         self.memory = False                             # type: bool
    #
    #     elif self.algo_type == 'sga':
    #         self.generations = 1                            # type: int
    #         self.cr = 0.9                                   # type: float
    #         self.eta_c = 1.0                                # type: float
    #         self.m = 0.02                                   # type: float
    #         self.param_m = 1.0                              # type: float
    #         self.param_s = 2                                # type: int
    #         self.crossover = 'exponential'                  # type: str
    #         self.mutation = 'polynomial'                    # type: str
    #         self.selection = 'tournament'                   # type: str
    #
    #     elif self.algo_type == 'nlopt':
    #         self.nlopt_solver = 'neldermead'                # type: str
    #         self.maxtime = 0                                # type: int
    #         self.maxeval = 0                                # type: int
    #         self.xtol_rel = 1.e-8                           # type: float
    #         self.xtol_abs = 0.                              # type: float
    #         self.ftol_rel = 0.                              # type: float
    #         self.ftol_abs = 0.                              # type: float
    #         self.stopval = float('-inf')                    # type: float
    #         self.local_optimizer = None                     # type: None
    #         self.replacement = 'best'                       # type: str
    #         self.selection = 'best'                         # type: str
    #
    #     names = ['generations',
    #              'variant', 'variant_adptv', 'ftol', 'xtol', 'memory',
    #              'cr', 'crossover', 'm', 'mutation', 'param_s', 'selection', 'eta_c', 'param_m',
    #              'maxtime', 'maxeval', 'xtol_rel', 'xtol_abs', 'ftol_rel', 'ftol_abs', 'stopval',
    #              'local_optimizer', 'replacement', 'selection', 'nlopt_solver']
    #     if self.args:
    #         for name in names:
    #             if name in self.args:
    #                 value = self.args[name]
    #                 setattr(self, name, value)

    def set_algorithm(self):
        """TBW.

        :return:
        """
        if self.algorithm == 'sade':
            opt_algorithm = pg.sade(gen=self.generations,
                                    variant=self.variant,
                                    variant_adptv=self.variant_adptv,
                                    ftol=self.ftol, xtol=self.xtol,
                                    memory=self.memory)
        elif self.algorithm == 'sga':
            opt_algorithm = pg.sga(gen=self.generations,
                                   cr=self.cr,                      # crossover probability
                                   crossover=self.crossover,        # single, exponential, binomial, sbx
                                   m=self.m,                        # mutation probability
                                   mutation=self.mutation,          # uniform, gaussian, polynomial
                                   param_s=self.param_s,            # number of best ind. in 'truncated'/tournament
                                   selection=self.selection,        # tournament, truncated
                                   eta_c=self.eta_c,                # distribution index for sbx crossover
                                   param_m=self.param_m)            # mutation parameter
        # elif self.algorithm == 'nlopt':
        #     opt_algorithm = pg.nlopt(self.nlopt_solver)
        #     opt_algorithm.maxtime = self.maxtime        # stop when the optimization time (in seconds) exceeds maxtime
        #     opt_algorithm.maxeval = self.maxeval        # stop when the number of function evaluations exceeds maxeval
        #     opt_algorithm.xtol_rel = self.xtol_rel      # relative stopping criterion for x
        #     opt_algorithm.xtol_abs = self.xtol_abs      # absolute stopping criterion for x
        #     opt_algorithm.ftol_rel = self.ftol_rel
        #     opt_algorithm.ftol_abs = self.ftol_abs
        #     opt_algorithm.stopval = self.stopval
        #     opt_algorithm.local_optimizer = self.local_optimizer
        #     opt_algorithm.replacement = self.replacement
        #     opt_algorithm.selection = self.selection
        else:
            raise NotImplementedError

        return opt_algorithm

    def run_calibration(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        # seed = self.args['seed']
        if self.seed is None:
            self.seed = np.random.randint(0, 1000000)
        print('pygmo seed: ', self.seed)
        pg.set_global_rng_seed(seed=self.seed)

        fitting = ModelFitting(processor)

        target_output = read_data(self.target_data_path)
        processor.detector.target_output_data = target_output

        # if 'population_size' in self.args:
        #     population_size = self.args['population_size']
        # else:
        #     raise AttributeError('Missing "population_size" from YAML config')
        # sort_var = None
        # if 'sort_by_var' in self.args:
        #     sort_var = self.args['sort_by_var']

        fitting.set_parameters(calibration_mode=self.calibration_mode,
                               model_names=self.model_names,
                               variables=self.variables,
                               var_log=self.var_log,
                               generations=self.generations,
                               population_size=self.population_size,
                               fitness_mode=self.fitness_mode,
                               simulation_output=self.output,
                               sort_by_var=self.sort_var)
        fitting.configure(params_per_variable=self.params_per_variable,
                          target_output_list=target_output,
                          target_fit_range=self.target_fit_range,
                          out_fit_range=self.output_fit_range)

        if self.fitness_mode == 'custom':
            fitting.set_custom_fitness(self.fitness_func_path)
        # if self.weighting_func_path:
        #     weighting_func = read_data(self.weighting_func_path)
        #     fitting.set_weighting_function(weighting_func[0])           # works only with one weighting function
        fitting.set_bound(low_val=self.lower_boundary,
                          up_val=self.upper_boundary)
        fitting.save_champions_in_file()
        # fitting.set_normalization()                                       # TODO

        prob = pg.problem(fitting)
        print('evolution started ...')

        opt_algorithm = self.set_algorithm()
        algo = pg.algorithm(opt_algorithm)

        pop = pg.population(prob, size=self.population_size)
        pop = algo.evolve(pop)

        champion_f = pop.champion_f
        champion_x = fitting.split_and_update_parameter(pop.champion_x)
        print('\nchampion_f:   %1.5e' % champion_f[0])
        print('champion_x: ', *champion_x, sep="\n")

        return 1        # todo: return results as output!!


def read_data(data_path: t.Union[str, list]):
    """TBW.

    :param data_path:
    :return:
    """
    if isinstance(data_path, str):
        data_path = [data_path]
    elif isinstance(data_path, list) and all(isinstance(item, str) for item in data_path):
        pass
    else:
        raise TypeError

    output = []                             # type: list
    for i in range(len(data_path)):
        if '.fits' in data_path[i]:
            data = fits.getdata(data_path[i])
        elif '.npy' in data_path[i]:
            data = np.load(data_path[i])
        else:
            data = np.loadtxt(data_path[i], dtype=float, delimiter='|')     # todo: more general with try-except
        output += [data]

    return output
