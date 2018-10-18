"""TBW."""
import numpy as np
import pygmo as pg
from pyxel.calibration.problem import ModelFitting
# from pyxel.calibration.inputdata import read_plato_data, read_test_data, read_former_campaign_data


class Calibration:
    """TBW.

    :return:
    """

    def __init__(self, settings, config):
        """TBW.

        :param settings:
        :param config:
        """
        self.detector = config.detector
        self.pipeline = config.pipeline
        self.settings = settings

        self.model_input_data = None
        self.target_output = None
        self.target_output_error = None
        self.weighting_func = None

        self.parameters = ['tr_p', 'nt_p', 'sigma_p', 'beta_p']
        self.tr_scale = 'log'
        self.nt_scale = 'log'
        self.sigma_scale = 'log'
        self.beta_scale = 'lin'
        self.fit_range_length = 350
        self.target_start_fit, self.target_end_fit = 51, 51 + self.fit_range_length
        self.sim_start_fit, self.sim_end_fit = 1103, 1103 + self.fit_range_length

        self.sade = True
        self.sga = False
        self.neldermead = False

        self.generations = 10
        self.population_size = 10
        if self.sade:
            self.self_adaptation_scheme = 1
            self.mutant_var = 2
        if self.sga:
            self.cr_prob = None  # probability of crossover
            self.mut_prob = None  # probability of mutation
            self.selection = int(np.ceil(0 * self.population_size))
        if self.neldermead:
            self.neldermead_max_eval = None  # max evaluation number  # TODO set it
            self.neldermead_xtol_rel = None  # relative stopping criterion for x

        self.island_mode = 'mp_island'
        self.islands = 0

        # self.champion_x, self.champion_f = None, None

        self.fitting = None
        self.prob = None

        seed = 1111
        if seed is None:
            self.seed = np.random.randint(0, 10000)
        else:
            self.seed = int(seed)
        pg.set_global_rng_seed(seed=self.seed)

        if self.islands == 0:
            self.use_archi = False
        else:
            self.use_archi = True

        self.island_type = None
        if self.island_mode == 'mp_island':
            self.island_type = pg.mp_island()
        elif self.island_mode == 'ipyparallel_island':
            self.island_type = pg.ipyparallel_island()  # not tested yet

        # #################################################
        # Model specific input arguements:
        traps = 4
        t = 947.22e-6  # s
        if self.tr_scale == 'log':                   # TODO for loop and list for boundary values!!
            lo_tr_p, up_tr_p = traps * [np.log10(t)], traps * [np.log10(2.)]
        else:
            lo_tr_p, up_tr_p = traps * [t], traps * [2.]
        if self.nt_scale == 'log':
            lo_nt_p, up_nt_p = traps * [np.log10(0.0001)], traps * [np.log10(100.)]
        else:
            lo_nt_p, up_nt_p = traps * [0.0001], traps * [100.]
        if self.sigma_scale == 'log':
            lo_sigma_p, up_sigma_p = traps * [np.log10(1.e-21)], traps * [np.log10(1.e-16)]
        else:
            lo_sigma_p, up_sigma_p = traps * [1.e-21], traps * [1.e-16]
        if self.beta_scale == 'log':
            lo_beta_p, up_beta_p = [np.log10(0.01)], [np.log10(0.99)]
        else:
            lo_beta_p, up_beta_p = [0.01], [0.99]
        self.lb = lo_tr_p + lo_nt_p + lo_sigma_p + lo_beta_p
        self.ub = up_tr_p + up_nt_p + up_sigma_p + up_beta_p

        # x = np.linspace(start=1, stop=self.fit_range_length, num=self.fit_range_length)
        # x = x.reshape(len(x), 1)
        #
        # if opts.weight_tau is not None:
        #     opts.weight_tau = float(opts.weight_tau) * 1.0e-04
        #     weighting_func = 1 - (np.exp(-1 * t * x / opts.weight_tau))
        #
        # # chi-square method:
        # # weighting_func = 1/target_error         # -> not good, because error values can be negative!!!!
        # # weighting_func = 1/(target_error ** 2)  # -> used earlier as "chi-square"

    def set_data(self,
                 model_input_data=None,
                 target_output=None,
                 weighting_func=None):
        """TBW.

        :return:
        """
        self.model_input_data = model_input_data
        self.target_output = target_output
        self.weighting_func = weighting_func

    def fitting_problem(self):
        """TBW.

        :return:
        """
        self.fitting = ModelFitting(input_data=self.model_input_data,
                                    target=self.target_output,
                                    variables=self.parameters,
                                    gen=self.generations,
                                    pop=self.population_size)
        self.fitting.set_simulated_fit_range((self.sim_start_fit, self.sim_end_fit))
        self.fitting.set_target_fit_range((self.target_start_fit, self.target_end_fit))
        self.fitting.set_uniformity_scales(sc_tr=self.tr_scale,
                                           sc_nt=self.nt_scale,
                                           sc_sig=self.sigma_scale,
                                           sc_be=self.beta_scale)
        self.fitting.set_bound(low_val=self.lb, up_val=self.ub)
        self.fitting.set_normalization()
        self.fitting.save_champions_in_file()
        if self.weighting_func is not None:
            self.fitting.set_weighting_function(self.weighting_func)

        # #################################################
        # Model specific input arguements:
        traps = 4                                                 # TODO read these from YAML config automatically
        number_of_transfers = 1552
        t = 947.22e-6  # s
        fwc = 1.e6  # e-
        vg = 1.62e-10  # cm**3 (half volume!)
        # # vth = 1.2175e7            # cm/s, from Alex's code
        vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
        # sigma = 5.e-16              # cm**2 (for all traps)
        sigma = None  # cm**2 (for all traps)
        self.fitting.charge_injection(True)                           # TODO set these from YAML config automatically
        self.fitting.set_parallel_parameters(traps=traps, t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
        self.fitting.set_dimensions(para_transfers=number_of_transfers)

        # self.prob = pg.problem(self.fitting)
        # self.prob = pg.problem(pg.rosenbrock())
        return self.fitting

    def create_pygmo_prob(self, obj):
        """TBW.

        :return:
        """
        self.prob = pg.problem(obj)
        # self.prob = pg.problem(pg.rosenbrock())

    def evolutionary_algorithm(self):
        """TBW.

        :return:
        """
        ##################################################
        # Simple Genetic Algorithm
        ##################################################
        opt_algorithm = None
        if self.sga:
            opt_algorithm = pg.sga(gen=self.generations,
                                   cr=self.cr_prob,  # crossover probability
                                   crossover="single",  # single, exponential, binomial, sbx
                                   m=self.mut_prob,  # mutation probability
                                   mutation="uniform",  # uniform, gaussian, polynomial
                                   param_s=self.selection,
                                   # number of best ind. in 'truncated'/size of the tournament
                                   selection="truncated"  # tournament, truncated
                                   # eta_c=1.,                # distribution index for sbx crossover
                                   # param_m=0.25,            # mutation parameter
                                   # mutation="gaussian",     # uniform, gaussian, polynomial
                                   )
        ##################################################
        # Self-Adaptive Differential Evolution Algorithm
        ##################################################
        elif self.sade:
            opt_algorithm = pg.sade(gen=self.generations,
                                    variant=self.mutant_var,
                                    variant_adptv=self.self_adaptation_scheme,
                                    ftol=1e-6,
                                    xtol=1e-6,
                                    memory=False)

        algo = pg.algorithm(opt_algorithm)
        algo.set_verbosity(1)

        if self.use_archi:
            archi = pg.archipelago(n=self.islands, algo=algo, prob=self.prob, pop_size=self.population_size,
                                   udi=self.island_type)
            archi.evolve()
            archi.wait_check()
            champion_x = archi.get_champions_x()
            champion_f = archi.get_champions_f()
        else:
            pop = pg.population(self.prob, size=self.population_size)
            pop = algo.evolve(pop)
            uda = algo.extract(pg.sade)
            uda.get_log()
            champion_x = pop.champion_x  # TODO: select the best N champions and fill pop2 with them
            champion_f = pop.champion_f

            # print('champion_x: ', champion_x)
            # print('champion_f: ', champion_f)
            # uda = algo.extract(pg.sga)
            # uda = algo.extract(pg.sade)
            # log = uda.get_log()

        return champion_x, champion_f

    def nonlinear_optimization_algorithm(self, earlier_champion_x, earlier_champion_f):
        """TBW.

        :return:
        """
        ##################################################
        # Non-Linear Optimization - Nelder-Mead Simplex
        ##################################################
        if self.neldermead:
            prob2 = pg.problem(self.fitting)

            nl = pg.nlopt('neldermead')
            # nl.maxtime = 180                # stop when the optimization time (in seconds) exceeds maxtime
            nl.maxeval = self.neldermead_max_eval  # stop when the number of function evaluations exceeds maxeval
            nl.xtol_rel = self.neldermead_xtol_rel  # relative stopping criterion for x
            # nl.stopval = 1
            # nl.xtol_abs = 1e-8              # absolute stopping criterion for x
            algo2 = pg.algorithm(nl)
            algo2.set_verbosity(0)

            if self.use_archi:
                earlier_champion_f, indices = np.unique(earlier_champion_f, return_index=True)
                pop2 = []
                nn = len(earlier_champion_f)
                for _ in range(nn):
                    pop2 += [pg.population(prob2)]
                archi2 = pg.archipelago()
                for i in range(nn):
                    pop2[i].push_back(x=earlier_champion_x[indices[i]], f=[earlier_champion_f[i]])
                    archi2.push_back(algo=algo2, pop=pop2[i], udi=self.island_type)
                archi2.evolve()
                archi2.wait_check()
                nlopt_cx = archi2.get_champions_x()
                nlopt_cf = archi2.get_champions_f()

                ind = np.argmin(nlopt_cf)
                cx_final = nlopt_cx[ind]
                cf_final = nlopt_cf[ind]
            else:
                pop2 = pg.population(prob2)
                pop2.push_back(earlier_champion_x, earlier_champion_f)
                pop2 = algo2.evolve(pop2)
                cx_final = pop2.champion_x
                cf_final = pop2.champion_f

            return cx_final, cf_final

    def log(self):
        """TBW.

        :return:
        """
        # with open('result.out', 'w') as file:
        #     file.write('Seed: %d' % opts.seed)
        #
        #     file.write('\n\nData:')
        #     if opts.irrad == 'test':
        #         file.write('\n  plato_cdm_4trap_15.5V.txt,'
        #                    '\n  plato_cdm_4trap_16.5V.txt,'
        #                    '\n  plato_cdm_4trap_18.5V.txt,'
        #                    '\n  plato_cdm_4trap_19.5V.txt')
        #     elif opts.irrad == 'cold' or 'warm':
        #         for i in range(len(data_files)):
        #             file.write('\n ' + data_files[i] + ' (col 20),')
        #     elif opts.irrad == 'former':
        #         for i in range(len(data_files)):
        #             file.write('\n ' + data_files[i] + ' (flatfield),')
        #
        #     file.write('\n\nCDM parameters:')
        #     file.write('\n  Number of transfers in CCD:  %d' % number_of_transfers)
        #     file.write('\n  Parallel transfer period:    %.4e' % t)
        #     file.write('\n  FWC:                         %.4e' % fwc)
        #     file.write('\n  Half pixel volume:           %.4e' % vg)
        #     file.write('\n  Thermal velocity:            %.7e' % vth)
        #     if sigma is not None:
        #         file.write('\n  Capture cross-sections:      %.4e' % sigma)
        #
        #     file.write('\n\nFitting:')
        #     file.write('\n  Variables: ' + str(parameters))
        #     file.write('\n  Number of traps: ' + str(traps))
        #     file.write('\n  Fit range (cdm output):  [%d, %d]' % (sim_start_fit, sim_end_fit))
        #     file.write('\n  Fit range (target data): [%d, %d]' % (target_start_fit, target_end_fit))
        #     file.write(
        #         '\n  Scales:
        # tr_p - ' + tr_scale + ';  nt_p - ' + nt_scale + ';  sigma_p - ' + sigma_scale + ';  beta - ' + beta_scale)
        #     file.write('\n  Lower boundaries: ' + str(lb))
        #     file.write('\n  Upper boundaries: ' + str(ub))
        #     if opts.weight_tau is None:
        #         file.write('\n  Weighting function: no weighting')
        #     else:
        #         file.write('\n  Weighting function: (1 - (np.exp(-1 * ptp * x / ' + str(opts.weight_tau) + ')))')
        #
        #     if sga:
        #         file.write('\n\nSimple Genetic Algorithm:')
        #         file.write('\n  Pygmo island mode:       ' + island_mode)
        #         file.write('\n  Islands:                 %d' % islands)
        #         file.write('\n  Population per island:   %d' % population_size)
        #         file.write('\n  Generations:             %d' % generations)
        #         file.write('\n  Selected individuals:    %d' % selection)
        #         file.write('\n  Crossover probability:   %.2f' % cr_prob)
        #         file.write('\n  Mutation probability:    %.2f' % mut_prob)
        #     if sade:
        #         file.write('\n\nSelf-adaptive Differential Evolution Algorithm:')
        #         file.write('\n  Pygmo island mode:       ' + island_mode)
        #         file.write('\n  Islands:                 %d' % islands)
        #         file.write('\n  Population per island:   %d' % population_size)
        #         file.write('\n  Generations:             %d' % generations)
        #         file.write('\n  Self adaptation scheme:  %d' % self_adaptation_scheme)
        #         file.write('\n  Mutation variant:        %d' % mutant_var)
        #     if nlopt:
        #         file.write('\n\nNelder-Mead Simplex Algorithm:')
        #         file.write('\n  Pygmo island mode:       ' + island_mode)
        #         file.write('\n  Optimizing only the best individual per island')
        #         file.write('\n  Max evaluation:          %d' % nlopt_max_eval)
        #         file.write('\n  Relative tolerance:      %.2e' % nlopt_xtol_rel)

    def results(self):
        """TBW.

        :return:
        """
        # # RESULTS:
        # result_tr_p = cx_final[:traps]
        # result_nt_p = cx_final[traps:2 * traps]
        # result_sigma_p = cx_final[2 * traps:3 * traps]
        # result_beta_p = cx_final[3 * traps:]
        #
        # if tr_scale == 'log':
        #     result_tr_p = np.power(10, result_tr_p)
        # if nt_scale == 'log':
        #     result_nt_p = np.power(10, result_nt_p)
        # if sigma_scale == 'log':
        #     result_sigma_p = np.power(10, result_sigma_p)
        # if beta_scale == 'log':
        #     result_beta_p = np.power(10, result_beta_p)
        #
        # fitted_data = []
        # for i in range(len(target_output)):
        #     fitted_data += [cdm.run_cdm(cx_final, i)]
        # with open('fit.out', 'wb') as of:
        #     np.savetxt(of, np.c_[fitted_data[0], fitted_data[1], fitted_data[2], fitted_data[3]], fmt='%.8E')
        #
        # with open('result.out', 'a') as file:
        #     file.write('\n\nFinal champion with best fitness:')
        #     file.write('\n  Release time (s):      ' + np.array2string(result_tr_p,
        #                                                               formatter={'float_kind': lambda x: "%.10e" % x},
        #                                                                separator=', '))
        #     file.write('\n  Density (trap/pix):    ' + np.array2string(result_nt_p,
        #                                                               formatter={'float_kind': lambda x: "%.10e" % x},
        #                                                                separator=', '))
        #     file.write('\n  Cross-section (cm^2):  ' + np.array2string(result_sigma_p,
        #                                                                formatter={'float_kind': lambda x: "%.6e" % x},
        #                                                                separator=', '))
        #     file.write('\n  Beta parameter:        ' + np.array2string(result_beta_p,
        #                                                                formatter={'float_kind': lambda x: "%.6f" % x},
        #                                                                separator=', '))
        #     file.write('\n  Fitness:               ' + np.array2string(cf_final,
        #                                                               formatter={'float_kind': lambda x: "%.6e" % x}))
        #
        #     now = time.time()
        #     file.write('\n\nRunning time:')
        #     # file.write('\n  SGA:          %.3f sec' % time_sga_end)
        #     # file.write('\n  Simplex:      %.3f sec' % (now - start_time - time_sga_end))
        #     file.write('\n  TOTAL:        %.3f sec\n' % (now - start_time))
