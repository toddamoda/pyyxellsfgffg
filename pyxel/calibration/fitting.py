"""CDM model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import numpy as np
import pandas as pd
from typing import List  # noqa: F401


class ModelFitting:
    """Pygmo problem class to fit data with any model in Pyxel."""

    def __init__(self, detector, pipeline):
        """TBW."""
        self.name = "model fitting"

        self.det = detector
        self.pipe = pipeline

        self.model_name_list = []           # type: List[str]
        self.params_per_variable = []          # type: List[List[int]]

        self.variable_name_lst = []         # type: List[List[str]]
        self.is_var_array = []              # type: List[List[bool]]
        self.is_var_log = []                # type: List[List[bool]]

        self.gen = None
        self.pop = None
        self.fullframe = None
        self.target_data = None

        self.datasets = None

        self.n = 0
        self.g = 0

        self.sort_by_var_name = None

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

    def configure(self,
                  model_names,
                  params_per_variable,
                  variables,
                  var_arrays,
                  var_log,
                  model_input,
                  target_output,
                  generations,
                  population_size,
                  target_fit_range,
                  out_fit_range
                  ):
        """TBW.

        :param model_names: list
        :param params_per_variable: list
        :param variables: list
        :param var_arrays: list
        :param var_log: list
        :param model_input: list
        :param target_output: list
        :param generations: int
        :param population_size: int
        :param target_fit_range: slice
        :param out_fit_range: slice
        :return:
        """
        self.model_name_list = model_names
        self.params_per_variable = params_per_variable

        self.variable_name_lst = variables
        self.is_var_array = var_arrays
        self.is_var_log = var_log

        self.gen = generations
        self.pop = population_size

        self.fullframe = model_input
        self.target_data = target_output
        self.datasets = len(target_output)

        if (target_fit_range[1] - target_fit_range[0]) == (out_fit_range[1] - out_fit_range[0]):
            self.targ_fit_range = slice(target_fit_range[0], target_fit_range[1])
            self.sim_fit_range = slice(out_fit_range[0], out_fit_range[1])
        else:
            raise AttributeError('Fitting ranges have different lengths')

        self.sort_by_var_name = self.variable_name_lst[0][0]  # todo
        self.champion_f_list = np.zeros((1, 1))
        self.champion_x_list = np.zeros((1, np.sum(np.sum(self.params_per_variable))))

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

    # def set_fit_ranges(self, target_range, out_range):
    #     """TBW.
    #
    #     :param target_range: slice
    #     :param out_range: slice
    #     :return:
    #     """
    #     self.targ_fit_range = target_range
    #     self.sim_fit_range = out_range

    def set_bound(self, low_val, up_val):
        """TBW.

        :param low_val: list
        :param up_val: list
        :return:
        """
        self.lbd = []
        self.ubd = []
        for i in range(len(low_val)):
            for j in range(len(up_val[i])):
                if self.is_var_log[i][j]:
                    lo_bd, up_bd = [np.log10(low_val[i][j])], [np.log10(up_val[i][j])]
                else:
                    lo_bd, up_bd = [low_val[i][j]], [up_val[i][j]]
                if self.is_var_array[i][j]:
                    lo_bd = self.params_per_variable[i][j] * lo_bd
                    up_bd = self.params_per_variable[i][j] * up_bd
                self.lbd += lo_bd
                self.ubd += up_bd

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
        parameter_lst = self.split_and_update(parameter)

        # # If we want to optimize detector properties and not model arguments:
        # self.update_detector_object(parameter_lst)                        # TODO not a priority
        # # If we want to optimize model arguments:
        self.update_pipeline_object(parameter_lst)

        self.det = self.pipe.run_pipeline(self.det)

        overall_fitness = 0.
        # overall_fitness = self.calculate_least_squares(self.det)          # TODO update

        self.population_and_champions(parameter_lst, overall_fitness)

        print('minden fasza')

        return [overall_fitness]

    def split_and_update(self, parameter):
        """TBW.

        :param parameter: 1d np.array
        :return:
        """
        split_list = []
        for i in range(len(self.params_per_variable)):
            for j in range(len(self.params_per_variable[i])):
                if i == 0 and j == 0:
                    split_list += [self.params_per_variable[0][0]]
                else:
                    split_list += [split_list[j-1] + self.params_per_variable[i][j]]

        subarrays = np.split(parameter, split_list)
        subarrays = subarrays[:-1]

        k = 0
        for i in range(len(self.variable_name_lst)):
            for j in range(len(self.variable_name_lst[i])):
                if self.is_var_log[i][j]:
                    subarrays[k] = np.power(10, subarrays[k])
                if not self.is_var_array[i][j]:
                    subarrays[k] = subarrays[k][0]
                k += 1

        return subarrays

    def update_pipeline_object(self, param_array_list):
        """TBW.

        :param param_array_list:
        :return:
        """
        k = 0
        for i in range(len(self.variable_name_lst)):
            fitted_pipeline_model = self.pipe.get_model(self.model_name_list[i])

            for j in range(len(self.variable_name_lst[i])):
                fitted_pipeline_model.arguments[self.variable_name_lst[i][j]] = param_array_list[k]
                k += 1

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

        df = pd.DataFrame()
        k = 0
        for i in range(len(self.variable_name_lst)):
            for j in range(len(self.variable_name_lst[i])):
                df[self.variable_name_lst[i][j]] = parameter[k]
                k += 1

        ordered_df = df.sort_values(by=[self.sort_by_var_name])

        ord_param = np.array([])
        for i in range(len(self.is_var_array)):
            for j in range(len(self.is_var_array[i])):
                if self.is_var_array[i][j]:
                    ord_param = np.append(ord_param, ordered_df[self.variable_name_lst[i][j]].values)
                else:
                    ord_param = np.append(ord_param,
                                          np.unique(ordered_df[self.variable_name_lst[i][j]].values))

        paramsize = len(ord_param)
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
