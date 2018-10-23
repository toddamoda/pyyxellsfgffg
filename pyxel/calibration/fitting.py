"""CDM model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import numpy as np
import pandas as pd
from typing import List  # noqa: F401


class ModelFitting:
    """Pygmo problem class to fit data with any model in Pyxel."""

    def __init__(self, detector, pipeline):
        """TBW.

        # :param input_data: np.array
        # :param target: np.array
        # :param variables: list of str, like ['tr_p', 'nt_p', 'beta_p'] or ['tr_p', 'nt_p', 'sigma_p', 'beta_p']
        """
        self.name = "model fitting"

        self.det = detector
        self.pipe = pipeline

        self.variable_name_lst = []     # type:  List[str]
        self.is_var_array = []          # type:  List[bool]
        self.is_var_log = []            # type:  List[bool]

        self.gen = None
        self.pop = None
        self.fullframe = None
        self.target_data = None

        self.datasets = None

        self.n = 0
        self.g = 0

        self.write2file = False
        self.champion_file = None
        self.pop_file = None

        self.pop_obj = None

        self.fitness_array = None
        self.population = None
        self.champion_f_list = None
        self.champion_x_list = None

        self.lbd = None         # lower boundary
        self.ubd = None         # upper boundary

        self.chg_inj = None

        self.para_transfers = None
        self.seri_transfers = None

        self.sim_fit_range = None
        self.targ_fit_range = None
        # self.sim_fit_range = slice(0, len(target[0]))
        # self.targ_fit_range = slice(0, len(target[0]))  # these two should have the same length!

        self.normalization = False
        self.target_data_norm = []

        self.weighting = False
        self.weighting_function = None

        # self.tr_log = False
        # self.nt_log = False
        # self.sigma_log = False
        # self.beta_log = False

        self.traps = None
        self.t = None           # parallel transfer period (s)
        self.fwc = None         # full well capacity in e-
        self.vg = None          # HALF of the pixel geometrical volume and max volume of e- cloud (cm**3)
        self.vth = None         # thermal velocity of e- (cm/s)

        self.tr_p = None
        self.nt_p = None
        self.sigma_p = None
        self.beta_p = None

        self.dob = 0.           # diffuse optical background

        self.st = 0.9828e-3
        self.sfwc = 900000.
        self.svg = 1.4e-10
        self.beta_s = 0.3
        self.sigma_s = np.array([1.])
        self.tr_s = np.array([0.03])
        self.nt_s = np.array([10.])                     # traps / pixel

    def get_bounds(self):
        """TBW.

        :return:
        """
        return self.lbd, self.ubd

    def get_name(self):
        """TBW.

        :return:
        """
        return self.name

    def set_data(self,
                 model_input,
                 target_output,
                 variables,
                 var_arrays,
                 var_log,
                 generations,
                 population_size):
        """TBW.

        :param model_input:
        :param target_output:
        :param variables:
        :param var_arrays:
        :param var_log:
        :param generations:
        :param population_size:
        :return:
        """
        self.variable_name_lst = variables
        self.is_var_array = var_arrays
        self.is_var_log = var_log

        self.gen = generations
        self.pop = population_size

        self.fullframe = model_input
        self.target_data = target_output
        self.datasets = len(target_output)

    def set_normalization(self):
        """TBW.

        :return:
        """
        self.normalization = True
        for i in range(len(self.target_data)):
            self.target_data_norm += [self.normalize(self.target_data[i], dataset=i)]

    def set_weighting_function(self, func):
        """TBW.

        :param func: 1d np.array
        :return:
        """
        self.weighting = True
        self.weighting_function = func.reshape(len(func), 1)

    # def set_uniformity_scales(self, sc_tr='lin', sc_nt='lin', sc_sig='lin', sc_be='lin'):
    #     """TBW.
    #
    #     :param sc_tr:
    #     :param sc_nt:
    #     :param sc_sig:
    #     :param sc_be:
    #     :return:
    #     """
    #     if sc_tr == 'log':
    #         self.tr_log = True
    #     if sc_nt == 'log':
    #         self.nt_log = True
    #     if sc_sig == 'log':
    #         self.sigma_log = True
    #     if sc_be == 'log':
    #         self.beta_log = True

    def set_simulated_fit_range(self, fit_range):
        """TBW.

        :param fit_range: tuple
        :return:
        """
        self.sim_fit_range = slice(fit_range[0], fit_range[1])

    def set_target_fit_range(self, fit_range):
        """TBW.

        :param fit_range: tuple
        :return:
        """
        self.targ_fit_range = slice(fit_range[0], fit_range[1])

    def set_bound(self, low_val, up_val):
        """TBW.

        :param low_val: np.array
        :param up_val: np.array
        :return:
        """
        self.lbd = low_val
        self.ubd = up_val

    def save_champions_in_file(self):
        """TBW.

        :return:
        """
        self.write2file = True
        self.champion_file = 'champion.out'
        f1 = open(self.champion_file, 'wb')  # truncate output file
        f1.close()
        self.pop_file = 'population.out'
        f2 = open(self.pop_file, 'wb')  # truncate output file
        f2.close()

        # filelist = glob.glob('champion_id*.out')
        # for file in filelist:
        #     os.remove(file)

    def charge_injection(self, flag: bool):
        """TBW.

        :param flag:
        :return:
        """
        self.chg_inj = flag

    def set_parallel_parameters(self,
                                traps: int,
                                t: float,
                                vg: float,
                                fwc: float,
                                vth: float,
                                sigma: float):
        """TBW.

        :param traps: number of trap species
        :param t: parallel transfer period (s)
        :param vg: HALF of the pixel geometrical volume and max volume of e- cloud (cm**3)
        :param fwc: full well capacity of pixels in e-
        :param vth: thermal velocity of e- (cm/s)
        :param sigma: capture cross-section for all traps (cm**2)
        :return:
        """
        self.traps = traps
        self.t = t
        self.vg = vg
        self.fwc = fwc
        self.vth = vth
        if isinstance(sigma, float) or isinstance(sigma, int):
            self.sigma_p = sigma * np.ones(self.traps)
        else:
            self.sigma_p = sigma
        self.champion_f_list = np.zeros((1, 1))
        self.champion_x_list = np.zeros((1, 3 * self.traps + 1))

    def set_dimensions(self,
                       para_transfers: int = None,
                       seri_transfers: int = None):
        """TBW.

        :param para_transfers:
        :param seri_transfers:
        :return:
        """
        self.para_transfers = para_transfers
        self.seri_transfers = seri_transfers

    def calculate_least_squares(self, simulated_data, dataset):
        """TBW.

        :param simulated_data: 2d np.array
        :param dataset: int
        :return:
        """
        input_array = simulated_data[self.sim_fit_range]

        if self.normalization:
            input_array = self.normalize(input_array, dataset=dataset)
            target = self.target_data_norm[dataset][self.targ_fit_range]
        else:
            target = self.target_data[dataset][self.targ_fit_range]

        diff = target - input_array
        diff_square = diff * diff

        if self.weighting:
            diff_square *= self.weighting_function

        return np.sum(diff_square)

    def normalize(self, array, dataset):
        """Normalize dataset arrays by injected signal maximum.

        :param array: 1d np.array
        :param dataset: int
        :return:
        """
        return array / np.average(self.target_data[dataset][self.targ_fit_range])

    def fitness(self, parameter):
        """Call the fitness function, elements of parameter array could be logarithm values.

        :param parameter: 1d np.array
        :return:
        """
        parameter_lst = self.update_parameter(parameter)

        # self.add_model_inputs_to_detector_object(self.fullframe)        # TODO not a priority

        # If we want to optimize detector properties and not model arguments
        # self.update_detector_object(parameter_lst)                        # TODO not a priority

        # If we want to optimize model arguments
        model_name_lst = ['cdm']   # ['tars', 'cdm']                        # TODO get this from yaml
        self.update_pipeline_object(parameter_lst, model_name_lst)

        self.det = self.pipe.run_pipeline(self.det)

        overall_fitness = 0.
        # overall_fitness = self.calculate_least_squares(self.det)         # TODO update

        # self.population_and_champions(parameter_lst, overall_fitness)     # TODO update to use parameter_lst

        print('minden fasza')

        return [overall_fitness]

    def split_parameter(self, parameter):
        """TBW.

        :param parameter: 1d np.array
        :return:
        """
        nn = len(self.variable_name_lst)

        # ####### This parameter splitting, grouping is MODEL-SPECIFIC !!!  # TODO
        if nn == 2:
            subarrays = np.split(parameter, [self.traps, 2 * self.traps])
        elif nn == 3:
            subarrays = np.split(parameter, [self.traps, 2 * self.traps, 2 * self.traps + 1])
        elif nn == 4:
            subarrays = np.split(parameter, [self.traps, 2 * self.traps, 3 * self.traps, 3 * self.traps + 1])
        else:
            subarrays = None
        # #######

        return subarrays[:-1]

    def update_parameter(self, parameter):
        """Update elements of parameter array, if they are logarithmic values.

        :param parameter: 1d np.array
        :return:
        """
        subarrays = self.split_parameter(parameter)

        nn = len(self.variable_name_lst)
        for i in range(nn):
            if self.is_var_log[i]:
                subarrays[i] = np.power(10, subarrays[i])
            if not self.is_var_array[i]:
                subarrays[i] = subarrays[i][0]

        return subarrays

    def update_pipeline_object(self, param_grp_list, model_name_list):
        """TBW.

        :param param_grp_list:
        :param model_name_list:
        :return:
        """
        if len(model_name_list) > 1:
            raise NotImplementedError

        for model_name in model_name_list:
            fitted_pipeline_model = self.pipe.get_model(model_name)
            nn = len(self.variable_name_lst)                        # TODO how many parameter groups this model has ???
            for i in range(nn):
                fitted_pipeline_model.arguments[self.variable_name_lst[i]] = param_grp_list[i]

        # # VALIDATION - just for the first time before running calibration
        # nn = len(self.variable_name_lst)
        # for i in range(nn):
        #     arg_value = fitted_pipeline_model.arguments[self.variable_name_lst[i]]
        #     if str(arg_value) != '_':
        #         raise AttributeError

        # ###############################
        # fitted_model = self.pipe.get_model('cdm')
        # asd = fitted_model.func
        # csd = fitted_model.function
        # out = fitted_model.function(self.det) # not working yet
        # ize = self.pipe.model_groups
        # ize2 = self.pipe.model_group_names
        # ###############################

    def population_and_champions(self, parameter, overall_fitness):
        """Get champion (also population) of each generation and write it to output file(s).

        :param parameter: 1d np.array
        :param overall_fitness: list
        :return:
        """
        # if self.champion_file is None:
        #     self.champion_file = 'champion_id' + str(id(self)) + '.out'

        paramsize = len(parameter)
        ord_param = None
        if paramsize == (2 * self.traps + 1):
            ordered_parameter = pd.DataFrame(np.c_[parameter[0:self.traps],
                                                   parameter[self.traps:2 * self.traps]],
                                             columns=['time',
                                                      'density'])
            ordered_parameter = ordered_parameter.sort_values(by=['time'])
            ord_param = np.append(np.array([]), ordered_parameter.time.values)
            ord_param = np.append(ord_param, ordered_parameter.density.values)

        elif paramsize == (3 * self.traps + 1):
            ordered_parameter = pd.DataFrame(np.c_[parameter[0:self.traps],
                                                   parameter[self.traps:2 * self.traps],
                                                   parameter[2 * self.traps:3 * self.traps]],
                                             columns=['time',
                                                      'density',
                                                      'sigma'])
            ordered_parameter = ordered_parameter.sort_values(by=['time'])
            ord_param = np.append(np.array([]), ordered_parameter.time.values)
            ord_param = np.append(ord_param, ordered_parameter.density.values)
            ord_param = np.append(ord_param, ordered_parameter.sigma.values)

        ord_param = np.append(ord_param, parameter[-1])
        ord_param = ord_param.reshape(1, paramsize)

        if self.n % self.pop == 0:
            self.fitness_array = np.array([overall_fitness])
            self.population = ord_param
        else:
            self.fitness_array = np.vstack((self.fitness_array, np.array([overall_fitness])))
            self.population = np.vstack((self.population, ord_param))

        if (self.n + 1) % self.pop == 0:

            best_index = np.argmin(self.fitness_array)

            if self.g == 0:
                self.champion_f_list[self.g] = self.fitness_array[best_index]
                self.champion_x_list[self.g] = self.population[best_index, :]
            else:
                best_champ_index = np.argmin(self.champion_f_list)

                if self.fitness_array[best_index] <= self.champion_f_list[best_champ_index]:
                    self.champion_f_list = np.vstack((self.champion_f_list, self.fitness_array[best_index]))
                    self.champion_x_list = np.vstack((self.champion_x_list, self.population[best_index]))
                else:
                    self.champion_f_list = np.vstack((self.champion_f_list, self.champion_f_list[-1]))
                    self.champion_x_list = np.vstack((self.champion_x_list, self.champion_x_list[-1]))

            if self.write2file:
                str_format = '%d' + (paramsize + 1) * ' %.6E'
                with open(self.champion_file, 'ab') as f3:
                    np.savetxt(f3, np.c_[np.array([self.g]),
                                         self.champion_f_list[self.g],
                                         self.champion_x_list[self.g, :].reshape(1, paramsize)],
                               fmt=str_format)

                if self.g % 200 == 0 or self.g == self.gen:
                    str_format = '%d' + (paramsize + 1) * ' %.6E'
                    with open(self.pop_file, 'ab') as f4:
                        np.savetxt(f4, np.c_[self.g * np.ones(self.fitness_array.shape),
                                             self.fitness_array,
                                             self.population], fmt=str_format)

            self.g += 1

        self.n += 1
