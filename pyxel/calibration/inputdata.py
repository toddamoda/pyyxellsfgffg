"""
PLATO CCD data reading script for CDM model calibration script
"""
import numpy as np


def create_injection_profile_average(array):
    """TBW.

    :param array:
    :return:
    """
    # # TODO
    # rows, _ = array.shape
    # out = np.zeros(rows)
    # out[np.where(array > threshold)[0]] = np.average(array[40:50])
    # return out.reshape(rows, 1)

    out = np.zeros(2051)
    signal = np.average(array[40:50])
    out[52:102] = signal
    out[552:602] = signal
    out[1052:1102] = signal
    return out.reshape(len(out), 1)


def create_injection_profile_highest(array):
    """TBW.

    :param array:
    :return:
    """
    out = np.zeros(2051)
    signal = np.max(array[0:50])
    out[52:102] = signal
    out[552:602] = signal
    out[1052:1102] = signal
    return out.reshape(len(out), 1)


def create_test_inj_profile(array):
    """TBW.

    :param array:
    :return:
    """
    # # TODO
    # rows, _ = array.shape
    # out = np.zeros(rows)
    # out[np.where(array > threshold)[0]] = np.average(array[40:50])
    # return out.reshape(rows, 1)

    signal = np.average(array[92:102])
    out = np.zeros(2051)
    out[52:102] = signal
    out[552:602] = signal
    out[1052:1102] = signal
    return out.reshape(len(out), 1)


def read_fit_data(path):
    """TBW.

    :param path: path of fit.out datafile
    :return:
    """
    fitdata = np.loadtxt(path, dtype=float, delimiter=' ')
    rows, _ = fitdata.shape
    out = []
    out += [fitdata[:, 0].reshape((rows, 1))]
    out += [fitdata[:, 1].reshape((rows, 1))]
    out += [fitdata[:, 2].reshape((rows, 1))]
    out += [fitdata[:, 3].reshape((rows, 1))]
    return out


# def read_champion(path, filename=None):
#     """TBW.
#
#     :param path: path of fit.out datafile
#     :return:
#     """
#     if filename is not None:
#         data = np.array([])
#         filelist = glob.glob(path + filename)
#         if filelist:
#             for file in filelist:
#                 if len(data) == 0:
#                     # data = np.loadtxt(file)[start:, :]
#                     data = np.loadtxt(path, dtype=float, delimiter=' ')
#                 else:
#                     # data = np.vstack((data, np.loadtxt(file)[start:, :]))
#                     data = np.vstack((data, np.loadtxt(path, dtype=float, delimiter=' ')))
#         else:
#             raise FileNotFoundError()
#         return data, filelist
#     else:
#         fitdata = np.loadtxt(path, dtype=float, delimiter=' ')
#         rows, _ = fitdata.shape
#         cf = fitdata[-1, 1]
#         cx = fitdata[-1, 2:]
#         return cx, cf


def read_test_data(data_path='../data/noisy_cdm_valid/'):
    """TBW.

    :param data_path: path to datafiles
    :return:
    """
    # # With noise:
    # data_cold_15v = np.loadtxt(data_path + 'plato_cdm_4trap_noise_sig10_15.5V.txt', dtype=float)
    # data_cold_16v = np.loadtxt(data_path + 'plato_cdm_4trap_noise_sig10_16.5V.txt', dtype=float)
    # data_cold_18v = np.loadtxt(data_path + 'plato_cdm_4trap_noise_sig10_18.5V.txt', dtype=float)
    # data_cold_19v = np.loadtxt(data_path + 'plato_cdm_4trap_noise_sig10_19.5V.txt', dtype=float)
    # Without noise:
    data_cold_15v = np.loadtxt(data_path + 'plato_cdm_4trap_15.5V.txt', dtype=float)
    data_cold_16v = np.loadtxt(data_path + 'plato_cdm_4trap_16.5V.txt', dtype=float)
    data_cold_18v = np.loadtxt(data_path + 'plato_cdm_4trap_18.5V.txt', dtype=float)
    data_cold_19v = np.loadtxt(data_path + 'plato_cdm_4trap_19.5V.txt', dtype=float)
    # data_cold_15v = np.loadtxt(data_path + 'plato_cdm_1trap_15.5V.txt', dtype=float)
    # data_cold_16v = np.loadtxt(data_path + 'plato_cdm_1trap_16.5V.txt', dtype=float)
    # data_cold_18v = np.loadtxt(data_path + 'plato_cdm_1trap_18.5V.txt', dtype=float)
    # data_cold_19v = np.loadtxt(data_path + 'plato_cdm_1trap_19.5V.txt', dtype=float)
    data = [data_cold_15v, data_cold_16v, data_cold_18v, data_cold_19v]
    return _format_singlecol_data_(data)


def read_former_campaign_data(data_path, data_files, flatfield_avg_signal, det_pix_rows):
    """TBW.

    :param data_path: path to datafiles
    :param data_files: datafile names
    :return:
    """
    data = []
    for i in range(len(data_files)):
        data += [np.loadtxt(data_path + data_files[i], dtype=float, skiprows=2)]

    target = []
    flatfield = []

    for i in range(len(data)):
        rows = len(data[i])
        target += [data[i].reshape(rows, 1)]
        flatfield += [flatfield_avg_signal[i] * np.ones((det_pix_rows, 1))]

    return flatfield, target


def read_plato_data(data_path, data_files, start, end):
    """TBW.

    :param data_path: path to datafiles
    :param data_files: datafile names
    :param start: index of first data point to be read
    :param end: index of last data point to be read
    :return:
    """
    data = []
    for i in range(len(data_files)):
        data += [np.loadtxt(data_path + data_files[i], dtype=float, delimiter='|')]
    return _format_data_(data, start, end)


def _format_data_(data_list, start=None, end=None):
    """
    
    :param data_list: list of loaded data
    :param start: index of first data point to be read
    :param end: index of last data point to be read
    :param thr: threshold for generating injection profile
    :return: 
    """
    injected = []
    target = []
    err = []

    for i in range(len(data_list)):
        rows, _ = data_list[i].shape
        target += [data_list[i][:, 0][start:end].reshape(rows, 1)]
        err += [data_list[i][:, 1][start:end].reshape(rows, 1)]
        injected += [create_injection_profile_highest(target[i])]

    return injected, target, err


def _format_singlecol_data_(data_list, start=None, end=None):
    """

    :param data_list: list of loaded data
    :param start: index of first data point to be read
    :param end: index of last data point to be read
    :param thr: threshold for generating injection profile
    :return:
    """
    rows1 = len(data_list[0])
    rows2 = len(data_list[1])
    rows3 = len(data_list[2])
    rows4 = len(data_list[3])
    target_1 = data_list[0].reshape(rows1, 1)
    target_2 = data_list[1].reshape(rows2, 1)
    target_3 = data_list[2].reshape(rows3, 1)
    target_4 = data_list[3].reshape(rows4, 1)

    injected_1 = create_test_inj_profile(target_1)
    injected_2 = create_test_inj_profile(target_2)
    injected_3 = create_test_inj_profile(target_3)
    injected_4 = create_test_inj_profile(target_4)

    target_output = [target_1[start:end, :],
                     target_2[start:end, :],
                     target_3[start:end, :],
                     target_4[start:end, :]]  # list of numpy arrays !

    injection_profile = [injected_1[start:end, :],
                         injected_2[start:end, :],
                         injected_3[start:end, :],
                         injected_4[start:end, :]]  # list of numpy arrays !

    return injection_profile, target_output
