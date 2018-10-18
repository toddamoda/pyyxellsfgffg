"""
CDM model calibration with PYGMO

https://esa.github.io/pagmo2/index.html

NEW AND BETTER DATA:
--irrad cold --data ../data/better-plato-target-data/ --traps 4
--irrad warm --data ../data/better-plato-target-data/ --traps 4
--irrad former --data ../data/former_test_campaign_flatfield/ --traps 4
On grid:
--irrad cold --data /home/dlucsany/cdm/data/better-plato-target-data/ --traps 4
--irrad warm --data /home/dlucsany/cdm/data/better-plato-target-data/ --traps 4

OLD DATA:
--irrad test --data ../data/noisy_cdm_valid/ --traps 4
--irrad cold --data ../data/plato-target-data/ --traps 4
--irrad warm --data ../data/plato-target-data/ --traps 4
On grid:
--irrad test --data /home/dlucsany/cdm/data/noisy_cdm_valid/ --traps 4
--irrad cold --data /home/dlucsany/cdm/data/plato-target-data/ --traps 4
--irrad warm --data /home/dlucsany/cdm/data/plato-target-data/ --traps 4
"""
import time
import argparse
import numpy as np
import pygmo as pg
# from pyxel.calibration.problem import ModelFitting
# from pyxel.calibration.inputdata import read_plato_data, read_test_data, read_former_campaign_data


def time_log(loc, ref_time):
    """Logging time.

    :return:
    """
    time_diff = time.time() - ref_time
    with open('log.out', 'a') as log:
        log.write('\ntime ' + str(loc) + ': \t\t\t%5.4f sec' % time_diff)
    return time_diff


def algorithm():
    """TBW.

    :return:
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)
    parser.add_argument('-i', '--irrad', required=True, help='Type of CCD irradiation ("cold", "warm", "test")')
    parser.add_argument('-d', '--data', required=True, help='Path of datafiles')
    parser.add_argument('-t', '--traps', required=True, help='Number of trap species')

    parser.add_argument('-isl', '--islands', default=0, help='Number of islands')
    parser.add_argument('-pop', '--population', default=300, help='Population size per island')
    parser.add_argument('-gen', '--generations', default=300, help='Number of generations')

    parser.add_argument('-adpt', '--adapt', default=1, help='Self-adaptation scheme')  # 1: Brest; 2: Elsayed
    parser.add_argument('-mv', '--variant', default=2, help='Mutation variant')

    parser.add_argument('-mut', '--mutation', default=0.45, help='Mutation probability')
    parser.add_argument('-cr', '--crossover', default=0.45, help='Crossover probability')
    parser.add_argument('-sel', '--selection', default=0.05, help='Selected fraction')

    parser.add_argument('-s', '--seed', default=1111, help='Random seed')

    parser.add_argument('-wt', '--weight_tau', default=None, help='Time constant of weighting function')
    opts = parser.parse_args()

    if opts.irrad not in ['cold', 'warm', 'test', 'former']:
        print('Bad argument for -i/--irrad')
        parser.print_help()
        return

    if opts.seed is None:
        opts.seed = np.random.randint(0, 10000)
    else:
        opts.seed = int(opts.seed)
    pg.set_global_rng_seed(seed=opts.seed)

    with open('log.out', 'w') as log:
        log.write('\nCDM calibration started')
    start_time = time.time()

    traps = int(opts.traps)
    # parameters = ['tr_p', 'nt_p', 'beta_p']
    parameters = ['tr_p', 'nt_p', 'sigma_p', 'beta_p']
    number_of_transfers = 1552

    island_mode = 'mp_island'
    islands = int(opts.islands)
    if islands == 0:
        use_archi = False
    else:
        use_archi = True

    island_type = None
    if island_mode == 'mp_island':
        island_type = pg.mp_island()
    elif island_mode == 'ipyparallel_island':
        island_type = pg.ipyparallel_island()   # not tested yet

    evolution = True
    sade = True
    sga = False
    nlopt = False

    self_adaptation_scheme = int(opts.adapt)
    mutant_var = int(opts.variant)
    generations = int(opts.generations)
    population_size = int(opts.population)
    cr_prob = float(opts.crossover)           # probability of crossover
    mut_prob = float(opts.mutation)           # probability of mutation
    selection = int(np.ceil(opts.selection * population_size))

    nlopt_max_eval = 10       # max evaluation number  # TODO set it
    nlopt_xtol_rel = 1e-8     # relative stopping criterion for x

    t = 947.22e-6               # s
    fwc = 1.e6                  # e-
    vg = 1.62e-10               # cm**3 (half volume!)
    # # # vth = 1.2175e7            # cm/s, from Alex's code
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook

    # sigma = 5.e-16              # cm**2 (for all traps)
    sigma = None                  # cm**2 (for all traps)

    tr_scale = 'log'
    nt_scale = 'log'
    sigma_scale = 'log'
    beta_scale = 'lin'

    # lo_tr_p, up_tr_p = traps * [np.log10(1.e-6)], traps * [np.log10(1.)]
    # lo_tr_p, up_tr_p = traps * [np.log10(t)], traps * [np.log10(1.)]
    # const_rel_time = [np.log10(4.36233759765019e-03), np.log10(3.03179103357533e-02),
    #                   np.log10(2.34800590710653e-01), np.log10(1.01730294052936e-03)]       # result of new_plato/cold/job_s1234
    # const_rel_time = [np.log10(1.63400595549762e-03), np.log10(1.38897806984646e-02),
    #                   np.log10(4.40971331369948e-03), np.log10(1.27310155855170e-01)]       # result of new_plato/warm/job_s7895
    # lo_tr_p, up_tr_p = const_rel_time, const_rel_time

    # lo_tr_p, up_tr_p = traps * [np.log10(t)], traps * [np.log10(2.)]
    # lo_nt_p, up_nt_p = traps * [np.log10(0.0001)], traps * [np.log10(100.)]
    # lo_beta_p, up_beta_p = [0.01], [0.99]

    # lb = lo_tr_p + lo_nt_p +  lo_beta_p
    # ub = up_tr_p + up_nt_p + up_beta_p

    lo_tr_p, up_tr_p = traps * [np.log10(t)], traps * [np.log10(2.)]
    lo_nt_p, up_nt_p = traps * [np.log10(0.0001)], traps * [np.log10(100.)]
    lo_sigma_p, up_sigma_p = traps * [np.log10(1.e-21)], traps * [np.log10(1.e-16)]
    lo_beta_p, up_beta_p = [0.01], [0.99]

    lb = lo_tr_p + lo_nt_p + lo_sigma_p + lo_beta_p
    ub = up_tr_p + up_nt_p + up_sigma_p + up_beta_p

    fit_range_length = 350

    x = np.linspace(start=1, stop=fit_range_length, num=fit_range_length)
    x = x.reshape(len(x), 1)

    if opts.weight_tau is not None:
        opts.weight_tau = float(opts.weight_tau) * 1.0e-04
        weighting_func = 1 - (np.exp(-1 * t * x / opts.weight_tau))

    # chi-square method:
    # weighting_func = 1/target_error         # -> not good, because error values can be negative!!!!
    # weighting_func = 1/(target_error ** 2)  # -> used earlier as "chi-square"

    target_start_fit, target_end_fit = None, None
    injection_profile, target_output, target_error = None, None, None
    data_files = None

    if opts.irrad == 'test':
        #     injection_profile, target_output = read_test_data(data_path=opts.data)
        #     target_start_fit, target_end_fit = 1103, 1103 + fit_range_length
        raise NotImplementedError()

    if opts.irrad == 'cold':
        # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
        data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']

    elif opts.irrad == 'warm':
        # data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd15.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']
        data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']

    elif opts.irrad == 'former':
        data_files = ['ccd270b-par-EPER-Ei1-one-image-single-4.txt',
                      'ccd270b-par-EPER-Ei1-one-image-single-8.txt',
                      'ccd270b-par-EPER-Ei1-one-image-single-12.txt',
                      'ccd270b-par-EPER-Ei1-one-image-single-16.txt']
        flatfield_avg_signal = [354.437103271,  # 4
                                2078.9050293,   # 8
                                7404.50146484,  # 12
                                12562.7226562]  # 16
        flatfield_illumination, target_output = read_former_campaign_data(data_path=opts.data, data_files=data_files,
                                                                          flatfield_avg_signal=flatfield_avg_signal,
                                                                          det_pix_rows=number_of_transfers)

        target_start_fit, target_end_fit = 1, 1 + fit_range_length
        sim_start_fit, sim_end_fit = 1, 1 + fit_range_length  # TODO 0 ????????????

    if opts.irrad != 'former':
        injection_profile, target_output, target_error = read_plato_data(data_path=opts.data, data_files=data_files,
                                                                         start=None, end=None)

        target_start_fit, target_end_fit = 51, 51 + fit_range_length

        sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length

    with open('result.out', 'w') as file:
        file.write('Seed: %d' % opts.seed)

        file.write('\n\nData:')
        if opts.irrad == 'test':
            file.write('\n  plato_cdm_4trap_15.5V.txt,'
                       '\n  plato_cdm_4trap_16.5V.txt,'
                       '\n  plato_cdm_4trap_18.5V.txt,'
                       '\n  plato_cdm_4trap_19.5V.txt')
        elif opts.irrad == 'cold' or 'warm':
            for i in range(len(data_files)):
                file.write('\n ' + data_files[i] + ' (col 20),')
        elif opts.irrad == 'former':
            for i in range(len(data_files)):
                file.write('\n ' + data_files[i] + ' (flatfield),')

        file.write('\n\nCDM parameters:')
        file.write('\n  Number of transfers in CCD:  %d' % number_of_transfers)
        file.write('\n  Parallel transfer period:    %.4e' % t)
        file.write('\n  FWC:                         %.4e' % fwc)
        file.write('\n  Half pixel volume:           %.4e' % vg)
        file.write('\n  Thermal velocity:            %.7e' % vth)
        if sigma is not None:
            file.write('\n  Capture cross-sections:      %.4e' % sigma)

        file.write('\n\nFitting:')
        file.write('\n  Variables: ' + str(parameters))
        file.write('\n  Number of traps: ' + str(traps))
        file.write('\n  Fit range (cdm output):  [%d, %d]' % (sim_start_fit, sim_end_fit))
        file.write('\n  Fit range (target data): [%d, %d]' % (target_start_fit, target_end_fit))
        file.write('\n  Scales:           tr_p - ' + tr_scale + ';  nt_p - ' + nt_scale +
                   ';  sigma_p - ' + sigma_scale + ';  beta - ' + beta_scale)
        file.write('\n  Lower boundaries: ' + str(lb))
        file.write('\n  Upper boundaries: ' + str(ub))
        if opts.weight_tau is None:
            file.write('\n  Weighting function: no weighting')
        else:
            file.write('\n  Weighting function: (1 - (np.exp(-1 * ptp * x / ' + str(opts.weight_tau) + ')))')

        if sga:
            file.write('\n\nSimple Genetic Algorithm:')
            file.write('\n  Pygmo island mode:       ' + island_mode)
            file.write('\n  Islands:                 %d' % islands)
            file.write('\n  Population per island:   %d' % population_size)
            file.write('\n  Generations:             %d' % generations)
            file.write('\n  Selected individuals:    %d' % selection)
            file.write('\n  Crossover probability:   %.2f' % cr_prob)
            file.write('\n  Mutation probability:    %.2f' % mut_prob)
        if sade:
            file.write('\n\nSelf-adaptive Differential Evolution Algorithm:')
            file.write('\n  Pygmo island mode:       ' + island_mode)
            file.write('\n  Islands:                 %d' % islands)
            file.write('\n  Population per island:   %d' % population_size)
            file.write('\n  Generations:             %d' % generations)
            file.write('\n  Self adaptation scheme:  %d' % self_adaptation_scheme)
            file.write('\n  Mutation variant:        %d' % mutant_var)
        if nlopt:
            file.write('\n\nNelder-Mead Simplex Algorithm:')
            file.write('\n  Pygmo island mode:       ' + island_mode)
            file.write('\n  Optimizing only the best individual per island')
            file.write('\n  Max evaluation:          %d' % nlopt_max_eval)
            file.write('\n  Relative tolerance:      %.2e' % nlopt_xtol_rel)

    time_log('data read', start_time)

    ###################################
    # Simple Genetic Algorithm
    ###################################
    sga_cx, sga_cf = None, None
    if evolution:
        cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)

        cdm.charge_injection(True)
        cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
        cdm.set_dimensions(para_transfers=number_of_transfers)
        cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
        cdm.set_target_fit_range((target_start_fit, target_end_fit))
        cdm.set_uniformity_scales(sc_tr=tr_scale, sc_nt=nt_scale, sc_sig=sigma_scale, sc_be=beta_scale)
        cdm.set_bound(low_val=lb, up_val=ub)          # tr_p[n] & nt_p[n] & sigma_p[n] & beta_p[n]
        cdm.set_normalization()
        cdm.set_sga_algo(evol=True, gen=generations, pop=population_size)
        cdm.save_champions_in_file()
        if opts.weight_tau is not None:
            cdm.set_weighting_function(weighting_func)

        prob = pg.problem(cdm)

        time_log('set cdm', start_time)

        algo = None
        if sga:
            opt_algorithm = pg.sga(gen=generations,
                                   cr=cr_prob,              # crossover probability
                                   crossover="single",      # single, exponential, binomial, sbx
                                   m=mut_prob,              # mutation probability
                                   mutation="uniform",      # uniform, gaussian, polynomial
                                   param_s=selection,       # number of best ind. in 'truncated'/size of the tournament
                                   selection="truncated"    # tournament, truncated
                                   # eta_c=1.,                # distribution index for sbx crossover
                                   # param_m=0.25,            # mutation parameter
                                   # mutation="gaussian",     # uniform, gaussian, polynomial
                                   )

        elif sade:
            opt_algorithm = pg.sade(gen=generations,
                                    variant=mutant_var,
                                    variant_adptv=self_adaptation_scheme,
                                    ftol=1e-6,
                                    xtol=1e-6,
                                    memory=False)

        algo = pg.algorithm(opt_algorithm)
        algo.set_verbosity(1)
        time_log('algo', start_time)
        if use_archi:
            archi = pg.archipelago(n=islands, algo=algo, prob=prob, pop_size=population_size, udi=island_type)
            time_log('archi', start_time)
            archi.evolve()
            time_log('evolve', start_time)
            archi.wait_check()
            time_log('wait', start_time)
            sga_cx = archi.get_champions_x()
            sga_cf = archi.get_champions_f()
        else:
            pop = pg.population(prob, size=population_size)
            time_log('pop created', start_time)
            pop = algo.evolve(pop)
            uda = algo.extract(pg.sade)
            uda.get_log()
            time_log('evolve', start_time)
            sga_cx = pop.champion_x       # TODO: select the best N champions and fill pop2 with them
            sga_cf = pop.champion_f

        # print('sga_cx: ', sga_cx)
        # print('sga_cf: ', sga_cf)
        # uda = algo.extract(pg.sga)
        # uda = algo.extract(pg.sade)
        # log = uda.get_log()

        time_sga_end = time_log('sga ended', start_time)

    ###################################
    # Nelder-Mead Simplex
    ###################################
    nlopt_cx, nlopt_cf = None, None
    if nlopt:
        cdm.set_sga_algo()
        prob2 = pg.problem(cdm)

        nl = pg.nlopt('neldermead')
        # nl.maxtime = 180                # stop when the optimization time (in seconds) exceeds maxtime
        nl.maxeval = nlopt_max_eval       # stop when the number of function evaluations exceeds maxeval
        nl.xtol_rel = nlopt_xtol_rel      # relative stopping criterion for x
        # nl.stopval = 1
        # nl.xtol_abs = 1e-8              # absolute stopping criterion for x
        algo2 = pg.algorithm(nl)
        algo2.set_verbosity(0)

        time_log('algo2', start_time)
        if use_archi:
            champions_f, indices = np.unique(sga_cf, return_index=True)
            pop2 = []
            nn = len(champions_f)
            for _ in range(nn):
                pop2 += [pg.population(prob2)]
            time_log('pop2 created', start_time)
            archi2 = pg.archipelago()
            for i in range(nn):
                champion_x = sga_cx[indices[i]]
                pop2[i].push_back(x=champion_x, f=[champions_f[i]])
                archi2.push_back(algo=algo2, pop=pop2[i], udi=island_type)
            time_log('archi2', start_time)
            archi2.evolve()
            time_log('evolve', start_time)
            archi2.wait_check()
            time_log('wait', start_time)
            nlopt_cx = archi2.get_champions_x()
            nlopt_cf = archi2.get_champions_f()
        else:
            pop2 = pg.population(prob2)
            pop2.push_back(sga_cx, sga_cf)
            pop2 = algo2.evolve(pop2)
            nlopt_cx = pop2.champion_x
            nlopt_cf = pop2.champion_f

    cx_final, cf_final = None, None
    if evolution:
        if use_archi:
            ind = np.argmin(sga_cf)
            sga_cx = sga_cx[ind]
            sga_cf = sga_cf[ind]

        cx_final = sga_cx
        cf_final = sga_cf
    if nlopt:
        if use_archi:
            ind = np.argmin(nlopt_cf)
            nlopt_cx = nlopt_cx[ind]
            nlopt_cf = nlopt_cf[ind]

        cx_final = nlopt_cx
        cf_final = nlopt_cf

    # RESULTS:
    result_tr_p = cx_final[:traps]
    result_nt_p = cx_final[traps:2*traps]
    result_sigma_p = cx_final[2*traps:3*traps]
    result_beta_p = cx_final[3*traps:]

    if tr_scale == 'log':
        result_tr_p = np.power(10, result_tr_p)
    if nt_scale == 'log':
        result_nt_p = np.power(10, result_nt_p)
    if sigma_scale == 'log':
        result_sigma_p = np.power(10, result_sigma_p)
    if beta_scale == 'log':
        result_beta_p = np.power(10, result_beta_p)

    fitted_data = []
    for i in range(len(target_output)):
        fitted_data += [cdm.run_cdm(cx_final, i)]
    with open('fit.out', 'wb') as of:
        np.savetxt(of, np.c_[fitted_data[0], fitted_data[1], fitted_data[2], fitted_data[3]], fmt='%.8E')
    
    with open('result.out', 'a') as file:
        file.write('\n\nFinal champion with best fitness:')
        file.write('\n  Release time (s):      ' +
                   np.array2string(result_tr_p, formatter={'float_kind': lambda x: "%.10e" % x}, separator=', '))
        file.write('\n  Density (trap/pix):    ' +
                   np.array2string(result_nt_p, formatter={'float_kind': lambda x: "%.10e" % x}, separator=', '))
        file.write('\n  Cross-section (cm^2):  ' +
                   np.array2string(result_sigma_p, formatter={'float_kind': lambda x: "%.6e" % x}, separator=', '))
        file.write('\n  Beta parameter:        ' +
                   np.array2string(result_beta_p, formatter={'float_kind': lambda x: "%.6f" % x}, separator=', '))
        file.write('\n  Fitness:               ' +
                   np.array2string(cf_final, formatter={'float_kind': lambda x: "%.6e" % x}))

        now = time.time()
        file.write('\n\nRunning time:')
        # file.write('\n  SGA:          %.3f sec' % time_sga_end)
        # file.write('\n  Simplex:      %.3f sec' % (now - start_time - time_sga_end))
        file.write('\n  TOTAL:        %.3f sec\n' % (now - start_time))

    time_log('finished', start_time)


if __name__ == '__main__':
    algorithm()
