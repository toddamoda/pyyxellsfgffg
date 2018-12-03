"""CDM model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import numpy as np
from copy import deepcopy
import typing as t   # noqa: F401

from pyxel.pipelines.model_group import ModelFunction


class ModelFitting:
    """Pygmo problem class to fit data with any model in Pyxel."""

    # def __init__(self, detector, pipeline):
    def __init__(self, processor):
        """TBW."""
        self.calibration_mode = None

        self.det = processor.detector
        self.pipe = processor.pipeline

        self.model_name_list = []           # type: t.List[str]
        self.params_per_variable = []       # type: t.List[t.List[int]]
        self.variable_name_lst = []         # type: t.List[t.List[str]]
        self.is_var_array = []              # type: t.List[t.List[int]]
        self.is_var_log = []                # type: t.List[t.List[bool]]

        # self.det_attr_class_list = []     # ['characteristics', 'geometry']  # todo

        self.generations = None
        self.pop = None

        self.all_target_data = []
        self.target_data = None

        # self.normalization = False
        # self.target_data_norm = []
        self.weighting = False
        self.weighting_function = None

        self.fitness_mode = None
        self.sim_output = None

        self.n = 0
        self.g = 0

        self.sort_by_var = None

        self.write2file = False
        self.champion_file = None
        self.pop_file = None

        self.fitness_array = None
        self.population = None
        self.champion_f_list = None
        self.champion_x_list = None

        self.lbd = None         # lower boundary
        self.ubd = None         # upper boundary

        self.sim_fit_range = None
        self.targ_fit_range = None

    def get_bounds(self):
        """TBW.

        :return:
        """
        return self.lbd, self.ubd

    def set_generations(self, gen):
        """TBW.

        :return:
        """
        self.generations = gen

    def configure(self,
                  calibration_mode: str,
                  model_names: list,
                  params_per_variable: list,
                  variables: list,
                  var_log: list,
                  target_output_list,
                  population_size: int = None,
                  target_fit_range=None,        # t.Optional[list]      # todo
                  out_fit_range=None,           # t.Union[list, None]   # todo
                  fitness_mode: str = 'residuals',
                  simulation_output: str = 'image',
                  sort_by_var: str = None
                  ):
        """TBW.

        :param calibration_mode: str
        :param model_names: list
        :param params_per_variable: list
        :param variables: list
        :param var_log: list
        :param target_output_list: list
        :param population_size: int
        :param target_fit_range:
        :param out_fit_range:
        :param fitness_mode: str
        :param simulation_output: str
        :param sort_by_var: str
        :return:
        """
        self.calibration_mode = calibration_mode
        self.model_name_list = model_names
        self.params_per_variable = params_per_variable

        self.is_var_array = deepcopy(self.params_per_variable)
        for i in range(len(self.params_per_variable)):
            for j in range(len(self.params_per_variable[i])):
                item = self.params_per_variable[i][j]
                if item > 1:
                    item = 1
                else:
                    item = 0
                self.is_var_array[i][j] = item

        self.variable_name_lst = variables
        self.is_var_log = var_log

        # self.det_attr_class_list = model_names      # ['characteristics.amp', 'geometry.row']  # TODO

        self.pop = population_size

        self.target_data = target_output_list[0]
        cols = None
        try:
            rows, cols = self.target_data.shape
        except AttributeError:
            rows = len(self.target_data)

        self.fitness_mode = fitness_mode
        self.sim_output = simulation_output

        self.sort_by_var = sort_by_var

        if target_fit_range is None:
            self.targ_fit_range = slice(None)
        else:
            if len(target_fit_range) == 2:
                self.targ_fit_range = slice(target_fit_range[0], target_fit_range[1])
            elif len(target_fit_range) == 4:
                self.targ_fit_range = (slice(target_fit_range[0], target_fit_range[1]),
                                       slice(target_fit_range[2], target_fit_range[3]))
            else:
                raise AttributeError('Fitting range should have 2 or 4 values')

        if out_fit_range is None:
            self.sim_fit_range = slice(None)
        else:
            if len(out_fit_range) == 2:
                self.sim_fit_range = slice(out_fit_range[0], out_fit_range[1])
            elif len(out_fit_range) == 4:
                self.sim_fit_range = (slice(out_fit_range[0], out_fit_range[1]),
                                      slice(out_fit_range[2], out_fit_range[3]))
            else:
                raise AttributeError('Fitting range should have 2 or 4 values')

        if target_fit_range and out_fit_range:
            if (target_fit_range[1] - target_fit_range[0]) != (out_fit_range[1] - out_fit_range[0]):
                raise AttributeError('Fitting ranges have different lengths in 1st dimension')
            if len(target_fit_range) == 4 and len(out_fit_range) == 4:
                if (target_fit_range[3] - target_fit_range[2]) != (out_fit_range[3] - out_fit_range[2]):
                    raise AttributeError('Fitting ranges have different lengths in 2nd dimension')

        if target_fit_range[0] < 0 or target_fit_range[0] > rows:
            raise ValueError('Value of fitting range is wrong')
        if target_fit_range[1] < 0 or target_fit_range[1] > rows:
            raise ValueError('Value of fitting range is wrong')
        if len(target_fit_range) > 2:
            if target_fit_range[2] < 0 or target_fit_range[2] > cols:
                raise ValueError('Value of fitting range is wrong')
            if target_fit_range[3] < 0 or target_fit_range[3] > cols:
                raise ValueError('Value of fitting range is wrong')

        self.target_data = self.target_data[self.targ_fit_range]
        for target in target_output_list:
            self.all_target_data += [target[self.targ_fit_range]]

        self.champion_f_list = np.zeros((1, 1))
        self.champion_x_list = np.zeros((1, np.sum(np.sum(self.params_per_variable))))

    # def set_normalization(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     self.normalization = True
    #     for i in range(len(self.target_data)):
    #         self.target_data_norm += [self.normalize(self.target_data[i], dataset=i)]

    def set_weighting_function(self, func):
        """TBW.

        :param func: 1d or 2d np.array
        :return:
        """
        self.weighting = True
        self.weighting_function = func[self.targ_fit_range]

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
        self.champion_file = 'data/calibration_champions.out'
        f1 = open(self.champion_file, 'wb')  # truncate output file
        f1.close()
        self.pop_file = 'data/calibration_populations.out'
        f2 = open(self.pop_file, 'wb')       # truncate output file
        f2.close()
        # filelist = glob.glob('champion_id*.out')
        # for file in filelist:
        #     os.remove(file)

    def calculate_fitness(self, simulated_data, target_data):
        """TBW.

        :param simulated_data:
        :param target_data:
        :return:
        """
        if self.fitness_mode == 'residuals':
            fitness = self.sum_of_abs_residuals(simulated=simulated_data,
                                                target=target_data)

        elif self.fitness_mode == 'least-squares':
            fitness = self.sum_of_squared_residuals(simulated=simulated_data,
                                                    target=target_data)

        elif self.fitness_mode == 'custom':
            custom_fitness_func = ModelFunction(name='test_func',       # TODO finish and test
                                                func='func',
                                                arguments=None,
                                                enabled=True)

            fitness = custom_fitness_func.function()   # simulated_data, target_data, self.det

        else:
            raise ValueError

        return fitness

    def sum_of_abs_residuals(self, simulated, target):
        """TBW.

        :param simulated:
        :param target:
        :return:
        """
        diff = target - simulated
        if self.weighting:
            diff *= self.weighting_function
        return np.sum(np.abs(diff))

    def sum_of_squared_residuals(self, simulated, target):
        """TBW.

        :param simulated:
        :param target:
        :return:
        """
        diff = target - simulated
        diff_square = diff * diff
        if self.weighting:
            diff_square *= self.weighting_function
        return np.sum(diff_square)

    # def least_squares(self, simulated_data, dataset=None):
    #     """TBW.
    #
    #     :param simulated_data:
    #     :param dataset: int
    #     :return:
    #     """
    #     input_array = simulated_data[self.sim_fit_range]
    #
    #     if dataset is not None:
    #         if self.normalization:
    #             input_array = self.normalize(input_array, dataset=dataset)
    #             target = self.target_data_norm[dataset][self.targ_fit_range]
    #         else:
    #             target = self.target_data[dataset][self.targ_fit_range]
    #     else:
    #         if self.normalization:
    #             input_array = self.normalize(input_array)
    #             target = self.target_data_norm[self.targ_fit_range]
    #         else:
    #             target = self.target_data[self.targ_fit_range]
    #
    #     diff = target - input_array
    #     diff_square = diff * diff
    #
    #     if self.weighting:
    #         diff_square *= self.weighting_function
    #
    #     return np.sum(diff_square)

    # def normalize(self, array, dataset):
    #     """Normalize dataset arrays by injected signal maximum.
    #
    #     :param array: 1d np.array
    #     :param dataset: int
    #     :return:
    #     """
    #     return array / np.average(self.target_data[dataset][self.targ_fit_range])

    def fitness(self, parameter):
        """Call the fitness function, elements of parameter array could be logarithm values.

        :param parameter: 1d np.array
        :return:
        """
        parameter_lst = self.split_and_update_parameter(parameter)

        self.update_detector_and_models(parameter_lst)

        if self.calibration_mode == 'pipeline':
            new_det = self.pipe.run_pipeline(self.det)
        elif self.calibration_mode == 'single_model':
            raise NotImplementedError
            # ###############################
            # fitted_model = self.pipe.get_model(self.model_name_list[0])
            # self.det.pixels.pixel_array = np.array([[100., 100.], [100., 100.]])              # TODO input of model
            # new_det = fitted_model.function(self.det)
            # new_det.image = new_det.pixels.pixel_array                                        # TODO output of model
            # ###############################
        else:
            raise ValueError

        if self.sim_output == 'image':
            simulated_data = new_det.image.array
        elif self.sim_output == 'signal':
            simulated_data = new_det.signal.array
        elif self.sim_output == 'charge':
            raise NotImplementedError       # todo: new_det.charge.array
        else:
            raise ValueError
        simulated_data = simulated_data[self.sim_fit_range]

        overall_fitness = 0
        for target_data in self.all_target_data:
            overall_fitness += self.calculate_fitness(simulated_data, target_data)

        # print('fitness: %1.5e' % overall_fitness)
        if self.write2file:
            self.population_and_champions(parameter_lst, overall_fitness)

        return [overall_fitness]

    def split_and_update_parameter(self, parameter):
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
                    split_list += [split_list[-1] + self.params_per_variable[i][j]]

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

    def update_detector_and_models(self, param_array_list):
        """TBW.

        :param param_array_list:
        :return:
        """
        self.det.reinitialize()

        k = 0
        for i in range(len(self.model_name_list)):
            if self.model_name_list[i] in ['geometry', 'material', 'environment', 'characteristics']:
                class_str = self.model_name_list[i]
                det_class = getattr(self.det, class_str)
                for j in range(len(self.variable_name_lst[i])):
                    setattr(det_class, self.variable_name_lst[i][j], param_array_list[k])
                    k += 1
            else:
                fitted_pipeline_model = self.pipe.get_model(self.model_name_list[i])
                for j in range(len(self.variable_name_lst[i])):
                    fitted_pipeline_model.arguments[self.variable_name_lst[i][j]] = param_array_list[k]
                    k += 1

    def population_and_champions(self, parameter, overall_fitness):
        """Get champion (also population) of each generation and write it to output file(s).

        :param parameter: 1d np.array
        :param overall_fitness: list
        :return:
        """
        # if self.champion_file is None:
        #     self.champion_file = 'champion_id' + str(id(self)) + '.out'

        # df = pd.DataFrame()       # TODO fill df only with cdm param and sort only them not other params
        # k = 0
        # for i in range(len(self.variable_name_lst)):
        #     for j in range(len(self.variable_name_lst[i])):
        #         df[self.variable_name_lst[i][j]] = parameter[k]
        #         k += 1
        #
        # if self.sort_by_var:
        #     df = df.sort_values(by=[self.sort_by_var])
        #
        # ord_param = np.array([])
        # for i in range(len(self.is_var_array)):
        #     for j in range(len(self.is_var_array[i])):
        #         if self.is_var_array[i][j]:
        #             ord_param = np.append(ord_param, df[self.variable_name_lst[i][j]].values)
        #         else:
        #             ord_param = np.append(ord_param,
        #                                   np.unique(df[self.variable_name_lst[i][j]].values))

        ord_param = np.array([])
        for p in parameter:
            ord_param = np.append(ord_param, p)     # todo: not yet ordered
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

            print('champion\'s fitness: %1.5e' % self.champion_f_list[self.g])

            str_format = '%d' + (paramsize + 1) * ' %.6E'
            with open(self.champion_file, 'ab') as f3:
                np.savetxt(f3, np.c_[np.array([self.g]),
                                     self.champion_f_list[self.g],
                                     self.champion_x_list[self.g, :].reshape(1, paramsize)],
                           fmt=str_format)

            if self.g % 100 == 0 or self.g == self.generations:
                str_format = '%d' + (paramsize + 1) * ' %.6E'
                with open(self.pop_file, 'ab') as f4:
                    np.savetxt(f4, np.c_[self.g * np.ones(self.fitness_array.shape),
                                         self.fitness_array,
                                         self.population], fmt=str_format)

            self.g += 1

        self.n += 1
