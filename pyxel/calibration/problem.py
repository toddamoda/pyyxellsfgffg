"""CDM model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import numpy as np
import pandas as pd
# from pyxel.models.cdm.CDM import cdm


class ModelFitting:
    """Pygmo problem class to fit data with any model in Pyxel."""

    def __init__(self, detector, pipeline):
                 # variables, gen, pop,     # ##### detector, pipeline,
                 # input_data, target           # todo get rid of these
                 # ):
        """TBW.

        # :param input_data: np.array
        # :param target: np.array
        # :param variables: list of str, like ['tr_p', 'nt_p', 'beta_p'] or ['tr_p', 'nt_p', 'sigma_p', 'beta_p']
        """
        self.det = detector
        self.pipe = pipeline
        self.lbd = [0]
        self.ubd = [1]

    def get_bounds(self):
        """TBW.
        :return:
        """
        return self.lbd, self.ubd

    def fitness(self, parameter):
        """Call the fitness function, elements of parameter array could be logarithm values.

        :param parameter: 1d np.array
        :return:
        """
        print('fitness')
        output_detector = self.pipe.run_pipeline(self.det)
        return [0.5]
    #
    #     # self.variables = variables
    #     # self.gen = gen
    #     # self.pop = pop
    #     # self.fullframe = input_data
    #     # self.target_data = target
    #     # self.datasets = len(target)
    #
    #     self.n = 0
    #     self.g = 0
    #
    #     self.write2file = False
    #     self.champion_file = None
    #     self.pop_file = None
    #
    #     self.pop_obj = None
    #
    #     self.fitness_array = None
    #     self.population = None
    #     self.champion_f_list = None
    #     self.champion_x_list = None
    #
    #     self.lbd = None         # lower boundary
    #     self.ubd = None         # upper boundary
    #
    #     self.chg_inj = None
    #
    #     self.para_transfers = None
    #     self.seri_transfers = None
    #
    #     self.normalization = False
    #     self.target_data_norm = []
    #
    #     self.weighting = False
    #     self.weighting_function = None
    #
    #     # self.sim_fit_range = slice(0, len(target[0]))
    #     # self.targ_fit_range = slice(0, len(target[0]))  # these two should have the same length!
    #
    #     self.tr_log = False
    #     self.nt_log = False
    #     self.sigma_log = False
    #     self.beta_log = False
    #
    #     self.traps = None
    #     self.t = None           # parallel transfer period (s)
    #     self.fwc = None         # full well capacity in e-
    #     self.vg = None          # HALF of the pixel geometrical volume and max volume of e- cloud (cm**3)
    #     self.vth = None         # thermal velocity of e- (cm/s)
    #
    #     self.tr_p = None
    #     self.nt_p = None
    #     self.sigma_p = None
    #     self.beta_p = None
    #
    #     self.dob = 0.           # diffuse optical background
    #
    #     # if self.variables:      # (if the list is not empty)  # TODO
    #     #     if 'tr_p' not in self.variables:
    #     #         raise NotImplementedError()
    #     #     if 'nt_p' not in self.variables:
    #     #         raise NotImplementedError()
    #     #     if 'beta_p' not in self.variables:
    #     #         raise NotImplementedError()
    #
    #     self.st = 0.9828e-3
    #     self.sfwc = 900000.
    #     self.svg = 1.4e-10
    #     self.beta_s = 0.3
    #     self.sigma_s = np.array([1.])
    #     self.tr_s = np.array([0.03])
    #     self.nt_s = np.array([10.])                     # traps / pixel
    #
    # def get_name(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     return "CDM"
    #
    # def set_normalization(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     self.normalization = True
    #     for i in range(len(self.target_data)):
    #         self.target_data_norm += [self.normalize(self.target_data[i], dataset=i)]
    #
    # def set_weighting_function(self, func):
    #     """TBW.
    #
    #     :param func: 1d np.array
    #     :return:
    #     """
    #     self.weighting = True
    #     self.weighting_function = func.reshape(len(func), 1)
    #
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
    #
    # def set_simulated_fit_range(self, fit_range):
    #     """TBW.
    #
    #     :param fit_range: tuple
    #     :return:
    #     """
    #     self.sim_fit_range = slice(fit_range[0], fit_range[1])
    #
    # def set_target_fit_range(self, fit_range):
    #     """TBW.
    #
    #     :param fit_range: tuple
    #     :return:
    #     """
    #     self.targ_fit_range = slice(fit_range[0], fit_range[1])
    #
    # def set_bound(self, low_val, up_val):
    #     """TBW.
    #
    #     :param low_val: np.array
    #     :param up_val: np.array
    #     # :param low_val1: np.array
    #     # :param up_val1: np.array
    #     # :param low_val2: np.array
    #     # :param up_val2: np.array
    #     :return:
    #     """
    #     self.lbd = low_val
    #     self.ubd = up_val
    #
    # def save_champions_in_file(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     self.write2file = True
    #     self.champion_file = 'champion.out'
    #     f1 = open(self.champion_file, 'wb')  # truncate output file
    #     f1.close()
    #     self.pop_file = 'population.out'
    #     f2 = open(self.pop_file, 'wb')  # truncate output file
    #     f2.close()
    #
    #     # filelist = glob.glob('champion_id*.out')
    #     # for file in filelist:
    #     #     os.remove(file)
    #
    # def charge_injection(self, flag: bool):
    #     """TBW.
    #
    #     :param flag:
    #     :return:
    #     """
    #     self.chg_inj = flag
    #
    # def set_parallel_parameters(self,
    #                             traps: int = None,
    #                             t: float = None,
    #                             vg: float = None,
    #                             fwc: float = None,
    #                             vth: float = None,
    #                             sigma: float = None):
    #     """TBW.
    #
    #     :param traps: number of trap species
    #     :param t: parallel transfer period (s)
    #     :param vg: HALF of the pixel geometrical volume and max volume of e- cloud (cm**3)
    #     :param fwc: full well capacity of pixels in e-
    #     :param vth: thermal velocity of e- (cm/s)
    #     :param sigma: capture cross-section for all traps (cm**2)
    #     :return:
    #     """
    #     self.traps = traps
    #     self.t = t
    #     self.vg = vg
    #     self.fwc = fwc
    #     self.vth = vth
    #     if isinstance(sigma, float) or isinstance(sigma, int):
    #         self.sigma_p = sigma * np.ones(self.traps)
    #     else:
    #         self.sigma_p = sigma
    #     self.champion_f_list = np.zeros((1, 1))
    #     self.champion_x_list = np.zeros((1, 3 * self.traps + 1))
    #
    # def set_dimensions(self,
    #                    para_transfers: int = None,
    #                    seri_transfers: int = None,
    #                    # ydim: int = None,
    #                    # xdim: int = None,
    #                    # ystart: int = None,
    #                    # xstart: int = None
    #                    ):
    #     """TBW.
    #
    #     :param para_transfers:
    #     :param seri_transfers:
    #     # :param ydim:
    #     # :param xdim:
    #     # :param ystart:
    #     # :param xstart:
    #     :return:
    #     """
    #     self.para_transfers = para_transfers
    #     self.seri_transfers = seri_transfers
    #     # self.ydim = ydim
    #     # self.xdim = xdim
    #     # self.y_start = ystart
    #     # self.x_start = xstart
    #
    # def least_squares(self, simulated_data, dataset):
    #     """TBW.
    #
    #     :param simulated_data: 2d np.array
    #     :param dataset: int
    #     :return:
    #     """
    #     input_array = simulated_data[self.sim_fit_range]
    #
    #     if self.normalization:
    #         input_array = self.normalize(input_array, dataset=dataset)
    #         target = self.target_data_norm[dataset][self.targ_fit_range]
    #     else:
    #         target = self.target_data[dataset][self.targ_fit_range]
    #
    #     diff = target - input_array
    #     diff_square = diff * diff
    #
    #     if self.weighting:
    #         diff_square *= self.weighting_function
    #
    #     return np.sum(diff_square)
    #
    # def normalize(self, array, dataset):
    #     """Normalize dataset arrays by injected signal maximum.
    #
    #     :param array: 1d np.array
    #     :param dataset: int
    #     :return:
    #     """
    #     return array / np.average(self.target_data[dataset][self.targ_fit_range])
    #
    # def fitness(self, parameter):
    #     """Call the fitness function, elements of parameter array could be logarithm values.
    #
    #     :param parameter: 1d np.array
    #     :return:
    #     """
    #     # if self.tr_log:
    #     #     parameter[0: self.traps] = np.power(10, parameter[0: self.traps])  # TODO: generalize this
    #     # if self.nt_log:
    #     #     parameter[self.traps: 2 * self.traps] = np.power(10, parameter[self.traps: 2 * self.traps])
    #     # if self.sigma_log:
    #     #     parameter[2 * self.traps: 3 * self.traps] = np.power(10, parameter[2 * self.traps: 3 * self.traps])
    #     # if self.beta_log:
    #     #     raise NotImplementedError('You do not want this :)')
    #     return self.fitness_evaluation(parameter)
    #
    # def fitness_evaluation(self, parameter):
    #     """Evaluate fitness.
    #
    #     The fitness function, elements of parameter can not be logarithm values!
    #     :param parameter: 1d np.array
    #     :return:
    #     """
    #     # if self.champion_file is None:
    #     #     self.champion_file = 'champion_id' + str(id(self)) + '.out'
    #
    #     # overall_fitness = 0.
    #     # for i in range(self.datasets):
    #     #     # self.run_cdm(parameter, dataset=i)
    #     #     # results = self.run_cdm(parameter, dataset=i)
    #     #     # fitness = self.least_squares(results, dataset=i)
    #     #     fitness = 1
    #     #     overall_fitness += fitness
    #     overall_fitness = 1.
    #     # output_detector = self.pipeline.run_pipeline(self.detector)
    #     print('minden fasza')
    #
    #     # paramsize = len(parameter)
    #     # ord_param = None
    #     # if paramsize == (2 * self.traps + 1):
    #     #     ordered_parameter = pd.DataFrame(np.c_[parameter[0:self.traps],
    #     #                                            parameter[self.traps:2 * self.traps]],
    #     #                                      columns=['time',
    #     #                                               'density'])
    #     #     ordered_parameter = ordered_parameter.sort_values(by=['time'])
    #     #     ord_param = np.append(np.array([]), ordered_parameter.time.values)
    #     #     ord_param = np.append(ord_param, ordered_parameter.density.values)
    #     #
    #     # elif paramsize == (3 * self.traps + 1):
    #     #     ordered_parameter = pd.DataFrame(np.c_[parameter[0:self.traps],
    #     #                                            parameter[self.traps:2 * self.traps],
    #     #                                            parameter[2 * self.traps:3 * self.traps]],
    #     #                                      columns=['time',
    #     #                                               'density',
    #     #                                               'sigma'])
    #     #     ordered_parameter = ordered_parameter.sort_values(by=['time'])
    #     #     ord_param = np.append(np.array([]), ordered_parameter.time.values)
    #     #     ord_param = np.append(ord_param, ordered_parameter.density.values)
    #     #     ord_param = np.append(ord_param, ordered_parameter.sigma.values)
    #     #
    #     # ord_param = np.append(ord_param, parameter[-1])
    #     # ord_param = ord_param.reshape(1, paramsize)
    #     #
    #     # if self.n % self.pop == 0:
    #     #     self.fitness_array = np.array([overall_fitness])
    #     #     self.population = ord_param
    #     # else:
    #     #     self.fitness_array = np.vstack((self.fitness_array, np.array([overall_fitness])))
    #     #     self.population = np.vstack((self.population, ord_param))
    #     #
    #     # if (self.n + 1) % self.pop == 0:
    #     #
    #     #     best_index = np.argmin(self.fitness_array)
    #     #
    #     #     if self.g == 0:
    #     #         self.champion_f_list[self.g] = self.fitness_array[best_index]
    #     #         self.champion_x_list[self.g] = self.population[best_index, :]
    #     #     else:
    #     #         best_champ_index = np.argmin(self.champion_f_list)
    #     #
    #     #         if self.fitness_array[best_index] <= self.champion_f_list[best_champ_index]:
    #     #             self.champion_f_list = np.vstack((self.champion_f_list, self.fitness_array[best_index]))
    #     #             self.champion_x_list = np.vstack((self.champion_x_list, self.population[best_index]))
    #     #         else:
    #     #             self.champion_f_list = np.vstack((self.champion_f_list, self.champion_f_list[-1]))
    #     #             self.champion_x_list = np.vstack((self.champion_x_list, self.champion_x_list[-1]))
    #     #
    #     #     if self.write2file:
    #     #         str_format = '%d' + (paramsize + 1) * ' %.6E'
    #     #         with open(self.champion_file, 'ab') as f3:
    #     #             np.savetxt(f3, np.c_[np.array([self.g]),
    #     #                                  self.champion_f_list[self.g],
    #     #                                  self.champion_x_list[self.g, :].reshape(1, paramsize)],
    #     #                        fmt=str_format)
    #     #
    #     #         if self.g % 200 == 0 or self.g == self.gen:
    #     #             str_format = '%d' + (paramsize + 1) * ' %.6E'
    #     #             with open(self.pop_file, 'ab') as f4:
    #     #                 np.savetxt(f4, np.c_[self.g * np.ones(self.fitness_array.shape),
    #     #                                      self.fitness_array,
    #     #                                      self.population], fmt=str_format)
    #     #
    #     #     self.g += 1
    #     #
    #     # self.n += 1
    #
    #     return [overall_fitness]
    #
    # def run_cdm(self, parameter, dataset):
    #     """TBW.
    #
    #     :param parameter: 2d np.array
    #     :param dataset: int index of dataset
    #     :return:
    #     """
    #     # TODO: finish this, do not general enough
    #     if len(self.variables) == 2:
    #         subarrays = np.split(parameter, [self.traps,
    #                                          2 * self.traps])
    #         self.tr_p = subarrays[0]
    #         self.nt_p = subarrays[1]
    #     elif len(self.variables) == 3:
    #         subarrays = np.split(parameter, [self.traps,
    #                                          2 * self.traps,
    #                                          2 * self.traps + 1])
    #         self.tr_p = subarrays[0]
    #         self.nt_p = subarrays[1]
    #         self.beta_p = subarrays[2][0]
    #     elif len(self.variables) == 4:
    #         subarrays = np.split(parameter, [self.traps,
    #                                          2 * self.traps,
    #                                          3 * self.traps,
    #                                          3 * self.traps + 1])
    #         self.tr_p = subarrays[0]
    #         self.nt_p = subarrays[1]
    #         self.sigma_p = subarrays[2]
    #         self.beta_p = subarrays[3][0]
    #
    #     # output = cdm(s=self.fullframe[dataset],
    #     #              beta_p=self.beta_p,
    #     #              beta_s=self.beta_s,
    #     #              vg=self.vg, svg=self.svg,
    #     #              t=self.t, st=self.st,
    #     #              fwc=self.fwc, sfwc=self.sfwc,
    #     #              vth=self.vth,
    #     #              charge_injection=self.chg_inj,
    #     #              all_parallel_trans=self.para_transfers,
    #     #              all_serial_trans=self.seri_transfers,
    #     #              sigma_p=self.sigma_p,
    #     #              sigma_s=self.sigma_s,
    #     #              tr_p=self.tr_p,
    #     #              tr_s=self.tr_s,
    #     #              nt_p=self.nt_p,
    #     #              nt_s=self.nt_s)
    #
    #     # output = cdm(
    #     #              beta_p=self.beta_p, beta_s=self.beta_s,
    #     #              sigma_p=self.sigma_p, sigma_s=self.sigma_s,
    #     #              tr_p=self.tr_p, tr_s=self.tr_s,
    #     #              nt_p=self.nt_p, nt_s=self.nt_s,
    #     #              chg_inj=self.chg_inj,  # ###########
    #     #              parallel_cti=True,  # #############
    #     #              serial_cti=False,  # ##############
    #     #              para_transfers=self.para_transfers)  # #########
    #
    #     # calib_pipeline, calib_detector = self.calib.get_everything()
    #     # output_detector = calib_pipeline.run_pipeline(calib_detector)
    #
    #     # return output_detector
    #     return 1
    #
    # def get_bounds(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     return self.lbd, self.ubd
