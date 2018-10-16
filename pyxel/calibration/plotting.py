"""
PLotting script for CDM model calibration script
"""
import glob
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.tri as tri
# from matplotlib import ticker
from pyxel.models.cdm.CDM import plot_1d_profile, plot_1d_profile_with_err, plot_residuals, plot_1d_profile_lin
from pyxel.calibration.inputdata import read_fit_data, read_test_data, read_plato_data
from pyxel.calibration.problem import CDMFitting
import pandas as pd
import seaborn as sns
import matplotlib.gridspec as gridspec


def read_champion(path, filename=None):
    """TBW.

    :param path: path of fit.out datafile
    :return:
    """
    if filename is not None:
        fitdata = np.array([])
        filelist = glob.glob(path + filename)
        if filelist:
            for file in filelist:
                if len(fitdata) == 0:
                    # data = np.loadtxt(file)[start:, :]
                    fitdata = np.loadtxt(file, dtype=float, delimiter=' ')[-1]
                else:
                    # data = np.vstack((data, np.loadtxt(file)[start:, :]))
                    fitdata = np.vstack((fitdata, np.loadtxt(file, dtype=float, delimiter=' ')[-1]))
        else:
            raise FileNotFoundError()
        # cf = fitdata[:, 1]
        # cx = fitdata[:, 2:]
        # return cx, cf
    else:
        fitdata = np.loadtxt(path, dtype=float, delimiter=' ')[-1]
        # rows, _ = fitdata.shape

    try:
        cf = fitdata[:, 1]
        cx = fitdata[:, 2:]
    except IndexError:
        cf = fitdata[1]
        cx = fitdata[2:]
    return cx, cf


def plot_01(irrad, injection_profile, target_output, target_error):
    """TBW.

    :return:
    """
    plt.figure()
    if irrad == 'cold':
        plot_1d_profile(injection_profile[0], label='inj, cold, 15.5V', m='--')
        plot_1d_profile(injection_profile[1], label='inj, cold, 16.5V', m='--')
        plot_1d_profile(injection_profile[2], label='inj, cold, 18.5V', m='--')
        plot_1d_profile(injection_profile[3], label='inj, cold, 19.5V', m='--')
        plot_1d_profile_with_err(target_output[0], target_error[0], label='cold, 15.5V')
        plot_1d_profile_with_err(target_output[1], target_error[1], label='cold, 16.5V')
        plot_1d_profile_with_err(target_output[2], target_error[2], label='cold, 18.5V')
        plot_1d_profile_with_err(target_output[3], target_error[3], label='cold, 19.5V')
    if irrad == 'warm':
        plot_1d_profile(injection_profile[0], label='inj, warm, 15V', m='--')
        plot_1d_profile(injection_profile[1], label='inj, warm, 16V', m='--')
        plot_1d_profile(injection_profile[2], label='inj, warm, 18V', m='--')
        plot_1d_profile(injection_profile[3], label='inj, warm, 19V', m='--')
        plot_1d_profile_with_err(target_output[0], target_error[0], label='warm, 15V')
        plot_1d_profile_with_err(target_output[1], target_error[1], label='warm, 16V')
        plot_1d_profile_with_err(target_output[2], target_error[2], label='warm, 18V')
        plot_1d_profile_with_err(target_output[3], target_error[3], label='warm, 19V')


def add_noise(cdm_output, gdpot, fpath, uni='const', sigma=20, seed=12421351):
    """Add noise to cdm outputs

    :param cdm_output: list
    :param gdpot: list
    :param uni: str, uniformity: const, linear
    :param sigma: double
    :param seed: int
    :return:
    """
    np.random.seed(seed)
    if uni == 'linear':
        # raise NotImplementedError()
        sigma_array1 = np.arange(start=sigma[0], stop=sigma[1], step=(len(cdm_output[0])))
        sigma_array2 = sigma_array1
        sigma_array3 = sigma_array1
        sigma_array4 = sigma_array1
    else:
        sigma_array1 = sigma * np.ones((len(cdm_output[0]), 1))
        sigma_array2 = sigma * np.ones((len(cdm_output[1]), 1))
        sigma_array3 = sigma * np.ones((len(cdm_output[2]), 1))
        sigma_array4 = sigma * np.ones((len(cdm_output[3]), 1))
    output_w_noise = []
    output_w_noise += [np.random.normal(loc=cdm_output[0], scale=sigma_array1)]
    output_w_noise += [np.random.normal(loc=cdm_output[1], scale=sigma_array2)]
    output_w_noise += [np.random.normal(loc=cdm_output[2], scale=sigma_array3)]
    output_w_noise += [np.random.normal(loc=cdm_output[3], scale=sigma_array4)]
    np.clip(output_w_noise[0], 0., None, output_w_noise[0])  # lower limit is 0
    np.clip(output_w_noise[1], 0., None, output_w_noise[1])
    np.clip(output_w_noise[2], 0., None, output_w_noise[2])
    np.clip(output_w_noise[3], 0., None, output_w_noise[3])
    np.savetxt(fpath + str(sigma) + '_' + gdpot[0] + '.txt', output_w_noise[0])
    np.savetxt(fpath + str(sigma) + '_' + gdpot[1] + '.txt', output_w_noise[1])
    np.savetxt(fpath + str(sigma) + '_' + gdpot[2] + '.txt', output_w_noise[2])
    np.savetxt(fpath + str(sigma) + '_' + gdpot[3] + '.txt', output_w_noise[3])
    return output_w_noise


def cdm_outputs(cdm, parameters, traps, gdpot, save2file=False):
    """Generate CDM outputs for all datasets
    test_parameters = np.hstack((tr_p, nt_p, beta_p))
    :param cdm:
    :param parameters:
    :param gdpot:
    :param traps:
    :param save2file:
    :return:
    """
    cdm_output = []
    cdm_output += [cdm.run_cdm(parameters, 0)]
    cdm_output += [cdm.run_cdm(parameters, 1)]
    cdm_output += [cdm.run_cdm(parameters, 2)]
    cdm_output += [cdm.run_cdm(parameters, 3)]
    if save2file:
        np.savetxt('../data/noisy_cdm_valid/plato_cdm_' +
                   str(traps) + 'trap_' + gdpot[0] + '.txt', cdm_output[0])
        np.savetxt('../data/noisy_cdm_valid/plato_cdm_' +
                   str(traps) + 'trap_' + gdpot[1] + '.txt', cdm_output[1])
        np.savetxt('../data/noisy_cdm_valid/plato_cdm_' +
                   str(traps) + 'trap_' + gdpot[2] + '.txt', cdm_output[2])
        np.savetxt('../data/noisy_cdm_valid/plato_cdm_' +
                   str(traps) + 'trap_' + gdpot[3] + '.txt', cdm_output[3])
    return cdm_output


def gd_pot_plot(injection_profile):
    """Guard Drain Potential plot
    
    :param :
    :return: 
    """
    gd_inj_warm = np.array([[15., injection_profile[0][0]],
                            [16., injection_profile[1][0]],
                            [18., injection_profile[2][0]],
                            [19., injection_profile[3][0]]])
    gd_inj_cold = np.array([[15.5, injection_profile[0][0]],
                            [16.5, injection_profile[1][0]],
                            [18.5, injection_profile[2][0]],
                            [19.5, injection_profile[3][0]]])
    plt.figure()
    plt.semilogy(gd_inj_warm[:, 0], gd_inj_warm[:, 1], '.-', label='warm irradiated')
    plt.semilogy(gd_inj_cold[:, 0], gd_inj_cold[:, 1], '.-', label='cold irradiated')
    plt.legend()
    plt.xlim((14.5, 20.))
    plt.ylim((5.e3, 5.e5))
    plt.xlabel('Guard Drain voltage (V)')
    plt.ylabel('electrons')
    plt.title('PLATO CCD charge injection (CCD280)')


def champion_rel_time_evolution(generations, params, traps, label=''):
    """

    :return:
    """
    # plt.figure()
    plt.ylabel(r'$\tau_{r}^{parallel}$ (s)')
    plt.xlabel('generation')
    plt.semilogy(generations, params[:, 0], '.-', label=label+'trap #1')
    if traps >= 2:
        plt.semilogy(generations, params[:, 1], '.-', label=label+'trap #2')
    if traps >= 3:
        plt.semilogy(generations, params[:, 2], '.-', label=label+'trap #3')
    if traps >= 4:
        plt.semilogy(generations, params[:, 3], '.-', label=label+'trap #4')
    plt.legend()


def champion_density_evolution(generations, params, traps, label=''):
    """

    :return:
    """
    # plt.figure()
    plt.ylabel(r'$n_{t}^{parallel}$ (traps/pixel)')
    plt.xlabel('generation')
    plt.semilogy(generations, params[:, traps], '.-', label=label+'trap #1')
    if traps >= 2:
        plt.semilogy(generations, params[:, traps + 1], '.-', label=label+'trap #2')
    if traps >= 3:
        plt.semilogy(generations, params[:, traps + 2], '.-', label=label+'trap #3')
    if traps >= 4:
        plt.semilogy(generations, params[:, traps + 3], '.-', label=label+'trap #4')
    plt.legend()


def cdm_validation():
    """TBW.

    :return:
    """
    number_of_transfers = 1552

    injection_profile = np.loadtxt('../data/for-david/cdm-input.txt', dtype=float)
    injection_profile = injection_profile.reshape((len(injection_profile), 1))
    injection_profile = [injection_profile]

    target_output = np.loadtxt('../data/for-david/cdm-output-pCTI-1trapspecies.txt', dtype=float)
    target_output = target_output.reshape((len(target_output), 1))
    target_output = [target_output]

    t = 947.22e-6                   # s
    fwc = 1.e6                      # e-
    vg = 1.62e-10                   # cm**3 (half volume!)
    vth = 1.866029409893778e7       # cm/s, from Thibaut's jupyter notebook
    # vth = 1.2175e7                # cm/s,
    sigma = 5.e-16                  # cm**2 (for all traps)
    parameters = ['tr_p', 'nt_p', 'beta_p']
    traps = 1
    tr = 0.09472207122546614        # s
    nt = 10.                        # trap/pixel
    beta = 0.3                      #

    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)

    cdm.charge_injection(True)
    # cdm.charge_injection(False)                        # TODO - JUST A TEST!!!

    cdm.set_dimensions(para_transfers=number_of_transfers)
    # cdm.set_dimensions(para_transfers=number_of_transfers, ystart=number_of_transfers)     # TODO - JUST A TEST!!!

    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)

    out = cdm.run_cdm(np.array([tr, nt, beta]), 0)

    plt.figure()
    plot_1d_profile(array=injection_profile[0], m='-', label='injected')
    plot_1d_profile(array=target_output[0], m='.', label='target')
    plot_1d_profile(array=out, m='--', label='cdm output')
    plt.xlabel(r'Parallel transfer period (947.22 $\mu$s)')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    plt.figure()
    plot_residuals(data=out, data2=target_output[0], label='')
    plt.xlabel(r'Parallel transfer period (947.22 $\mu$s)')
    plt.ylabel(r'CCD signal difference (e$^{-}$)')

    plt.figure()
    plot_1d_profile_lin(array=injection_profile[0], m='-', label='injected')
    plot_1d_profile_lin(array=target_output[0], m='.', label='target')
    plot_1d_profile_lin(array=out, m='--', label='cdm output')
    plt.xlabel(r'Parallel transfer period (947.22 $\mu$s)')
    plt.ylabel(r'CCD signal (e$^{-}$)')

    plt.show()


def old_plotting():
    """TBW.

    :return:
    """

    # irrad = 'warm'
    irrad = 'cold'
    # irrad = 'test'

    # plot_algo = True
    # plot_algo = False

    read_data = True
    generate_data = False
    tofile = False
    noise = False

    traps = None
    cx_goal = None
    # result_tr_p, result_nt_p, result_beta_p = None, None, None
    injection_profile, target_output, target_error = None, None, None
    gdpot = None
    fit_path = None
    # fit_results_path = None
    target_start_fit, target_end_fit = None, None
    sim_start_fit, sim_end_fit = None, None

    if irrad == 'test':
        traps = 4
        # gen = 100
        gdpot = ['15.5V', '16.5V', '18.5V', '19.5V']
        result_tr_p = np.array([9.e-04, 8.e-03, 3.e-02, 3.e-01])
        result_nt_p = np.array([8.e-02, 5.e-01, 3.e+01, 5.e-00])
        result_beta_p = 0.3
        cx_goal = np.hstack((result_tr_p, result_nt_p, result_beta_p))

        fit_results_path = './'
        fit_path = fit_results_path + 'fit.out'
        fit_range_length = 150
        target_start_fit, target_end_fit = 1102, 1102 + fit_range_length
        sim_start_fit, sim_end_fit = 1102, 1102 + fit_range_length

    # # ### COLD results with best fitness per run ###
    # elif irrad == 'cold':
    #     gdpot = ['15.5V', '16.5V', '18.5V', '19.5V']
    #     traps = 4
    #     # fit_path = r'C:\dev\work\cdm\calibration\fit.out'
    #     result_tr_p = np.array([1.62460673e-04,   1.66121662e-03,  1.12176017e-02,  9.68597271e-02])
    #     result_nt_p = np.array([4.69459672e-01,   5.05424677e-01,  2.50960907e+00,  2.22881410e+01])
    #     result_beta_p = 0.3579
    #     cx_goal = np.hstack((result_tr_p, result_nt_p, result_beta_p))
    #     targ_offset = 1052  # if all the 3 charge blocks
    #     # targ_offset = 0     # if only last charge block
    #     fit_results_path = './'
    #
    # # ### WARM results with best fitness per run ###
    # elif irrad == 'warm':
    #     gdpot = ['15V', '16V', '18V', '19V']

    # thr = 5000
    # first, last = 0, 300

    if irrad == 'test':
        injection_profile, target_output = read_test_data(data_path='../data/noisy_cdm_valid/')

    elif irrad == 'cold':
        # fit_results_path = './'
        fit_results_path = '../data/results/plato_cold/runs_w_new_inj_and_normalization/job_s2436/'
        fit_path = fit_results_path + 'fit.out'
        data_path = '../data/plato-target-data/'
        # if only last charge block
        # injection_profile, target_output, target_error = read_cold_data(data_path=data_path,
        #                                                                 start=first, end=last, thr=thr)
        # if all the 3 charge blocks
        data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
        injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                        start=None, end=None)

    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16      # cm**2 (for all traps)

    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))

    if read_data and not generate_data:
        raise NotImplementedError()
        fitted_data = read_fit_data(fit_path)  # TODO
        # pass
    elif not read_data and generate_data:
        fitted_data = cdm_outputs(cdm, cx_goal, traps=traps, gdpot=gdpot, save2file=tofile)
        if noise:
            fitted_data = add_noise(fitted_data, gdpot, fpath='../data/noisy_cdm_valid/plato_cdm_4trap_noise_sig',
                                    uni='const', sigma=10, seed=12421351)
    else:
        raise AttributeError()

    # print('\nBest fitted curve:')
    # fitness0 = cdm.least_squares(fitted_data[0], dataset=0)
    # fitness1 = cdm.least_squares(fitted_data[1], dataset=1)
    # fitness2 = cdm.least_squares(fitted_data[2], dataset=2)
    # fitness3 = cdm.least_squares(fitted_data[3], dataset=3)
    # print('dataset[0] fitness = %.3f' % fitness0)
    # print('dataset[1] fitness = %.3f' % fitness1)
    # print('dataset[2] fitness = %.3f' % fitness2)
    # print('dataset[3] fitness = %.3f' % fitness3)
    # fsum = fitness0 + fitness1 + fitness2 + fitness3
    # print('sum of fitnesses   = %.3f' % fsum)
    #
    # print('\nMinimum overall fitness limit we want to reach:')
    # fitness_goal = cdm.fitness_evaluation(cx_goal)
    # print('overall fitness goal = %.3f' % fitness_goal[0],
    #       '\tdifference = %.3f' % (fsum - fitness_goal[0]))

    # if plot_algo:
    #
    #     data = []
    #     filelist = glob.glob(fit_results_path + 'champion_id*.out')
    #     for file in filelist:
    #         data += [np.loadtxt(file)]
    #
    #     nn = len(filelist)
    #     generations = []
    #     fitness = []
    #     params = []
    #     for i in range(nn):
    #         generations += [data[i][:, 0]]
    #         fitness += [data[i][:, 1]]
    #         params += [data[i][:, 2:]]
    #
    #     plt.figure()
    #     plt.title('Fitness function of champion')
    #     plt.xlabel('generation')
    #     plt.ylabel('f(x)')
    #     for i in range(nn):
    #         plt.semilogy(generations[i], fitness[i], '.-', label=str(i))
    #     plt.legend()
    #
    #     plt.figure()
    #     for i in range(nn):
    #         champion_rel_time_evolution(generations[i], params[i], traps, label=str(i)+', ')
    #
    #     plt.figure()
    #     for i in range(nn):
    #         champion_density_evolution(generations[i], params[i], traps, label=str(i)+', ')
    #
    #     plt.figure()
    #     plt.title('Best beta parameter')
    #     plt.ylabel(r'$\beta^{parallel}$')
    #     plt.xlabel('generation')
    #     for i in range(nn):
    #         plt.plot(generations[i], params[i][:, 2 * traps], '.-', label=str(i))
    #     plt.legend()
    #
    #     file = fit_results_path + 'fitness_sga.dat'
    #     file2 = fit_results_path + 'fitness_sga.dat'
    #     fitness_sga = np.loadtxt(file)
    #     params_sga = np.loadtxt(file2)
    #     fitness_simplex = None
    #     params_simplex = None
    #     if (fitness_simplex and params_simplex) is not None:
    #         fitness = np.concatenate((fitness_sga, fitness_simplex))
    #         fitness[len(fitness_sga):, 0] = max(fitness_sga[:, 0]) + 1 + fitness_simplex[:, 0]
    #         params = np.concatenate((params_sga, params_simplex))
    #         params[len(params_sga):, 0] = max(params_sga[:, 0]) + 1 + params_simplex[:, 0]
    #     else:
    #         fitness = fitness_sga
    #         params = params_sga
    #
    #     tr_p = []
    #     nt_p = []
    #     # line_x = np.array([fitness[0, 0], np.max(fitness[:, 0]) + 10])
    #     line_x = np.array([generations[0], np.max(generations[-1]) + 10])
    #     tr_p += [result_tr_p[0] * np.ones(2)]
    #     nt_p += [result_nt_p[0] * np.ones(2)]
    #     if traps >= 2:
    #         tr_p += [result_tr_p[1] * np.ones(2)]
    #         nt_p += [result_nt_p[1] * np.ones(2)]
    #     if traps >= 3:
    #         tr_p += [result_tr_p[2] * np.ones(2)]
    #         nt_p += [result_nt_p[2] * np.ones(2)]
    #     if traps >= 4:
    #         tr_p += [result_tr_p[3] * np.ones(2)]
    #         nt_p += [result_nt_p[3] * np.ones(2)]
    #     beta_p = result_beta_p * np.ones(2)
    #
    #     release_time_evolution(params, tr_p, line_x)
    #     density_evolution(params, nt_p, line_x)
    #
    #     plt.figure()
    #     plt.title('Fitness function')
    #     plt.xlabel('individuals')
    #     plt.ylabel('f(x)')
    #     plt.semilogy(fitness[:, 0], fitness[:, 1], 'r.')
    #
    #     plt.figure()
    #     plt.title('Beta parameter')
    #     plt.ylabel(r'$\beta^{parallel}$')
    #     plt.xlabel('individuals')
    #     plt.plot(params[:, 0], params[:, 2 * traps + 1], '.', label='dataset #1')
    #     plt.plot(line_x, beta_p, '-', label='champion, dataset #1')
    #     plt.legend()

    plt.figure()
    targ_offset = 1052
    plot_1d_profile_with_err(array=target_output[0], error=target_error[0],
                             offset=targ_offset, label='target data, 15.5V')
    plot_1d_profile_with_err(array=target_output[1], error=target_error[1],
                             offset=targ_offset, label='target data, 16.5V')
    plot_1d_profile_with_err(array=target_output[2], error=target_error[2],
                             offset=targ_offset, label='target data, 18.5V')
    plot_1d_profile_with_err(array=target_output[3], error=target_error[3],
                             offset=targ_offset, label='target data, 19.5V')
    # plot_1d_profile(array=target_output[0], offset=targ_offset, m='.', label='target data, 15.5V')
    # plot_1d_profile(array=target_output[1], offset=targ_offset, m='.', label='target data, 16.5V')
    # plot_1d_profile(array=target_output[2], offset=targ_offset, m='.', label='target data, 18.5V')
    # plot_1d_profile(array=target_output[3], offset=targ_offset, m='.', label='target data, 19.5V')
    # plot_1d_profile(target_output[0], m='.', label='target data, 15.5V')
    # plot_1d_profile(target_output[1], m='.', label='target data, 16.5V')
    # plot_1d_profile(target_output[2], m='.', label='target data, 18.5V')
    # plot_1d_profile(target_output[3], m='.', label='target data, 19.5V')
    # plot_1d_profile(injection_profile[0], label='injected, 15.5V')
    # plot_1d_profile(injection_profile[1], label='injected, 16.5V')
    # plot_1d_profile(injection_profile[2], label='injected, 18.5V')
    # plot_1d_profile(injection_profile[3], label='injected, 19.5V')
    plot_1d_profile(fitted_data[0], label='fitted curve, 15.5V')
    plot_1d_profile(fitted_data[1], label='fitted curve, 16.5V')
    plot_1d_profile(fitted_data[2], label='fitted curve, 18.5V')
    plot_1d_profile(fitted_data[3], label='fitted curve, 19.5V')
    # plt.xlabel('parallel pixel location')
    plt.xlabel(r'Parallel transfer period (947.22 $\mu$s)')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    if irrad == 'cold':
        # plt.title('Fitted parallel CTI profiles, PLATO cold irrad. data')
        plt.title('Measured parallel CTI profiles with error, PLATO cold irrad.')
    elif irrad == 'warm':
        # plt.title('Fitted parallel CTI profiles, PLATO warm irrad. data')
        plt.title('Measured parallel CTI profiles with error,, PLATO warm irrad.')
    ax = plt.gca()
    ax.legend(loc='upper right')

    plt.figure()
    # plot_residuals(data=fitted_data[0][targ_offset:targ_offset+len(target_output[0])],
    #                data2=target_output[0], label='gd=15.5V')
    # plot_residuals(data=fitted_data[1][targ_offset:targ_offset+len(target_output[1])],
    #                data2=target_output[1], label='gd=16.5V')
    # plot_residuals(data=fitted_data[2][targ_offset:targ_offset+len(target_output[2])],
    #                data2=target_output[2], label='gd=18.5V')
    # plot_residuals(data=fitted_data[3][targ_offset:targ_offset+len(target_output[3])],
    #                data2=target_output[3], label='gd=19.5V')
    plot_residuals(data=fitted_data[0][1052:1552], data2=target_output[0], label='gd=15.5V')
    plot_residuals(data=fitted_data[1][1052:1552], data2=target_output[1], label='gd=16.5V')
    plot_residuals(data=fitted_data[2][1052:1552], data2=target_output[2], label='gd=18.5V')
    plot_residuals(data=fitted_data[3][1052:1552], data2=target_output[3], label='gd=19.5V')
    plt.xlabel(r'Parallel transfer period (947.22 $\mu$s)')
    plt.ylabel(r'CCD signal difference (e$^{-}$)')
    if irrad == 'cold':
        plt.title('Residuals of fitted and target parallel CTI profiles, PLATO cold irrad. data')
    elif irrad == 'warm':
        plt.title('Residuals of fitted and target parallel CTI profiles, PLATO warm irrad. data')

    plt.show()


def old_analysis():
    """TBW.

    :return:
    """

    traps = 4
    gen = 2000
    # gdpot = ['15.5V', '16.5V', '18.5V', '19.5V']
    result_tr_p = np.array([9.e-04, 8.e-03, 3.e-02, 3.e-01])
    result_nt_p = np.array([8.e-02, 5.e-01, 3.e+01, 5.e-00])
    result_beta_p = 0.3
    cx_goal = np.hstack((result_tr_p, result_nt_p, result_beta_p))

    fit_results_path = '../data/results/plato_cold/runs_w_new_inj_and_normalization/job_s2436/'
    fit_path = fit_results_path + 'fit.out'

    fit_range_length = 150
    target_start_fit, target_end_fit = 1102, 1102 + fit_range_length
    sim_start_fit, sim_end_fit = 1102, 1102 + fit_range_length

    # if irrad == 'test':
    injection_profile, target_output = read_test_data(data_path='../data/noisy_cdm_valid/')

    winner_fitness = []
    winner_params = []

    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6  # s
    fwc = 1.e6  # e-
    vg = 1.62e-10  # cm**3 (half volume!)
    vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16  # cm**2 (for all traps)

    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))

    # $$$  FITTED CURVES $$$
    raise NotImplementedError()
    fitted_data = read_fit_data(fit_path) # TODO

    print('\nBest fitted curve:')
    fitness0 = cdm.least_squares(fitted_data[0], dataset=0)
    fitness1 = cdm.least_squares(fitted_data[1], dataset=1)
    fitness2 = cdm.least_squares(fitted_data[2], dataset=2)
    fitness3 = cdm.least_squares(fitted_data[3], dataset=3)
    print('dataset[0] fitness = %.3f' % fitness0)
    print('dataset[1] fitness = %.3f' % fitness1)
    print('dataset[2] fitness = %.3f' % fitness2)
    print('dataset[3] fitness = %.3f' % fitness3)
    fsum = fitness0 + fitness1 + fitness2 + fitness3
    print('sum of fitnesses   = %.3f' % fsum)

    # print('\nMinimum overall fitness limit we want to reach:')
    fitness_goal = cdm.fitness_evaluation(cx_goal)
    fitness_goal = fitness_goal[0]
    print('overall fitness goal = %.3f' % fitness_goal, '\tdifference = %.3f' % (fsum - fitness_goal))

    # plt.figure()
    # plot_1d_profile(target_output[0], m='.', label='target data, 15.5V')
    # plot_1d_profile(target_output[1], m='.', label='target data, 16.5V')
    # plot_1d_profile(target_output[2], m='.', label='target data, 18.5V')
    # plot_1d_profile(target_output[3], m='.', label='target data, 19.5V')
    # plot_1d_profile(injection_profile[0])
    # plot_1d_profile(injection_profile[1])
    # plot_1d_profile(injection_profile[2])
    # plot_1d_profile(injection_profile[3])
    # plot_1d_profile(fitted_data[0], label='fitted curve, 15.5V')
    # plot_1d_profile(fitted_data[1], label='fitted curve, 16.5V')
    # plot_1d_profile(fitted_data[2], label='fitted curve, 18.5V')
    # plot_1d_profile(fitted_data[3], label='fitted curve, 19.5V')
    # plt.xlabel(r'Parallel transfer periods')
    # plt.ylabel(r'CCD signal (e$^{-}$)')
    # plt.title('Fitted parallel CTI profiles')
    # ax = plt.gca()
    # ax.legend(loc='upper right')
    #
    # plt.figure()
    # plot_residuals(data=fitted_data[0], data2=target_output[0], label='gd=15.5V')
    # plot_residuals(data=fitted_data[1], data2=target_output[1], label='gd=16.5V')
    # plot_residuals(data=fitted_data[2], data2=target_output[2], label='gd=18.5V')
    # plot_residuals(data=fitted_data[3], data2=target_output[3], label='gd=19.5V')
    # plt.xlabel(r'Parallel transfer periods')
    # plt.ylabel(r'CCD signal difference (e$^{-}$)')
    # plt.title('Residuals of fitted and target parallel CTI profiles')

    tr_p = []
    nt_p = []
    # line_x = np.array([generations[0][0], np.max(generations[0][-1]) + 5])
    line_x = np.array([0, gen])
    tr_p += [result_tr_p[0] * np.ones(2)]
    nt_p += [result_nt_p[0] * np.ones(2)]
    if traps >= 2:
        tr_p += [result_tr_p[1] * np.ones(2)]
        nt_p += [result_nt_p[1] * np.ones(2)]
    if traps >= 3:
        tr_p += [result_tr_p[2] * np.ones(2)]
        nt_p += [result_nt_p[2] * np.ones(2)]
    if traps >= 4:
        tr_p += [result_tr_p[3] * np.ones(2)]
        nt_p += [result_nt_p[3] * np.ones(2)]
    beta_p = result_beta_p * np.ones(2)
    ftn_goal = fitness_goal * np.ones(2)

    # $$$  EVOLUTION  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # evol_results_path = fit_results_path
    # job_list = ['.']  # , 'test_job4'
    # job_list = ['']  # , 'test_job4'
    # job_list = ['test_job10', 'test_job11', 'test_job12', 'test_job13', 'test_job14']
    job_list = ['job_s2436']
    run_path = '../data/results/plato_cold/runs_w_new_inj_and_normalization/'
    # run_path = '../data/noisy_cdm_valid_4trap_outputs/run_pop1k_gen1000/'
    # pathhh = '../data/noisy_cdm_valid_4trap_outputs/test/'
    # job_list = ['test_job0', 'test_job2', 'test_job3']  # , 'test_job4'
    # job_list = ['test_job2', 'test_job21', 'test_job22', 'test_job23']
    nn = None
    generations = []
    fevals = []
    fitness = []

    for sim in job_list:
        evol_results_path = run_path + sim + '/'

        # data, nn = read_data_from_all_files(evol_results_path, 'champion_id*.out')
        data, filelist = read_data_from_all_files(evol_results_path, 'run.out')
        nn = len(filelist)

        generations = []
        fevals = []
        fitness = []
        params = []
        glob_min_f = 1e20
        glob_min_f_ind = None
        glob_min_f_isl = None
        for i in range(nn):
            # generations += [data[i][:, 0]]
            # fitness += [data[i][:, 1]]
            # params += [data[i][:, 2:]]
            generations += [data[i][:, 0]]
            fevals += [data[i][:, 1]]
            fitness += [data[i][:, 2]]
            params += [data[i][:, 3:]]

            isl_min_f_ind = np.argmin(fitness[i][:])
            isl_min_f = fitness[i][isl_min_f_ind]
            if isl_min_f < glob_min_f:
                glob_min_f = isl_min_f
                glob_min_f_ind = isl_min_f_ind
                glob_min_f_isl = i

        # print(glob_min_f_isl)
        # print(glob_min_f_ind)
        # print(glob_min_f)

        winner_ind = glob_min_f_isl   # index of the winner island
        winner_fitness += [fitness[winner_ind]]
        winner_params += [params[winner_ind]]

        plt.figure()
        plt.title('Trap release times, best island')
        champion_rel_time_evolution(generations=generations[winner_ind], params=params[winner_ind], traps=traps, label='best, ')

        plt.figure()
        plt.title('Trap densities, best island')
        champion_density_evolution(generations=generations[winner_ind], params=params[winner_ind], traps=traps, label='best, ')

        plt.figure()
        plt.title('Fitness function, best island')
        plt.xlabel('individuals')
        plt.ylabel('f(x)')
        plt.semilogy(generations[winner_ind], fitness[winner_ind], '.-')
        plt.plot(line_x, ftn_goal, '-', label='goal')
        plt.legend()

        plt.figure()
        plt.title('Beta parameter, best island')
        plt.ylabel(r'$\beta^{parallel}$')
        plt.xlabel('individuals')
        plt.plot(generations[winner_ind], params[winner_ind][:, 2 * traps], '.-', label='best')
        plt.plot(line_x, beta_p, '-', label='goal')
        plt.legend()

        #################

        plt.figure()
        plt.title('Fitness function, all islands')
        plt.xlabel('generation')
        plt.ylabel('f(x)')
        for i in range(nn):
            plt.semilogy(generations[i], fitness[i], '.-', label=str(i))
        plt.plot(line_x, ftn_goal, '-', label='goal')
        plt.legend()

        plt.figure()
        plt.title('Trap release times, all islands')
        for i in range(nn):
            champion_rel_time_evolution(generations[i], params[i], traps, label=str(i) + ', ')

        plt.figure()
        plt.title('Trap densities, all islands')
        for i in range(nn):
            champion_density_evolution(generations[i], params[i], traps, label=str(i) + ', ')

        plt.figure()
        plt.title('Beta parameter, all islands')
        plt.ylabel(r'$\beta^{parallel}$')
        plt.xlabel('generation')
        for i in range(nn):
            plt.plot(generations[i], params[i][:, 2 * traps], '.-', label=str(i))
        plt.plot(line_x, beta_p, '-', label='goal')
        plt.legend()

    plt.show()


def read_data_from_all_files(path, filename, start=None):
    """

    :return:
    """
    data = []
    filelist = glob.glob(path + filename)
    if filelist:
        for file in filelist:
            data += [np.loadtxt(file, comments=['   Gen:', 'Exit'])[start:, :]]
    else:
        raise FileNotFoundError()
    return data, filelist


def read_data_from_all_files_into_array(path, filename, start=None):
    """

    :return:
    """
    data = np.array([])
    filelist = glob.glob(path + filename)
    if filelist:
        for file in filelist:
            if len(data) == 0:
                data = np.loadtxt(file)[start:, :]
            else:
                data = np.vstack((data, np.loadtxt(file)[start:, :]))
    else:
        raise FileNotFoundError()
    return data, filelist


def sensitivity_analysis(data_path):
    """TBW.

    :return:
    """
    traps = 4

    # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.0V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.0V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.0V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.0V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
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

    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                    start=None, end=None)

    # fit_range_length = 150
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16              # cm**2 (for all traps)
    # cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_normalization()

    ###################################
    # SENSITIVITY ANALYSIS FOR ONE TRAP
    ###################################
    var_trp = 1.60920476209271e-04
    var_ntp = 9.99999999999978e+01
    result_tr_p = np.array([1.61898462611810e-03, 1.05290728598730e-02, 9.23196016400425e-02, var_trp])
    result_nt_p = np.array([5.03718227323677e-01, 4.50959789646447e-01, 2.48538432207972e+00, var_ntp])
    result_beta_p = [0.357715]
    cx_sensitivity = np.hstack((result_tr_p, result_nt_p, result_beta_p))

    idataset = 0  # only first dataset, 15.5V
    plt.figure()
    plot_1d_profile(target_output[0][0:300], m='.', label='target data, 15.5V')
    result = cdm.run_cdm(cx_sensitivity, dataset=idataset)
    fitness = cdm.least_squares(result, dataset=idataset)
    plot_1d_profile(result[1052:1352], m='x', label='original fit')
    # variable_lst = np.array([var_trp])
    variable_lst = np.array([var_ntp])
    fitness_lst = np.array([fitness])

    # for factor in np.linspace(start=0.1, stop=10., num=10):
    for factor in np.logspace(start=np.log10(0.01), stop=np.log10(10.), num=10):
        print('factor : ', factor)

        # variable = var_trp * factor
        variable = var_ntp * factor

        result_tr_p = np.array([1.61898462611810e-03, 1.05290728598730e-02, 9.23196016400425e-02, var_trp])
        result_nt_p = np.array([5.03718227323677e-01, 4.50959789646447e-01, 2.48538432207972e+00, variable])
        result_beta_p = [0.357715]
        # Fitness:             [1.567717e+03]
        cx_sensitivity = np.hstack((result_tr_p, result_nt_p, result_beta_p))

        result = cdm.run_cdm(cx_sensitivity, dataset=idataset)
        fitness = cdm.least_squares(result, dataset=idataset)
        # plot_1d_profile(result[1052:1352], label=r't$_r$ = %.2e s' % variable)
        plot_1d_profile(result[1052:1352], label=r'n$_t$ = %.2e' % variable)
        variable_lst = np.append(variable_lst, variable)
        fitness_lst = np.append(fitness_lst, fitness)

    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    # plt.title('15.5V data fitted with different trap release times for one trap')
    plt.title('15.5V data fitted with different trap density for one trap')

    plt.figure()
    plt.loglog(variable_lst, fitness_lst, '.')
    # plt.xlabel('Trap release time (sec)')
    plt.xlabel('Trap density (traps/half pixel)')
    plt.ylabel('Fitness')
    plt.title('Sensitivity, 1 out of 4 trap species, 15.5V data')
    ###################################

    plt.show()


def cdm_fwc_sensitivity_analysis(data_path):
    """TBW.

    :return:
    """
    traps = 4

    # data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']
    # gd_lst = [15.5, 16.5, 18.5, 19.5]
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)

    # fit_range_length = 150
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    # fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16              # cm**2 (for all traps)
    # cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    # cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_normalization()

    result_tr_p = np.array([1.017E-03, 4.362E-03, 3.032E-02, 2.348E-01])
    result_nt_p = np.array([2.965E-01, 3.579E-01, 5.756E-01, 2.682E+00])
    result_beta_p = [0.342052]
    cx_sensitivity = np.hstack((result_tr_p, result_nt_p, result_beta_p))

    idataset = 0  # only first dataset, 15.5V

    plt.figure()
    plot_1d_profile(target_output[0], m='.', label='target data, 15.5V')

    variable_lst = [6e5, 7e5, 8e5, 9e5, 9.5e5, 1e6, 1.05e6, 1.1e6, 1.15e6]
    fitness_lst = np.array([])
    for variable in variable_lst:
        print('variable : ', variable)

        cdm.set_parallel_parameters(t=t, vg=vg, fwc=variable, vth=vth, sigma=sigma)

        result = cdm.run_cdm(cx_sensitivity, dataset=idataset)
        fitness = cdm.least_squares(result, dataset=idataset)

        plot_1d_profile(result[1052:1352], m='-', label=r'FWC = %.2e' % variable)
        fitness_lst = np.append(fitness_lst, fitness)

    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    plt.title('CDM output sensitivity in function of Full Well Capacity, 15.5V cold data')

    plt.figure()
    plt.loglog(variable_lst, fitness_lst, '.')
    plt.xlabel(r'FWC (e$^{-}$)')
    plt.ylabel('Fitness')
    plt.title('Fitness sensitivity on FWC, 15.5V cold data')
    plt.ylim([1, 20])

    plt.show()


def cdm_crosssection_sensitivity_analysis(data_path):
    """TBW.

    :return:
    """
    traps = 4

    # data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
    #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']
    # gd_lst = [15.5, 16.5, 18.5, 19.5]
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)

    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    # sigma = 5.e-16              # cm**2 (for all traps)
    # cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    # cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_normalization()

    # sigma = 5.e-16  # cm**2 (for all traps)

    # Traps, cold, job_wt1_wa1, cf = 4.669e+01
    result_tr_p = np.array([1.373e-03,  4.652e-03,  3.633e-02,  2.979e-01])
    result_nt_p = np.array([1.921e-01,  3.005e-01,  6.705e-01,  2.393e+00])
    result_beta_p = [0.291664]
    cx_sensitivity = np.hstack((result_tr_p, result_nt_p, result_beta_p))

    idataset = 0  # only first dataset, 15.5V
    # idataset = 1  # only first dataset, 16.5V
    # idataset = 2  # only first dataset, 18.5V
    # idataset = 3  # only last dataset, 19.5V

    # plt.figure()
    # plot_1d_profile(target_output[idataset], m='.', label='target data, 15.5V')
    # plot_1d_profile(target_output[idataset], m='.', label='target data, 16.5V')
    # plot_1d_profile(target_output[idataset], m='.', label='target data, 18.5V')
    # plot_1d_profile(target_output[idataset], m='.', label='target data, 19.5V')

    # variable_lst = []
    # sigma_lst = []
    sigma_lst = 10 ** np.linspace(-22, -14, 100)

    # fitness_lst = np.array([])
    # fitness_lst1 = np.array([])
    # fitness_lst2 = np.array([])
    # fitness_lst3 = np.array([])
    # fitness_lst4 = np.array([])
    # sigma_exp
    plt.figure()
    sp = 221
    for trs in range(1, 5):
        plt.subplot(sp)
        sp += 1
        fitness_lst1 = np.array([])
        fitness_lst2 = np.array([])
        fitness_lst3 = np.array([])
        fitness_lst4 = np.array([])
        # for sigma_exp in range(-21, -14):
        for sigma in sigma_lst:
            # sigma = 10 ** sigma_exp
            # sigma_lst += [sigma]
            print('sigma: %1.1e' % sigma)
            print('trap specie: ', trs)

            if trs == 1:
                sigma_array = np.array([sigma, 5.e-16, 5.e-16, 5.e-16])
            elif trs == 2:
                sigma_array = np.array([5.e-16, sigma, 5.e-16, 5.e-16])
            elif trs == 3:
                sigma_array = np.array([5.e-16, 5.e-16, sigma, 5.e-16])
            elif trs == 4:
                sigma_array = np.array([5.e-16, 5.e-16, 5.e-16, sigma])
            else:
                sigma_array = sigma   # for all the traps
            cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma_array)

            # result = cdm.run_cdm(cx_sensitivity, dataset=idataset)
            # fitness = cdm.least_squares(result, dataset=idataset)

            result = cdm.run_cdm(cx_sensitivity, dataset=0)
            fitness1 = cdm.least_squares(result, dataset=0)
            result = cdm.run_cdm(cx_sensitivity, dataset=1)
            fitness2 = cdm.least_squares(result, dataset=1)
            result = cdm.run_cdm(cx_sensitivity, dataset=2)
            fitness3 = cdm.least_squares(result, dataset=2)
            result = cdm.run_cdm(cx_sensitivity, dataset=3)
            fitness4 = cdm.least_squares(result, dataset=3)

            # plot_1d_profile(result[1052:1453], m='-', label=r'$\sigma_{all}$ = %1.e' % sigma)

            fitness_lst1 = np.append(fitness_lst1, fitness1)
            fitness_lst2 = np.append(fitness_lst2, fitness2)
            fitness_lst3 = np.append(fitness_lst3, fitness3)
            fitness_lst4 = np.append(fitness_lst4, fitness4)
        #
        # plt.xlabel(r'Parallel transfer periods')
        # plt.ylabel(r'CCD signal (e$^{-}$)')
        # # plt.title(r'CDM output sensitivity on $\sigma$, 15.5V cold data')
        # # plt.title(r'CDM output sensitivity on $\sigma$, 16.5V cold data')
        # plt.title(r'CDM output sensitivity on $\sigma$, 18.5V cold data')
        # # plt.title(r'CDM output sensitivity on $\sigma$, 19.5V cold data')
        # plt.ylim([1e0, 1e2])

        # plt.figure()
        # # plt.semilogx(sigma_lst, fitness_lst, '.')
        # plt.loglog(sigma_lst, fitness_lst, '.')
        plt.loglog(sigma_lst, fitness_lst1, '.-', label='15.5V')
        plt.loglog(sigma_lst, fitness_lst2, '.-', label='16.5V')
        plt.loglog(sigma_lst, fitness_lst3, '.-', label='18.5V')
        plt.loglog(sigma_lst, fitness_lst4, '.-', label='19.5V')
        plt.legend()
        if trs == 3 or trs == 4:
            plt.xlabel(r'$\sigma$ capture cross-section (cm$^{2}$)')
        plt.ylabel('Fitness')
        # plt.title('Fitness sensitivity on capture cross-section, 15.5V cold data, all traps')
        # plt.title('Fitness sensitivity on capture cross-section, cold data, all traps')
        # plt.title('Fitness sensitivity on capture cross-section, cold data, trap #' + str(trs))
        plt.title(r'changing $\sigma$ only for trap #' + str(trs) + ' (cold data)')
        plt.ylim([1e0, 1e3])

    plt.show()


def calc_target_fitness_from_error(data_path):
    """TBW.

    :return:
    """
    traps = 4

    gd_lst = [15.0, 16.0, 18.0, 19.0]
    data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']

    # gd_lst = [15.5, 16.5, 18.5, 19.5]
    # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
    #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']

    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)

    # fit_range_length = 150
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length

    # sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16              # cm**2 (for all traps)

    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    # cdm.set_normalization()

    sim_start_fit, sim_end_fit = 51, 51 + fit_range_length
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))

    # err0 = np.array(target_error[0])   # [slice(sim_start_fit, sim_end_fit)])  # convert list to numpy array
    # cdm.set_weighting_function(err0)

    plt.figure()

    for i in range(4):
        # the mean and std. dev of ccd signals were calculated using 5 different data files
        target_error[i] = target_error[i] / np.sqrt(5)      # only for new data! (20 columns)

        plot_1d_profile(target_output[i], m='.', label='mean, ' + str(gd_lst[i]) + 'V')
        plot_1d_profile(np.abs(target_error[i]), m='.', label='std.dev., ' + str(gd_lst[i]) + 'V')
        # plot_1d_profile(target_output[i] + target_error[i], m='.', label='signal+error, ' + str(gd_lst[i]) + 'V')
    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'e$^{-}$')
    plt.title('Mean and std.dev. of measured pCTI profiles, warm irrad.')
    # plt.title('Mean and std.dev. of measured pCTI profiles, cold irrad.')
    ax = plt.gca()
    ax.legend(loc='upper right')

    clp_err = []
    rmv_err = []
    # noise_range = slice(51, 201, 1)
    noise_range = slice(51, 401, 1)
    noise_limit = 20
    print('noise_range: ', noise_range)
    print('noise_limit: ', noise_limit)
    for i in range(4):
        print('dataset (i): ', i)
        # print('np.sum(target_error[i]): ', np.sum(target_error[i]))
        # print('np.sum(target_error[i][noise_range]): ', np.sum(target_error[i][noise_range]))
        print('np.sum(target_error[i]**2):               %1.3e' % np.sum(target_error[i]**2))
        print('np.sum(target_error[i][noise_range]**2):  %1.3e' % np.sum(target_error[i][noise_range]**2))

        clp_err += [np.clip(target_error[i], -1 * noise_limit, noise_limit)]

        wgsfg = np.where(target_error[i] ** 2 > noise_limit ** 2)
        target_error[i][wgsfg] = 0

        rmv_err += [target_error[i]]

        print('np.sum(clp_err[i]**2):                    %1.3e' % np.sum(clp_err[i] ** 2))
        print('np.sum(clp_err[i][noise_range]**2):       %1.3e' % np.sum(clp_err[i][noise_range] ** 2))
        # print('np.sum(err[i]): ', np.sum(err[i]))
        # print('np.sum(err[i][noise_range]): ', np.sum(err[i][noise_range]))
        print('np.sum(rmv_err[i]**2):                    %1.3e' % np.sum(rmv_err[i]**2))
        print('np.sum(rmv_err[i][noise_range]**2):       %1.3e' % np.sum(rmv_err[i][noise_range]**2))



    plt.figure()
    plt.subplot(211)
    for i in range(4):
        plot_1d_profile(rmv_err[i], m='.', label=str(gd_lst[i]) + 'V')
    plt.title('Std.dev. on log & lin scale, large values removed')
    plt.xlabel('')
    plt.ylabel(r'e$^{-}$')
    plt.subplot(212)
    for i in range(4):
        plot_1d_profile_lin(rmv_err[i], m='.', label=str(gd_lst[i]) + 'V')
    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'e$^{-}$')

    # i = 0
    # target_output = [target_output[0]]  #############
    # # for array in target_output:
    # #     # plot_1d_profile(array, m='.', label=str(gd_lst[i]) + 'V')
    # #     # plot_1d_profile_with_err(array, error=err0, label='w err, ' + str(gd_lst[i]) + 'V')
    # #     i += 1
    #
    # i = 0
    # for array in target_output:
    #     # plot_1d_profile(array, m='.', label=str(gd_lst[i]) + 'V')
    #     # plot_1d_profile_with_err(array, error=err0, label='w err, ' + str(gd_lst[i]) + 'V')
    #     i += 1
    # plt.xlabel(r'Parallel transfer periods')
    # plt.ylabel(r'CCD signal (e$^{-}$)')
    # plt.title('Measured parallel CTI profiles (target data), cold irrad.')
    # plt.ylim((1e-1, 1e6))
    # ax = plt.gca()
    # ax.legend(loc='upper right')
    #
    #
    # fitnessleast0 = cdm.least_squares(inp, dataset=0)
    #
    # # fitnessleast1 = cdm.least_squares(target_output[1], dataset=1)
    # # fitnessleast2 = cdm.least_squares(target_output[2], dataset=2)
    # # fitnessleast3 = cdm.least_squares(target_output[3], dataset=3)
    # print('Least-squares fitness values:')
    # print('  dataset[0] fitness = %.3f' % fitnessleast0)
    # # print('  dataset[1] fitness = %.3f' % fitnessleast1)
    # # print('  dataset[2] fitness = %.3f' % fitnessleast2)
    # # print('  dataset[3] fitness = %.3f' % fitnessleast3)
    # # print('  Sum of fitnesses   = %.6e' % (fitnessleast0 + fitnessleast1 + fitnessleast2 + fitnessleast3))



    # err = np.array(target_error[0][slice(sim_start_fit, sim_end_fit)])       # convert list to numpy array
    # cdm.set_weighting_function(err)
    # print('*** Weighting func:')
    #
    # fitnessleast0 = cdm.least_squares(target_output[0], dataset=0)
    # # fitnessleast1 = cdm.least_squares(target_output[1], dataset=1)
    # # fitnessleast2 = cdm.least_squares(target_output[2], dataset=2)
    # # fitnessleast3 = cdm.least_squares(target_output[3], dataset=3)
    # print('Least-squares fitness values:')
    # print('  dataset[0] fitness = %.3f' % fitnessleast0)
    # # print('  dataset[1] fitness = %.3f' % fitnessleast1)
    # # print('  dataset[2] fitness = %.3f' % fitnessleast2)
    # # print('  dataset[3] fitness = %.3f' % fitnessleast3)
    # # print('  Sum of fitnesses   = %.6e' % (fitnessleast0 + fitnessleast1 + fitnessleast2 + fitnessleast3))

def data_plots(data_path):
    """TBW.

    :return:
    """
    traps = 4

    cold_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.0V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd17.0V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd17.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.0V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.0V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']

    warm_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd15.5V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.5V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.5V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.5V.txt',
                  'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']

    c_injection_profile, c_target_output, c_target_error = read_plato_data(data_path=data_path, data_files=cold_files,
                                                                           start=None, end=None)
    w_injection_profile, w_target_output, w_target_error = read_plato_data(data_path=data_path, data_files=warm_files,
                                                                           start=None, end=None)

    c_gd_lst = [15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5]
    w_gd_lst = [15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0]

    i = 0
    plt.figure()
    for array in c_target_output:
        plot_1d_profile(array, m='.', label=str(c_gd_lst[i])+'V')
        i += 1
    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    plt.title('Measured parallel CTI profiles (target data), cold irrad.')
    plt.ylim((1e-1, 1e6))
    ax = plt.gca()
    ax.legend(loc='upper right')

    i = 0
    plt.figure()
    for array in w_target_output:
        plot_1d_profile(array, m='.', label=str(w_gd_lst[i])+'V')
        i += 1
    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    plt.title('Measured parallel CTI profiles (target data), warm irrad.')
    plt.ylim((1e-1, 1e6))
    ax = plt.gca()
    ax.legend(loc='upper right')

    c_signal_max = []
    w_signal_max = []
    plt.figure()
    for i in range(len(c_gd_lst)):
        plot_1d_profile_lin(c_injection_profile[i][1052:1552], m='--', label='cold, '+str(c_gd_lst[i])+'V')
        plot_1d_profile_lin(w_injection_profile[i][1052:1552], m='--', label='warm, '+str(w_gd_lst[i])+'V')
        c_signal_max += [np.max(c_injection_profile[i])]
        w_signal_max += [np.max(w_injection_profile[i])]
    plt.xlabel(r'Parallel transfer periods')
    plt.ylabel(r'CCD signal (e$^{-}$)')
    plt.title('Parallel charge injection profiles created for CDM')
    ax = plt.gca()
    ax.legend(loc='upper right')

    plt.figure()
    plt.semilogy(c_gd_lst, c_signal_max, '.-', label='cold irrad.')
    plt.semilogy(w_gd_lst, w_signal_max, '.-', label='warm irrad.')
    plt.xlabel(r'Guard Drain voltage (V)')
    plt.ylabel(r'CCD signal max. (e$^{-}$)')
    plt.title('PLATO CCD charge injection (CCD280), new data')
    plt.xlim((14.5, 20.0))
    plt.ylim((1e3, 1e6))
    ax = plt.gca()
    ax.legend(loc='upper right')


def fit_plots(data_path, run_path, job_list, irrad):
    """TBW.

    :return:
    """
    traps = 4

    # sns.set()
    # sns.set_style("whitegrid")

    data_files = None
    if irrad == 'cold':
        # gd_lst = [15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5]
        # data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd17.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.0V.txt',
        #               'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
        gd_lst = [15.5, 16.5, 18.5, 19.5]
        data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    elif irrad == 'warm':
        # gd_lst = [15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0]
        # data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd15.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd17.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.5V.txt',
        #               'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']
        gd_lst = [15.0, 16.0, 18.0, 19.0]
        data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']

    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)

    # fit_range_length = 150
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    # parameters = ['tr_p', 'nt_p', 'beta_p']
    parameters = ['tr_p', 'nt_p', 'sigma_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    # sigma = 5.e-16              # cm**2 (for all traps)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=None)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_normalization()

    for job_name in job_list:

        champion_file_path = run_path + job_name + '/champion.out'
        cx, cf = read_champion(champion_file_path)

        # try:
        #     fit_path = run_path + job_name + '/fit.out'
        #     raise NotImplementedError()
        #     fitted_data = read_fit_data(fit_path)  # TODO
        # except FileNotFoundError:
        fitted_data = []
        for i in range(len(target_output)):
            fitted_data += [cdm.run_cdm(cx, dataset=i)]
            # print('File fit.out does not exist!')

        # fitnessleast0 = cdm.least_squares(fitted_data[0], dataset=0)
        # fitnessleast1 = cdm.least_squares(fitted_data[1], dataset=1)
        # fitnessleast2 = cdm.least_squares(fitted_data[2], dataset=2)
        # fitnessleast3 = cdm.least_squares(fitted_data[3], dataset=3)
        # print('Least-squares fitness values:')
        # print('  dataset[0] fitness = %.3f' % fitnessleast0)
        # print('  dataset[1] fitness = %.3f' % fitnessleast1)
        # print('  dataset[2] fitness = %.3f' % fitnessleast2)
        # print('  dataset[3] fitness = %.3f' % fitnessleast3)
        # print('  Sum of fitnesses   = %.6e' % (fitnessleast0 + fitnessleast1 + fitnessleast2 + fitnessleast3))

        # plt.figure()
        # # plot_1d_profile_lin(target_output[0], m='.', col='blue', label='target data, 15.5V')
        # # plot_1d_profile_lin(injection_profile[0][1052:1552], col='blue', m='--', label='injected, 15.5V')
        # plot_1d_profile_lin(target_output[1], m='.', col='orange', label='target data, 16.5V')
        # plot_1d_profile_lin(injection_profile[1][1052:1552], m='--', col='orange', label='injected, 16.5V')
        # # plot_1d_profile_lin(target_output[2], m='.', label='target data, 18.5V')
        # # plot_1d_profile_lin(target_output[3], m='.', label='target data, 19.5V')
        # # plot_1d_profile_lin(injection_profile[2][1052:1552], m='--', label='injected, 18.5V')
        # # plot_1d_profile_lin(injection_profile[3][1052:1552], m='--', label='injected, 19.5V')
        # plt.xlabel(r'Parallel transfer periods')
        # plt.ylabel(r'CCD signal (e$^{-}$)')
        # plt.title('Parallel charge injection profiles created for CDM')
        # # plt.ylim((3.214e+5, 3.224e+5))
        # plt.ylim((1.97700e+5, 1.98400e+5))
        # plt.xlim((-20, 70))
        # ax = plt.gca()
        # ax.legend(loc='upper right')

        plt.figure()
        plt.subplot(211)
        for i in range(len(target_output)):
            plot_1d_profile(target_output[i], m='.', label='target data, '+str(gd_lst[i]) + 'V')
        if len(data_files) == 9:
            plot_1d_profile([0], m='.')
        for i in range(len(target_output)):
            plot_1d_profile(fitted_data[i][1052:1552], label='fitted, '+str(gd_lst[i]) + 'V')
        plt.ylabel(r'CCD signal (e$^{-}$)')
        plt.title('Fitted parallel CTI profiles, ' + str(job_name))
        plt.ylim((1e+0, 1e+3))
        ax = plt.gca()
        ax.legend(loc='upper right')

        # # residual_range = slice(1052, 1551, 1)
        residual_range = slice(1052, 1552, 1)
        plt.subplot(212)
        for i in range(len(target_output)):
            plot_residuals(data=fitted_data[i][residual_range], data2=target_output[i], label=str(gd_lst[i]) + 'V')
        plt.xlabel(r'Parallel transfer periods')
        plt.ylabel(r'Residuals (e$^{-}$)')
        plt.title('Residuals, ' + str(job_name))
        # plt.ylim((-100, 100))
        plt.ylim((-30, 30))
        ax = plt.gca()
        ax.legend(loc='upper right')


def weighting_func_plots(data_path, run_path, job_list, irrad):
    """TBW.

    :return:
    """
    traps = 4

    # sns.set()
    # sns.set_style("whitegrid")

    data_files = None
    if irrad == 'cold':
        gd_lst = [15.5, 16.5, 18.5, 19.5]
        data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                      'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    elif irrad == 'warm':
        gd_lst = [15.0, 16.0, 18.0, 19.0]
        data_files = ['warm/CCD280-14321-24-02-room-temperature-irrad-gd15.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd16.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd18.0V.txt',
                      'warm/CCD280-14321-24-02-room-temperature-irrad-gd19.0V.txt']

    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)

    fit_range_length = 350

    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6       # s
    fwc = 1.e6          # e-
    vg = 1.62e-10       # cm**3 (half volume!)
    vth = 1.866029409893778e7   # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16              # cm**2 (for all traps)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_normalization()

    # COLD Traps, job_s9759, cf = 1.201e+01
    # tr:  9.597e-04  3.716e-03  3.154e-02  6.384e-01
    # nt:  2.945e-01  3.408e-01  7.838e-01  5.269e+00
    # WARM Traps, job_s8456, cf = 7.104e+00
    # tr:  1.889e-03  3.582e-03  1.380e-02  1.297e-01
    # nt:  4.220e-01  1.414e-01  5.253e-01  3.068e+00

    # reltime1 = 6.384e-01
    # reltime2 = 3.154e-02
    # reltime3 = 3.716e-03
    # reltime4 = 9.597e-04
    # dens1 = 1
    # dens2 = 1
    # dens3 = 1
    # dens4 = 1
    # reltime = reltime3

    weighting_func = []
    inv_weighting_func = []

    for job_name in job_list:

        champion_file_path = run_path + job_name + '/champion.out'
        cx, cf = read_champion(champion_file_path)

        fitted_data = []

        x = np.linspace(start=1, stop=fit_range_length+1, num=fit_range_length)
        x = x.reshape(len(x), 1)
        x = np.insert(x, 0, np.zeros(51))

        weighting_func = []

        for i in range(len(target_output)):

            fitted_data += [cdm.run_cdm(cx, dataset=i)]

        # reltime2 = 3.154e-02
        reltimes = np.array([1, 2, 3, 4, 5, 6]) * 1.e-02

        for reltime in reltimes:

            wf = 1-( np.exp(-1 * t * x / reltime) )

            weighting_func = wf.reshape(len(wf), 1)

            plot_1d_profile_lin(weighting_func, label='tau: ' + str(reltime))

        plt.legend()
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Residual weighting function')

        plt.figure()
        plt.subplot(211)

        # target_output = [target_output[0]]

        for i in range(len(target_output)):
            plot_1d_profile(target_output[i], m='.', label='target data, '+str(gd_lst[i]) + 'V')
        for i in range(len(target_output)):
            plot_1d_profile(fitted_data[i][1052:1052+len(target_output[0])], label='fitted, '+str(gd_lst[i]) + 'V')

        plt.ylabel(r'CCD signal (e$^{-}$)')
        plt.title('Fitted parallel CTI profiles, ' + str(job_name))
        plt.ylim((1e+0, 1e+3))
        ax = plt.gca()
        ax.legend(loc='upper right')

        # # residual_range = slice(1052, 1551, 1)
        residual_range = slice(1052, 1552, 1)
        plt.subplot(212)
        for i in range(len(target_output)):
            plot_residuals(data=fitted_data[i][residual_range], data2=target_output[i], label=str(gd_lst[i]) + 'V')
        # for i in range(len(target_output)):
        plot_1d_profile_lin(weighting_func, m='.-', label='weighting func')
        plt.xlabel(r'Parallel transfer periods')
        plt.ylabel(r'Residuals (e$^{-}$)')
        # plt.title('Residuals, ' + str(job_name))
        # plt.ylim((-100, 100))
        plt.ylim((-30, 30))
        ax = plt.gca()
        ax.legend(loc='upper right')


def results_map(run_paths):
    """TBW.

    :return:
    """
    # sns.set()
    sns.set_style("whitegrid")
    # sns.set(style="white")
    plt.figure()
    traps = 4
    i = 0
    trap_df = pd.DataFrame()
    for run_path in run_paths:

        data, filelist = read_data_from_all_files_into_array(run_path, 'champion.out', start=-1)

        fitness = data[:, 1]
        reltime = data[:, 2:2+traps]
        trapdens = data[:, 2+traps:2+traps*2]
        beta = data[:, 2 + traps * 2]

        trap_run_df = pd.DataFrame()
        rows = len(filelist)
        trap_ii = 1
        for trsp in range(traps):
            trapspecie = np.repeat(np.array([trap_ii]), rows).reshape((rows, 1))
            trap_df_new = pd.DataFrame(np.c_[filelist, trapspecie, fitness, reltime[:, trsp], trapdens[:, trsp], beta],
                                       columns=['island', 'trap', 'fitness', 'time', 'density', 'beta'])
            trap_run_df = pd.concat([trap_run_df, trap_df_new], ignore_index=True)
            trap_df = pd.concat([trap_df, trap_df_new], ignore_index=True)
            trap_ii += 1

        label_str = run_path.replace('../data/results/new_plato/', '')
        label_str = label_str.replace('/job_s*/', '')
        label_str = label_str.replace('_', ' ')
        label_str = label_str.replace('/', ', ')
        plt.scatter(pd.to_numeric(trap_run_df['density'].values),
                    pd.to_numeric(trap_run_df['time'].values), label=label_str)
        plt.xlabel('density')
        plt.ylabel('release time')
        plt.title('traps')
        # t = 947.22e-6
        y_lb, y_ub = 947.22e-6, 2.
        x_lb, x_ub = 0.001, 100.
        plt.xlim([x_lb, x_ub])
        plt.ylim([y_lb, y_ub])
        plt.legend(loc='upper left')
        ax = plt.gca()
        ax.set_yscale('log')
        ax.set_xscale('log')


def set_jointplot_axes(ax):
    """

    :param ax:
    :return:
    """
    # x_lb, x_ub = -5, +3
    # y_lb, y_ub = -3.5, +0.5
    t = 947.22e-6
    y_lb, y_ub = np.log10(t), np.log10(2.)
    x_lb, x_ub = np.log10(0.001), np.log10(100.)
    # x_lb, x_ub = np.log10(0.01), np.log10(100.)
    try:
        ax.ax_joint.set_xlim([x_lb, x_ub])
        ax.ax_joint.set_ylim([y_lb, y_ub])
        ax.ax_marg_x.set_xlim([x_lb, x_ub])
        ax.ax_marg_y.set_ylim([y_lb, y_ub])
    except:
        ax.set_xlim([x_lb, x_ub])
        ax.set_ylim([y_lb, y_ub])


def chi_square_map(trap_df, gen):
    """TBW.

    :return:
    """
    sns.set(style="white")

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[trap_df['generation'] == gen],
                    trap_df['log-time'].loc[trap_df['generation'] == gen],
                    zorder=0, n_levels=25,
                    cmap="GnBu_d",
                    cbar=True,
                    shade=True,
                    # shade_lowest=False,
                    shade_lowest=True
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', all traps')
    set_jointplot_axes(g)

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)],
                    zorder=0, n_levels=25,
                    cmap="Reds",
                    shade=False,
                    shade_lowest=False,
                    )
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)],
                    zorder=0, n_levels=25,
                    cmap="Greens",
                    shade=False,
                    shade_lowest=False,
                    )
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)],
                    zorder=0, n_levels=25,
                    cmap="Blues",
                    shade=False,
                    shade_lowest=False,
                    )
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)],
                    zorder=0, n_levels=25,
                    cmap="Purples",
                    shade=False,
                    shade_lowest=False,
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', all traps')
    set_jointplot_axes(g)

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)],
                    zorder=0, n_levels=25,
                    cmap="Reds",
                    cbar=True,
                    shade=True,
                    shade_lowest=False,
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', trap #1')
    set_jointplot_axes(g)

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)],
                    zorder=0, n_levels=25,
                    cmap="Greens",
                    cbar=True,
                    shade=True,
                    shade_lowest=False,
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', trap #2')
    set_jointplot_axes(g)

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)],
                    zorder=0, n_levels=25,
                    cmap="Blues",
                    cbar=True,
                    shade=True,
                    shade_lowest=False,
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', trap #3')
    set_jointplot_axes(g)

    plt.figure()
    g = sns.kdeplot(trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)],
                    trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)],
                    zorder=0, n_levels=25,
                    cmap="Purples",
                    cbar=True,
                    shade=True,
                    shade_lowest=False,
                    )
    plt.title(r'$\chi^2$ map of population at generation ' + str(gen) + ', trap #4')
    set_jointplot_axes(g)

    g = sns.jointplot("log-density", "log-time",
                      data=trap_df.loc[trap_df['generation'] == gen],
                      space=0,
                      marginal_kws=dict(bins=300), s=0.5
                      ).plot_joint(sns.kdeplot,
                                   zorder=0,
                                   n_levels=25,
                                   cmap="GnBu_d",
                                   shade=False,
                                   shade_lowest=False
                                   )
    set_jointplot_axes(g)

    g = sns.jointplot("log-density", "log-time",
                      data=trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)],
                      color="red",
                      space=0,
                      marginal_kws=dict(bins=300), s=0.5
                      ).plot_joint(sns.kdeplot,
                                   zorder=0,
                                   n_levels=25,
                                   cmap="Reds",
                                   shade=False,
                                   shade_lowest=False
                                   )
    set_jointplot_axes(g)
    g = sns.jointplot("log-density", "log-time",
                      data=trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)],
                      color="green",
                      space=0,
                      marginal_kws=dict(bins=300), s=0.5
                      ).plot_joint(sns.kdeplot,
                                   zorder=0,
                                   n_levels=25,
                                   cmap="Greens",
                                   shade=False,
                                   shade_lowest=False
                                   )
    set_jointplot_axes(g)
    g = sns.jointplot("log-density", "log-time",
                      data=trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)],
                      color="blue",
                      space=0,
                      marginal_kws=dict(bins=300), s=0.5
                      ).plot_joint(sns.kdeplot,
                                   zorder=0,
                                   n_levels=25,
                                   cmap="Blues",
                                   shade=False,
                                   shade_lowest=False
                                   )
    set_jointplot_axes(g)
    g = sns.jointplot("log-density", "log-time",
                      data=trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)],
                      color="purple",
                      space=0,
                      marginal_kws=dict(bins=300), s=0.5
                      ).plot_joint(sns.kdeplot,
                                   zorder=0,
                                   n_levels=25,
                                   cmap="Purples",
                                   shade=False,
                                   shade_lowest=False
                                   )
    set_jointplot_axes(g)


def population_dataframe(run_path, traps, gen, add_champion_to_pop, sigma_fitted=False):
    """

    :return:
    """
    df = pd.DataFrame()
    data, filelist = read_data_from_all_files_into_array(run_path, 'population.out')

    generation = data[:, 0]
    selected = np.where(generation == gen)
    rows = len(selected[0])
    generation = data[selected, 0].reshape(rows, 1)
    fitness = data[selected, 1].reshape(rows, 1)
    reltime = data[selected, 2:2 + traps].reshape(rows, traps)
    trapdens = data[selected, 2 + traps:2 + traps * 2].reshape(rows, traps)
    if sigma_fitted:
        sigma = data[selected, 2 + traps * 2:2 + traps * 3].reshape(rows, traps)
        beta = data[selected, 2 + traps * 3].reshape(rows, 1)
    else:
        beta = data[selected, 2 + traps * 2].reshape(rows, 1)

    trap_ii = 1
    for trsp in range(traps):
        trapspecie = np.repeat(np.array([trap_ii]), rows).reshape((rows, 1))
        if sigma_fitted:
            df_new = pd.DataFrame(np.c_[generation, trapspecie, fitness, reltime[:, trsp], trapdens[:, trsp],
                                        np.log10(reltime[:, trsp]), np.log10(trapdens[:, trsp]),
                                        sigma[:, trsp], np.log10(sigma[:, trsp]), beta],
                                  columns=['generation', 'trap', 'fitness', 'time', 'density',
                                           'log-time', 'log-density', 'sigma', 'log-sigma', 'beta'])
        else:
            df_new = pd.DataFrame(np.c_[generation, trapspecie, fitness, reltime[:, trsp], trapdens[:, trsp],
                                        np.log10(reltime[:, trsp]), np.log10(trapdens[:, trsp]), beta],
                                  columns=['generation', 'trap', 'fitness', 'time', 'density',
                                           'log-time', 'log-density', 'beta'])
        df = pd.concat([df, df_new], ignore_index=True)
        trap_ii += 1

    if add_champion_to_pop:
        cx, cf = read_champion(run_path, filename='champion.out')
        cxs, _ = cx.shape
        trap_ii = 1
        for trsp in range(traps):
            if sigma_fitted:
                df_new = pd.DataFrame(np.c_[cxs*[gen], cxs*[trap_ii], cf, cx[:, 0:traps][:, trsp], cx[:, traps:2*traps][:, trsp],                                            np.log10(cx[:, 0:traps][:, trsp]), np.log10(cx[:, traps:2*traps][:, trsp]),
                                            cx[:, 2*traps:3*traps][:, trsp], np.log10(cx[:, 2*traps:3*traps][:, trsp]),
                                            cx[:, 3*traps:]],
                                      columns=['generation', 'trap', 'fitness', 'time', 'density',
                                               'log-time', 'log-density', 'sigma', 'log-sigma', 'beta'])
            else:
                df_new = pd.DataFrame(np.c_[[gen], [trap_ii], [cf], cx[0:traps][trsp], cx[traps:2*traps][trsp],
                                            np.log10(cx[0:traps][trsp]), np.log10(cx[traps:2*traps][trsp]),
                                            cx[2*traps:]],
                                      columns=['generation', 'trap', 'fitness', 'time', 'density',
                                               'log-time', 'log-density', 'beta'])
            df = pd.concat([df, df_new], ignore_index=True)
            trap_ii += 1

    return df


def fitness_scatter_plots(trap_df, gen, scale='lin'):
    """TBW.

    :return:
    """
    sns.set(style="white")
    fig = plt.figure()
    coloured_scatter_plot(trap_df, gen, trap='all', fig=fig, scale=scale)
    n = 0
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 2)
    for trap in [3, 4, 1, 2]:
        ax = fig.add_subplot(gs[n])
        coloured_scatter_plot(trap_df, gen, trap=trap, fig=fig, scale=scale)
        n += 1


def coloured_scatter_plot(trap_df, gen, trap, fig, scale='log'):
    """

    :param trap_df:
    :param gen:
    :param trap:
    :param cm:
    :param scale:
    :return:
    """
    z = None
    sign = 1
    if trap == 'all':
        x = trap_df['log-density'].loc[(trap_df['generation'] == gen)].values
        y = trap_df['log-time'].loc[(trap_df['generation'] == gen)].values
        if scale == 'lin':
            z = sign * trap_df['fitness'].loc[(trap_df['generation'] == gen)].values
        elif scale == 'log':
            z = sign * np.log10(trap_df['fitness'].loc[(trap_df['generation'] == gen)].values)
    else:
        x = trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        y = trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        if scale == 'lin':
            z = sign * trap_df['fitness'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        elif scale == 'log':
            z = sign * np.log10(trap_df['fitness'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values)

    # levels = 60
    # fig = plt.figure()
    sp = plt.scatter(x, y, c=z, s=1.)
    plt.xlabel(r'log$_{10}$(density)')
    plt.ylabel(r'log$_{10}$(release time)')
    cbar = fig.colorbar(sp)
    if sign == -1:
        ticks = [abs(float(t.get_text().replace('−', '-'))) for t in cbar.ax.get_yticklabels()]
        cbar.ax.set_yticklabels(ticks)
    if scale == 'log':
        cbar.set_label(r'log$_{10}$(fitness)')
    elif scale == 'lin':
        cbar.set_label('fitness')
    ax = plt.gca()
    set_jointplot_axes(ax)
    plt.title(r'Fitness of population at generation ' + str(gen) + ', trap #' + str(trap))


def fitness_contour_maps(trap_df, gen, scale='log'):
    """TBW.

    :return:
    """
    sns.set(style="white")
    contour_map(trap_df, gen, trap=1, cm="Reds", scale=scale)
    contour_map(trap_df, gen, trap=2, cm="Greens", scale=scale)
    contour_map(trap_df, gen, trap=3, cm="Blues", scale=scale)
    contour_map(trap_df, gen, trap=4, cm="Purples", scale=scale)
    contour_map(trap_df, gen, trap='all', cm="Greys", scale=scale)


def contour_map(trap_df, gen, trap, cm, scale='log'):
    """TBW.

    :return:
    """
    z = None
    sign = -1
    if trap == 'all':
        x = trap_df['log-density'].loc[(trap_df['generation'] == gen)].values
        y = trap_df['log-time'].loc[(trap_df['generation'] == gen)].values
        if scale == 'lin':
            z = sign * trap_df['fitness'].loc[(trap_df['generation'] == gen)].values
        elif scale == 'log':
            z = sign * np.log10(trap_df['fitness'].loc[(trap_df['generation'] == gen)].values)
    else:
        x = trap_df['log-density'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        y = trap_df['log-time'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        if scale == 'lin':
            z = sign * trap_df['fitness'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values
        elif scale == 'log':
            z = sign * np.log10(trap_df['fitness'].loc[(trap_df['generation'] == gen) & (trap_df['trap'] == trap)].values)

    levels = 60

    # ngridx = 100
    # ngridy = 100
    # fig = plt.figure()
    # ax1 = plt.axes()
    # xi = np.linspace(np.min(x), np.max(x), ngridx)
    # yi = np.linspace(np.min(y), np.max(y), ngridy)
    # triang = tri.Triangulation(x, y)
    # interpolator = tri.LinearTriInterpolator(triang, z)
    # Xi, Yi = np.meshgrid(xi, yi)
    # zi = interpolator(Xi, Yi)
    # # ax1.contour(xi, yi, zi, 14, linewidths=0.5, colors='k')
    # cntr1 = ax1.contourf(xi, yi, zi, levels, cmap=cm)
    # fig.colorbar(cntr1, ax=ax1)
    # # ax1.plot(x, y, 'ko', ms=1)
    # set_jointplot_axes(ax1)
    # plt.title(r'Fitness of population at generation ' + str(gen) + ', all traps')

    fig2 = plt.figure()
    ax2 = plt.axes()
    cntr2 = ax2.tricontourf(x, y, z, levels, cmap=cm)
    cbar = fig2.colorbar(cntr2, ax=ax2)
    if sign == -1:
        ticks = [abs(float(t.get_text().replace('−', '-'))) for t in cbar.ax.get_yticklabels()]
        cbar.ax.set_yticklabels(ticks)
    if scale == 'log':
        cbar.set_label(r'log$_{10}$(fitness)')
    elif scale == 'lin':
        cbar.set_label('fitness')
    set_jointplot_axes(ax2)
    plt.title(r'Fitness of population at generation ' + str(gen) + ', trap #' + str(trap))
    plt.xlabel(r'log$_{10}$(density)')
    plt.ylabel(r'log$_{10}$(release time)')
    # ax2.tricontour(x, y, z, 14, linewidths=0.5, colors='k')
    # ax2.plot(x, y, 'ko', ms=1)


def evolution_plots(run_path, job_list, sigma_fitted=False):
    """TBW.

    :return:
    """
    sns.set()
    sns.set_style("whitegrid")

    traps = 4

    generation = []
    fitness = []
    param_gen = []
    param_f = []
    param_cr = []
    param_dx = []
    param_df = []
    reltime = []
    trapdens = []
    sigma = []
    beta = []
    glob_min_f = 1e20

    i = 0
    isl = 0
    trap_df = pd.DataFrame()
    for job_name in job_list:

        evol_results_path = run_path + job_name + '/'

        runfileexist = True
        try:
            data, _ = read_data_from_all_files(evol_results_path, 'run.out')
            param_gen += [data[i][:, 0]]
            param_f += [data[i][:, 3]]   # F (float), amplification factor of the difference vector
            param_cr += [data[i][:, 4]]  # CR (float), crossover control parameter
            param_dx += [data[i][:, 5]]  # dx (float), the norm of the distance to the population mean of the mutant vectors
            param_df += [data[i][:, 6]]  # df (float), the population flatness evaluated as the distance between the fitness of the best and of the worst individual
        except FileNotFoundError:
            runfileexist = False
            # print('File run.out does not exist!')

        champion_file_path = run_path + job_name + '/champion.out'

        cx, cf = read_champion(champion_file_path)
        if sigma_fitted:
            order = pd.DataFrame(np.c_[cx[0:traps], cx[traps:2*traps], cx[2*traps:3*traps]],
                                 columns=['time', 'density', 'sigma'])
        else:
            order = pd.DataFrame(np.c_[cx[0:traps], cx[traps:2*traps]], columns=['time', 'density'])
        order = order.sort_values(by=['time'])

        data, filelist = read_data_from_all_files(evol_results_path, 'champion.out')
        nn = len(filelist)
        generation += [data[i][:, 0]]
        fitness += [data[i][:, 1]]
        reltime += [data[i][:, 2:2+traps]]
        trapdens += [data[i][:, 2+traps:2+traps*2]]
        if sigma_fitted:
            sigma += [data[i][:, 2+traps*2:2+traps*3]]
            beta += [data[i][:, 2+traps*3]]
        else:
            beta += [data[i][:, 2+traps*2]]

        rows = len(generation[-1])
        island = np.repeat(isl, rows).reshape((rows, 1))
        trap_ii = 1
        for trsp in order.index.values:
            trapspecie = np.repeat(np.array([trap_ii]), rows).reshape((rows, 1))
            if sigma_fitted:
                trap_df_new = pd.DataFrame(np.c_[island, trapspecie, generation[-1], fitness[-1], reltime[-1][:, trsp],
                                                 trapdens[-1][:, trsp], sigma[-1][:, trsp], beta[-1]],
                                           columns=['island', 'trap', 'generation', 'fitness', 'time', 'density',
                                                    'sigma', 'beta'])
            else:
                trap_df_new = pd.DataFrame(np.c_[island, trapspecie, generation[-1], fitness[-1], reltime[-1][:, trsp],
                                                 trapdens[-1][:, trsp], beta[-1]],
                                           columns=['island', 'trap', 'generation', 'fitness', 'time', 'density',
                                                    'beta'])
            trap_df = pd.concat([trap_df, trap_df_new], ignore_index=True)
            trap_ii += 1
        isl += 1
        trap_df['island'] = trap_df['island'].astype(int)
        trap_df['trap'] = trap_df['trap'].astype(int)
        trap_df['generation'] = trap_df['generation'].astype(int)

        # isl_min_f_ind = np.argmin(fitness[i][:])
        # isl_min_f = fitness[i][isl_min_f_ind]
        # if isl_min_f < glob_min_f:
        #     glob_min_f = isl_min_f
        #     glob_min_f_ind = isl_min_f_ind
        #     glob_min_f_isl = i

        # winner_ind = glob_min_f_isl   # index of the winner island
        # winner_fitness += [fitness[winner_ind]]
        # winner_params += [params[winner_ind]]

    # print('glob_min_f: ', glob_min_f)
    # print('glob_min_f_ind: ', glob_min_f_ind)
    # print('glob_min_f_isl: ', glob_min_f_isl)

    if runfileexist:
        plt.figure()
        plt.title('F amplification factor of the difference vector (adapted)')
        plt.xlabel('generation')
        plt.ylabel('F')
        for j in range(len(job_list)):
            plt.plot(param_gen[j], param_f[j], '.-', label='island '+str(j))
        plt.legend()
        plt.figure()
        plt.title('CR crossover control parameter (adapted)')
        plt.xlabel('generation')
        plt.ylabel('CR')
        for j in range(len(job_list)):
            plt.plot(param_gen[j], param_cr[j], '.-', label='island '+str(j))
        plt.legend()
        plt.figure()
        plt.title('Norm of the distance between pop. mean and mutant vectors')
        plt.xlabel('generation')
        plt.ylabel('dx')
        for j in range(len(job_list)):
            plt.semilogy(param_gen[j], param_dx[j], '.-', label='island '+str(j))
        plt.legend()
        plt.figure()
        plt.title('Pop. flatness (distance between fitness of best and worst indiv.)')
        plt.xlabel('generation')
        plt.ylabel('df')
        for j in range(len(job_list)):
            plt.semilogy(param_gen[j], param_df[j], '.-', label='island '+str(j))
        plt.legend()

    # plt.figure()
    # plt.title('Fitness function evolution')
    # plt.xlabel('generation')
    # plt.ylabel('f(x)')
    # for j in range(len(job_list)):
    #     plt.plot(generation[j], fitness[j], '.-', label='island '+str(j))
    #     # plt.semilogy(generation[j], fitness[j], '.-', label='island '+str(j))
    # plt.legend()
    #
    # plt.figure()
    # plt.title('Trap release time evolution')
    # plt.xlabel('generation')
    # plt.ylabel(r'$\tau_{release}^{parallel}$ (s)')
    # for j in range(len(job_list)):
    #     plt.semilogy(generation[j], reltime[j], '.-', label='island '+str(j))
    # plt.legend()
    #
    # plt.figure()
    # plt.title('Trap density evolution')
    # plt.xlabel('generation')
    # plt.ylabel(r'$n_{trap}^{parallel}$ (traps/pixel)')
    # for j in range(len(job_list)):
    #     plt.semilogy(generation[j], trapdens[j], '.-', label='island ' + str(j))
    # plt.legend()
    #
    # plt.figure()
    # plt.title('Beta parameter evolution')
    # plt.xlabel('generation')
    # plt.ylabel(r'$\beta$')
    # for j in range(len(job_list)):
    #     plt.plot(generation[j], beta[j], '.-', label='island ' + str(j))
    # plt.legend()

    plt.figure()
    plot = sns.lineplot(x="generation", y="time", hue="trap", style="island", palette="tab10",  # size="island",
                        legend="full", data=trap_df)
    plot.set(yscale="log")
    plt.ylabel(r'$\tau_{release}^{parallel}$ (s)')
    plt.legend(loc='upper right')
    plt.title("Evolution of trap release times")

    plt.figure()
    plot = sns.lineplot(x="generation", y="density", hue="trap", style="island", palette="tab10",
                        legend="full", data=trap_df)
    plot.set(yscale="log")
    plt.ylabel(r'$n_{trap}^{parallel}$ (traps/pixel)')
    plt.legend(loc='lower right')
    plt.ylim((1.e-3, 1.e+1))  # todo !!!!!!!!
    plt.title("Evolution of trap densities")

    plt.figure()
    plot = sns.lineplot(x="generation", y="sigma", hue="trap", style="island", palette="tab10",
                        legend="full", data=trap_df)
    plot.set(yscale="log")
    plt.ylabel(r'$\sigma_{capture}^{parallel}$ (cm$^2$)')
    plt.legend(loc='lower right')
    plt.title("Evolution of trap capture cross-sections")

    plt.figure()
    plot = sns.lineplot(x="generation", y="beta", style="island", palette="tab10",
                        legend="full", data=trap_df)
    plt.ylabel(r'$\beta$')
    plt.legend(loc='upper right')
    plt.title("Evolution of beta parameter")

    plt.figure()
    plot = sns.lineplot(x="generation", y="fitness", style="island", palette="tab10",
                        legend="full", data=trap_df)
    # plot.set(yscale="log")
    plt.ylabel('f(x)')
    plt.legend(loc='upper right')
    plt.title("Evolution of fitness values")


def print_results(run_path, job_list, sigma_fitted=False):
    """

    :param run_path:
    :param job_list:
    :param sigma_fitted:
    :return:
    """
    traps = 4
    for job_name in job_list:

        champion_file_path = run_path + job_name + '/champion.out'
        cx, cf = read_champion(champion_file_path)

        if sigma_fitted:
            order = pd.DataFrame(np.c_[cx[0:traps], cx[traps:2 * traps], cx[2 * traps:3 * traps]],
                                 columns=['time', 'density', 'sigma'])
        else:
            order = pd.DataFrame(np.c_[cx[0:traps], cx[traps:2 * traps]], columns=['time', 'density'])
        order = order.sort_values(by=['time'])
        print('Traps, ' + job_name + ', cf = %1.3e' % cf)
        try:
            print('            #1         #2         #3         #4')
            print('tr:  {:1.3e}  {:1.3e}  {:1.3e}  {:1.3e}'.format(*order.time.values))
            print('nt:  {:1.3e}  {:1.3e}  {:1.3e}  {:1.3e}'.format(*order.density.values))
            if sigma_fitted:
                print('si:  {:1.3e}  {:1.3e}  {:1.3e}  {:1.3e}'.format(*order.sigma.values))
        except IndexError:
            print('Two trap species have the same release time!')


def results_in_function_of_weighting(run_path, weight_list):
    """

    :param run_path:
    :param weight_list:
    :return:
    """
    traps = 4
    trap_result_df = pd.DataFrame()
    for weight_value in weight_list:
        champion_file_path = run_path + 'job_w' + str(weight_value) + '/champion.out'
        cx, cf = read_champion(champion_file_path)
        order = pd.DataFrame(np.c_[traps*[weight_value], list(range(1, 1+traps)),
                                   cx[0:traps], cx[traps:2 * traps]],
                             columns=['weight', 'trap', 'time', 'density'])
        order = order.sort_values(by=['time'])
        print('Traps, weight = ' + str(weight_value) + ', cf = %1.3e' % cf)
        trap_result_df = pd.concat([trap_result_df, order], ignore_index=True)
    trap_result_df['trap'] = trap_result_df['trap'].astype(int)

    plt.figure()
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 1]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 2]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 3]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 4]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    plt.legend()
    plt.xlabel('weighting func. maximum')
    plt.ylabel('release time')

    plt.figure()
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 1]),
                 pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 2]),
                 pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 3]),
                 pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    plt.semilogy(pd.to_numeric(trap_result_df['weight'].loc[trap_result_df['trap'] == 4]),
                 pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    plt.legend()
    plt.xlabel('weighting func. maximum')
    plt.ylabel('density')


def results_2d_in_function_of_weight_params(run_path, weight_amp_list, weight_tau_list):
    """

    :param run_path:
    :param weight_amp_list:
    :param weight_tau_list:
    :return:
    """
    traps = 4
    trap_result_df = pd.DataFrame()

    data_path = '../data/better-plato-target-data/'
    data_files = ['cold/CCD280-14482-06-02-cryo-irrad-gd15.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd16.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd18.5V.txt',
                  'cold/CCD280-14482-06-02-cryo-irrad-gd19.5V.txt']
    injection_profile, target_output, target_error = read_plato_data(data_path=data_path, data_files=data_files,
                                                                     start=None, end=None)
    fit_range_length = 350
    target_start_fit, target_end_fit = 51, 51 + fit_range_length
    sim_start_fit, sim_end_fit = 1103, 1103 + fit_range_length
    number_of_transfers = 1552
    parameters = ['tr_p', 'nt_p', 'beta_p']
    t = 947.22e-6  # s
    fwc = 1.e6  # e-
    vg = 1.62e-10  # cm**3 (half volume!)
    vth = 1.866029409893778e7  # cm/s, from Thibaut's jupyter notebook
    sigma = 5.e-16  # cm**2 (for all traps)
    cdm = CDMFitting(injection_profile, target_output, trap_species=traps, variables=parameters)
    cdm.charge_injection(True)
    cdm.set_parallel_parameters(t=t, vg=vg, fwc=fwc, vth=vth, sigma=sigma)
    cdm.set_dimensions(para_transfers=number_of_transfers)
    cdm.set_target_fit_range((target_start_fit, target_end_fit))
    cdm.set_simulated_fit_range((sim_start_fit, sim_end_fit))
    cdm.set_normalization()

    x = np.linspace(start=1, stop=fit_range_length, num=fit_range_length)
    x = x.reshape(len(x), 1)

    for weight_tau in weight_tau_list:
        for weight_amp in weight_amp_list:

            curr_file_path = run_path + 'job_wt' + str(weight_tau) + '_wa' + str(weight_amp)
            champion_file_path = curr_file_path + '/champion.out'
            cx, cf = read_champion(champion_file_path)

            weight_tau = weight_tau * 1.0e-2
            # weighting_func = 1 - (np.exp(-1 * t * x / weight_tau))
            # cdm.set_weighting_function(weighting_func)

            fitness_norm = cdm.fitness_evaluation(cx)

            order = pd.DataFrame(np.c_[traps*[weight_tau], traps*[weight_amp], list(range(1, 1+traps)),
                                       cx[0:traps], cx[traps:2 * traps], traps*[cf], traps*fitness_norm],
                                 columns=['weight_tau', 'weight_amp', 'trap', 'time', 'density', 'fitness',
                                          'fitness_norm'])
            order = order.sort_values(by=['time'])

            print('Traps, weight_amp = ' + str(weight_amp) + ', weight_tau = ' + str(weight_tau) +
                  ', cf = %1.3e' % cf + ', fn = %1.3e' % fitness_norm[0])
            trap_result_df = pd.concat([trap_result_df, order], ignore_index=True)
    trap_result_df['trap'] = trap_result_df['trap'].astype(int)

    # print('Least-squares fitness values:')
    # print('  dataset[0] fitness = %.3f' % fitnessleast0)
    # print('  dataset[1] fitness = %.3f' % fitnessleast1)
    # print('  dataset[2] fitness = %.3f' % fitnessleast2)
    # print('  dataset[3] fitness = %.3f' % fitnessleast3)
    # print('  Sum of fitnesses   = %.6e' % (fitnessleast0 + fitnessleast1 + fitnessleast2 + fitnessleast3))

    # plt.figure()
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 1]),
    #              pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 2]),
    #              pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 3]),
    #              pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 4]),
    #              pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    # plt.legend()
    # plt.xlabel('weighting func. amplitude')
    # plt.ylabel('release time')
    #
    # plt.figure()
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 1]),
    #              pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 2]),
    #              pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 3]),
    #              pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    # plt.semilogy(pd.to_numeric(trap_result_df['weight_amp'].loc[trap_result_df['trap'] == 4]),
    #              pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    # plt.legend()
    # plt.xlabel('weighting func. amplitude')
    # plt.ylabel('density')

    plt.figure()
    plt.loglog(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 1]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    plt.loglog(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 2]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    plt.loglog(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 3]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    plt.loglog(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 4]),
                 pd.to_numeric(trap_result_df['time'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    plt.legend()
    plt.xlabel('weighting func. time const.')
    plt.ylabel('release time')

    plt.figure()
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 1]),
             pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 1]), '.-', label='trap #1')
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 2]),
             pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 2]), '.-', label='trap #2')
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 3]),
             pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 3]), '.-', label='trap #3')
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau'].loc[trap_result_df['trap'] == 4]),
             pd.to_numeric(trap_result_df['density'].loc[trap_result_df['trap'] == 4]), '.-', label='trap #4')
    plt.legend()
    plt.xlabel('weighting func. time const.')
    plt.ylabel('density')

    plt.figure()
    plt.plot(pd.to_numeric(trap_result_df['weight_tau']),
             pd.to_numeric(trap_result_df['fitness']), '.-', label='fitness calc. with wf')
    plt.plot(pd.to_numeric(trap_result_df['weight_tau']),
             pd.to_numeric(trap_result_df['fitness_norm']), '.-', label='fitness calc. w/o wf')
    curr_file_path = run_path + 'job_no_weighting'
    champion_file_path = curr_file_path + '/champion.out'
    cx, cf = read_champion(champion_file_path)
    fitness_no_wf = cdm.fitness_evaluation(cx)
    print('Traps, no weighting, cf = %1.3e' % cf + ', fn = %1.3e' % fitness_no_wf[0])
    plt.plot([0, 6.e-2], 2*[fitness_no_wf], '--', label='no weighting')
    plt.legend()
    plt.xlabel('weighting func. time const.')
    plt.ylabel('fitness')

    plt.figure()
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau']),
                 pd.to_numeric(trap_result_df['fitness']), '.-', label='fitness calc. with wf')
    plt.semilogx(pd.to_numeric(trap_result_df['weight_tau']),
                 pd.to_numeric(trap_result_df['fitness_norm']), '.-', label='fitness calc. w/o wf')
    plt.semilogx([1.e-4, 6.e-2], 2*[fitness_no_wf], '--', label='no weighting')
    plt.legend(loc='lower left')
    plt.xlabel('weighting func. time const.')
    plt.ylabel('fitness')


def histograms(trap_df, gen):
    """TBW.

    :return:
    """
    sns.set(style="ticks")
    bins = 100
    trp_lst = []
    trp_lst += [trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 1)]]
    trp_lst += [trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 2)]]
    trp_lst += [trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 3)]]
    trp_lst += [trap_df.loc[(trap_df['generation'] == gen) & (trap_df['trap'] == 4)]]
    n = 0
    fig = plt.figure()
    gs = gridspec.GridSpec(3, 4)
    for param in ['log-time', 'log-density', 'log-sigma']:
        for trap in range(0, 4):
            df = trp_lst[trap]
            ax = fig.add_subplot(gs[n])
            sns.distplot(df[param], bins=bins, hist=True, kde=False, rug=False)
            if param is 'log-time':
                plt.title('trap #'+str(trap+1))
                plt.xlim((-3.3, 0.5))
            elif param is 'log-density':
                plt.xlim((-4, 2))
            elif param is 'log-sigma':
                plt.xlim((-22, -16))
            # plt.ylim((0, 2.5))
            n += 1


def former_test_campaign_data_plots():
    """

    :return:
    """

    former_plato_data_path = '../data/former_test_campaign_flatfield/'  # FLATFIELD (NO CHARGE INJECTION), WARM DATA

    former_files = ['ccd270b-par-EPER-Ei1-one-image-single-4.txt',
                    'ccd270b-par-EPER-Ei1-one-image-single-8.txt',
                    'ccd270b-par-EPER-Ei1-one-image-single-12.txt',
                    'ccd270b-par-EPER-Ei1-one-image-single-16.txt']
    data = []
    for i in range(len(former_files)):
        data += [np.loadtxt(former_plato_data_path + former_files[i], dtype=float, skiprows=2)]

    flatfield_avg_signal = [354.437103271,  # 4
                            2078.9050293,   # 8
                            7404.50146484,  # 12
                            12562.7226562]  # 16

    plt.figure()
    for i in range(len(former_files)):
        plt.plot(data[i], '.')


if __name__ == '__main__':
    # old_plotting()
    # old_analysis()

    # plato_data_path = '../data/plato-target-data/'
    plato_data_path = '../data/better-plato-target-data/'

    # analysis_job_list = ['job_s1234', 'job_s9759', 'job_s8456', 'job_s7895',
    #                      'job_s6786', 'job_s6666', 'job_s2357', 'job_s3467']

    # COLD
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/cold/'
    # analysis_job_list = ['job_s1234', 'job_s6786', 'job_s5397', 'job_s9759', 'job_s6666']

    # WARM
    # irrad_type = 'warm'
    # analysis_run_path = '../data/results/new_plato/warm/'
    # analysis_job_list = ['job_s6786', 'job_s9759', 'job_s6666', 'job_s8456', 'job_s7895']

    # COLD FITTED WITH WARM RESULTS
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/cold/fitting_with_s7895_warm_results/'
    # analysis_job_list = ['job_s6786', 'job_s9759', 'job_s6666', 'job_s8456', 'job_s7895']

    # WARM FITTED WITH COLD RESULTS
    # irrad_type = 'warm'
    # analysis_run_path = '../data/results/new_plato/warm/fitting_with_s1234_cold_results/'
    # analysis_job_list = ['job_s1234', 'job_s6786', 'job_s5397', 'job_s9759', 'job_s6666']

    # COLD FITTING 9 DATASETS
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/9_dataset_fits/cold/'
    # analysis_job_list = ['job_s1234', 'job_s9759', 'job_s8456', 'job_s2357', 'job_s3467']

    # WARM FITTING 9 DATASETS
    # irrad_type = 'warm'
    # analysis_run_path = '../data/results/new_plato/9_dataset_fits/warm/'
    # analysis_job_list = ['job_s6786', 'job_s6666', 'job_s2357', 'job_s3467', 'job_s7895']

    # COLD, 4 DATASETS, pop 10k, gen 3k, fit range 150, no weighting func, chi2 map, BEST RESULTS so far
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/cold/chi_sq_map_run_ordered/'
    # analysis_job_list = ['job_s6786', 'job_s6666', 'job_s1234', 'job_s5397', 'job_s9759']   # BEST FITNESS: job_s9759

    # WARM, 4 DATASETS, pop 10k, gen 3k, fit range 150, no weighting func, chi2 map, BEST RESULTS so far
    # irrad_type = 'warm'
    # analysis_run_path = '../data/results/new_plato/warm/chi_sq_map_run_ordered/'
    # analysis_job_list = ['job_s6786', 'job_s6666', 'job_s8456', 'job_s7895', 'job_s9759']   # BEST FITNESS: job_s8456

    # weighting_func_plots(plato_data_path, '../data/results/new_plato/cold/chi_sq_map_run_ordered/',
    #                      ['job_s9759'], irrad='cold')
    # weighting_func_plots(plato_data_path, '.', [''], irrad='cold')

    # Weighting func: COLD, 4 DATASETS, pop 1k, gen 1k, fit range 400, different weighting func max (np.logspace)
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/cold/weighting_func/'
    # wf_list = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 30, 40, 50, 60, 100]
    # results_in_function_of_weighting(analysis_run_path, wf_list)

    # # Weighting func: COLD, 4 DATASETS, pop 1k, gen 1k, fit range 350, different weighting func: (1-exp(-t*x/tau))
    # irrad_type = 'cold'
    # analysis_run_path = '../data/results/new_plato/cold/weighting_func/exp/'
    # analysis_job_list = ['job_wt0.01_wa1', 'job_wt0.05_wa1',
    #                      # 'job_wt0.2_wa1', 'job_wt0.3_wa1',
    #                      # 'job_wt0.4_wa1', 'job_wt0.5_wa1', 'job_wt0.6_wa1', 'job_wt0.7_wa1',
    #                      # 'job_wt0.8_wa1', 'job_wt0.9_wa1', 'job_wt1_wa1',
    #                      'job_no_weighting']
    # wfa_list = [1]
    # wft_list = [0.01, 0.02, 0.03, 0.04, 0.045, 0.05, 0.055, 0.06, 0.07, 0.08, 0.09,
    #             0.1, 0.15, 0.2, 0.25, 0.3, 0.35,
    #             0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3, 3.5, 3.7, 3.9, 4, 4.1, 4.3, 4.5, 5, 6]
    # results_2d_in_function_of_weight_params(analysis_run_path, wfa_list, wft_list)
    # fit_plots(plato_data_path, analysis_run_path, analysis_job_list, irrad_type)
    # print_results(analysis_run_path, analysis_job_list)

    results_run_paths = [
        '../data/results/new_plato/warm/fitting_with_s1234_cold_results/job_s*/',
        '../data/results/new_plato/cold/job_s*/',
        '../data/results/new_plato/9_dataset_fits/cold/job_s*/',
        '../data/results/new_plato/cold/fitting_with_s7895_warm_results/job_s*/',
        '../data/results/new_plato/warm/job_s*/',
        '../data/results/new_plato/9_dataset_fits/warm/job_s*/',
        '../data/results/new_plato/cold/chi_sq_map_run_ordered/job_s*/',
        '../data/results/new_plato/warm/chi_sq_map_run_ordered/job_s*/'
                        ]
    # results_map(run_paths=results_run_paths)

    # trap_df = population_dataframe(run_path='../data/results/new_plato/warm/chi_sq_map_run_ordered/job_s8456/',
    # trap_df = population_dataframe(run_path='../data/results/new_plato/cold/chi_sq_map_run_ordered/job_s9759/',
    #                                gen=3000, traps=4, add_champion_to_pop=True)
    # trap_df.to_pickle("./trap_df_cold_pop10000_gen3000_seed9759_championadded.pkl")
    # trap_df.to_pickle("./trap_df_warm_pop10000_gen3000_seed8456_championadded.pkl")

    # fitness_contour_maps(trap_df, gen=3000)
    # chi_square_map(trap_df, gen=3000)

    # fitness_limit = 16.
    # lim_trap_df = trap_df.loc[(trap_df['fitness'] <= fitness_limit)]
    # fitness_contour_maps(lim_trap_df, gen=3000, scale='lin')
    # chi_square_map(lim_trap_df, gen=3000)

    # calc_target_fitness_from_error(plato_data_path)

    # analysis_run_path = '.'
    # analysis_job_list = ['']
    # irrad_type = 'cold'
    # fit_plots(plato_data_path, analysis_run_path, analysis_job_list, irrad_type)

    # cdm_crosssection_sensitivity_analysis(plato_data_path)

    # cdm_fwc_sensitivity_analysis(plato_data_path)
    # sensitivity_analysis(plato_data_path)
    # data_plots(plato_data_path)

    # former_test_campaign_data_plots()
    #
    # analysis_run_path = '.'
    # analysis_job_list = ['']
    # irrad_type = 'cold'

    # print_results(analysis_run_path, analysis_job_list, sigma_fitted=True)
    # evolution_plots(analysis_run_path, analysis_job_list, sigma_fitted=True)
    # fit_plots(plato_data_path, analysis_run_path, analysis_job_list, irrad_type)

    # trap_df = population_dataframe(run_path='./', gen=300, traps=4, add_champion_to_pop=True, sigma_fitted=True)

    ggg = 3000
    analysis_run_path = '../data/results/new_plato/cold/fitting_sigma/pop5k_gen3k/'
    analysis_job_list = ['job_s1234', 'job_s5397', 'job_s6666', 'job_s6786', 'job_s9759']
    # irrad_type = 'cold'
    print_results(analysis_run_path, analysis_job_list, sigma_fitted=True)

    trap_df = population_dataframe(run_path='../data/results/new_plato/cold/fitting_sigma/pop5k_gen3k/job_s*/',
                                   gen=ggg, traps=4, add_champion_to_pop=True, sigma_fitted=True)
    fitness_limit = np.power(10, 1.8)  # 63.09573444
    trap_df = trap_df.loc[(trap_df['fitness'] <= fitness_limit)]
    trap_df = trap_df.sort_values(by=['fitness'], ascending=False)
    # chi_square_map(trap_df, gen=ggg)
    histograms(trap_df, gen=ggg)
    fitness_scatter_plots(trap_df, gen=ggg)

    plt.show()
