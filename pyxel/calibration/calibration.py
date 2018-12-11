"""TBW."""
import numpy as np
import pygmo as pg
# import typing as t      # noqa: F401
import esapy_config as om

from pyxel.calibration.fitting import ModelFitting
from pyxel.calibration.util import read_data


@om.attr_class
class Algorithm:
    """TBW.

    :return:
    """

    type = om.attr_def(
        type=str,
        validator=om.validate_choices(['sade', 'sga', 'nlopt']),
        default='sade',
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

    # SADE #####
    variant = om.attr_def(type=int, validator=om.validate_range(1, 18), default=2, doc='')
    variant_adptv = om.attr_def(type=int, validator=om.validate_range(1, 2), default=1, doc='')
    ftol = om.attr_def(type=float, default=1e-06, doc='')  # validator=om.validate_range(),
    xtol = om.attr_def(type=float, default=1e-06, doc='')  # validator=om.validate_range(),
    memory = om.attr_def(type=bool, default=False, doc='')
    # SADE #####

    # SGA #####
    cr = om.attr_def(type=float, validator=om.validate_range(0, 1), default=0.9, doc='')
    eta_c = om.attr_def(type=float, default=1.0, doc='')    # validator=om.validate_range(0, 1),
    m = om.attr_def(type=float, validator=om.validate_range(0, 1), default=0.02, doc='')
    param_m = om.attr_def(type=float, default=1.0, doc='')   # validator=om.validate_range(1, 2),
    param_s = om.attr_def(type=int, default=2, doc='')  # validator=om.validate_range(1, 2),
    crossover = om.attr_def(type=str, default='exponential', doc='')  # validator=om.validate_choices(),
    mutation = om.attr_def(type=str, default='polynomial', doc='')  # validator=om.validate_choices(),
    selection = om.attr_def(type=str, default='tournament', doc='')   # validator=om.validate_choices(),
    # SGA #####

    # NLOPT #####
    nlopt_solver = om.attr_def(type=str, default='neldermead', doc='')    # validator=om.validate_choices(),  todo
    maxtime = om.attr_def(type=int, default=0, doc='')                     # validator=om.validate_range(),  todo
    maxeval = om.attr_def(type=int, default=0, doc='')
    xtol_rel = om.attr_def(type=float, default=1.e-8, doc='')
    xtol_abs = om.attr_def(type=float, default=0., doc='')
    ftol_rel = om.attr_def(type=float, default=0., doc='')
    ftol_abs = om.attr_def(type=float, default=0., doc='')
    stopval = om.attr_def(type=float, default=float('-inf'), doc='')
    local_optimizer = om.attr_def(type=None, default=None, doc='')          # validator=om.validate_choices(),  todo
    replacement = om.attr_def(type=str, default='best', doc='')
    nlopt_selection = om.attr_def(type=str, default='best', doc='')         # todo: "selection" - same name as in SGA
    # NLOPT #####

    def get_algorithm(self):
        """TBW.

        :return:
        """
        if self.type == 'sade':
            opt_algorithm = pg.sade(gen=self.generations,
                                    variant=self.variant,
                                    variant_adptv=self.variant_adptv,
                                    ftol=self.ftol,
                                    xtol=self.xtol,
                                    memory=self.memory)
        elif self.type == 'sga':
            opt_algorithm = pg.sga(gen=self.generations,
                                   cr=self.cr,  # crossover probability
                                   crossover=self.crossover,  # single, exponential, binomial, sbx
                                   m=self.m,  # mutation probability
                                   mutation=self.mutation,  # uniform, gaussian, polynomial
                                   param_s=self.param_s,  # number of best ind. in 'truncated'/tournament
                                   selection=self.selection,  # tournament, truncated
                                   eta_c=self.eta_c,  # distribution index for sbx crossover
                                   param_m=self.param_m)  # mutation parameter
        elif self.type == 'nlopt':
            opt_algorithm = pg.nlopt(self.nlopt_solver)
            opt_algorithm.maxtime = self.maxtime  # stop when the optimization time (in seconds) exceeds maxtime
            opt_algorithm.maxeval = self.maxeval  # stop when the number of function evaluations exceeds maxeval
            opt_algorithm.xtol_rel = self.xtol_rel  # relative stopping criterion for x
            opt_algorithm.xtol_abs = self.xtol_abs  # absolute stopping criterion for x
            opt_algorithm.ftol_rel = self.ftol_rel
            opt_algorithm.ftol_abs = self.ftol_abs
            opt_algorithm.stopval = self.stopval
            opt_algorithm.local_optimizer = self.local_optimizer
            opt_algorithm.replacement = self.replacement
            opt_algorithm.selection = self.nlopt_selection
        else:
            raise NotImplementedError

        return opt_algorithm


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
    output_type = om.attr_def(
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
    fitness_function = om.attr_def(
        type=str,
        default='',
        doc=''
    )
    algorithm = om.attr_def(
        type=str,
        default='',
        doc=''
    )
    seed = om.attr_def(
        type=int,
        validator=om.validate_range(0, 100000),
        default=np.random.randint(0, 100000),
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
    weighting_path = om.attr_def(
        type=list,
        # validator=
        default=None,
        doc=''
    )
    champions_file = om.attr_def(
        type=str,
        default='data/calibration_champions.out',
        doc=''
    )
    population_file = om.attr_def(
        type=str,
        default=None,
        doc=''
    )

    def run_calibration(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        pg.set_global_rng_seed(seed=self.seed)
        print('pygmo seed: ', self.seed)

        fitting = ModelFitting(processor)

        target_output = read_data(self.target_data_path)
        if self.weighting_path:
            weighting = read_data(self.weighting_path)[0]
        else:
            weighting = None

        fitting.set_parameters(calibration_mode=self.calibration_mode,
                               model_names=self.model_names,
                               variables=self.variables,
                               var_log=self.var_log,
                               generations=self.algorithm.generations,
                               population_size=self.algorithm.population_size,
                               simulation_output=self.output_type,
                               sort_by_var=self.sort_var,
                               fitness_func=self.fitness_function,
                               champions_file=self.champions_file,
                               population_file=self.population_file)
        fitting.configure(params_per_variable=self.params_per_variable,
                          target_output_list=target_output,
                          target_fit_range=self.target_fit_range,
                          out_fit_range=self.output_fit_range,
                          weighting=weighting)
        fitting.set_bound(low_val=self.lower_boundary,
                          up_val=self.upper_boundary)

        prob = pg.problem(fitting)
        print('evolution started ...')

        opt_algorithm = self.algorithm.get_algorithm()
        algo = pg.algorithm(opt_algorithm)

        pop = pg.population(prob, size=self.algorithm.population_size)
        pop = algo.evolve(pop)

        champion_f = pop.champion_f
        champion_x = fitting.split_and_update_parameter(pop.champion_x)
        print('\nchampion_f:   %1.5e' % champion_f[0])
        print('champion_x: ', *champion_x, sep="\n")

        return 1        # todo: return results as output!!
