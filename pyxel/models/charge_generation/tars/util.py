"""Pyxel TARS model to generate charge by ionization."""
import math
from bisect import bisect
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import interpolate


def sampling_distribution(distribution):
    """TBW.

    :param distribution:
    """
    u = np.random.random()
    # random_value_from_dist = distribution[bisect(distribution[:, 1], u) - 1, 0]
    random_value_from_dist = get_xvalue_with_interpolation(distribution, u)

    return random_value_from_dist


def get_xvalue_with_interpolation(function_array, y_value):
    """TBW.

    :param function_array:
    :param y_value:
    """
    if y_value <= function_array[0, 1]:
        intpol_x_value = function_array[0, 0]
    elif y_value >= function_array[-1, 1]:
        intpol_x_value = function_array[-1, 0]
    else:
        y_index_bot = bisect(function_array[:, 1], y_value) - 1
        y_index_top = y_index_bot + 1
        y_value_bot = function_array[y_index_bot, 1]
        y_value_top = function_array[y_index_top, 1]
        x_value_bot = function_array[y_index_bot, 0]
        x_value_top = function_array[y_index_top, 0]

        intpol_x_value = x_value_bot + (y_value - y_value_bot) * \
                                       (x_value_top - x_value_bot) / (y_value_top - y_value_bot)

    return intpol_x_value


def get_yvalue_with_interpolation(function_array, x_value):
    """TBW.

    :param function_array:
    :param x_value:
    """
    x_index_bot = bisect(function_array[:, 0], x_value) - 1
    x_index_top = x_index_bot + 1
    x_value_bot = function_array[x_index_bot, 0]
    x_value_top = function_array[x_index_top, 0]
    y_value_bot = function_array[x_index_bot, 1]
    y_value_top = function_array[x_index_top, 1]

    intpol_y_value = y_value_bot + (x_value - x_value_bot) * (y_value_top - y_value_bot) / (x_value_top - x_value_bot)

    return intpol_y_value


def load_histogram_data(file_name, hist_type, skip_rows, read_rows):
    """TBW.

    :param file_name:
    :param hist_type:
    :param skip_rows:
    :param read_rows:
    """
    # TODO store count in pandas dataframe as int !!!
    return pd.read_csv(file_name, delimiter="\t", names=[hist_type, "counts"],
                       usecols=[1, 2], skiprows=skip_rows, nrows=read_rows)


def read_data(file_name):
    """TBW.

    :param file_name:
    :return:
    """
    return np.loadtxt(file_name, 'float', '#')


def interpolate_data(data):
    """TBW.

    :param data:
    :return:
    """
    return interpolate.interp1d(data[:, 0], data[:, 1], kind='linear')


def read_particle_spectrum(file_name, detector_area):
    """Set up the particle specs according to a spectrum.

    :param file_name: path of the file containing the spectrum
    :param detector_area: area of detector
    """
    spectrum = read_data(file_name)                             # nuc/m2*s*sr*MeV
    spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * detector_area      # nuc/s*MeV     # TODO TODO !

    spectrum_function = interpolate_data(spectrum)

    lin_energy_range = np.arange(np.min(spectrum[:, 0]), np.max(spectrum[:, 0]), 0.01)

    cum_sum = np.cumsum(spectrum_function(lin_energy_range))
    cum_sum /= np.max(cum_sum)
    spectrum_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

    return spectrum_cdf


def read_data_library():
    """TBW."""
    path = Path(__file__).parent.joinpath('data', 'inputs')
    return pd.read_csv(Path(path, 'data_library.csv'))


def create_data_library():
    """TBW."""
    data_library = pd.DataFrame(columns=['type', 'energy', 'thickness', 'file'])

    # mat_list = ['Si']

    type_list = ['proton']                          # 'ion', 'alpha', 'beta', 'electron', 'gamma', 'x-ray']
    energy_list = [100.]                            # MeV
    thick_list = [40., 50., 60., 70., 100.]         # um

    filename_list = [
        'stepsize_proton_100MeV_40um_Si_10k.ascii',
        'stepsize_proton_100MeV_50um_Si_10k.ascii',
        'stepsize_proton_100MeV_60um_Si_10k.ascii',
        'stepsize_proton_100MeV_70um_Si_10k.ascii',
        'stepsize_proton_100MeV_100um_Si_10k.ascii'
    ]

    i = 0
    for pt in type_list:
        for en in energy_list:
            for th in thick_list:
                data_dict = {
                    'type': pt,
                    'energy': en,
                    'thickness': th,
                    'file': str(filename_list[i]),
                    }
                new_df = pd.DataFrame(data_dict, index=[0])
                data_library = pd.concat([data_library, new_df], ignore_index=True)
                i += 1

    path = Path(__file__).parent.joinpath('data', 'inputs')
    data_library.to_csv(Path(path, 'data_library.csv'), index=False)


def find_smaller_neighbor(data_library, column, value):
    """TBW.

    :return:
    """
    sorted_list = sorted(data_library[column].unique())
    index = bisect(sorted_list, value) - 1
    if index < 0:
        index = 0
    return sorted_list[index]


def find_larger_neighbor(data_library, column, value):
    """TBW.

    :return:
    """
    sorted_list = sorted(data_library[column].unique())
    index = bisect(sorted_list, value)
    if index > len(sorted_list) - 1:
        index = len(sorted_list) - 1
    return sorted_list[index]


def find_closest_neighbor(data_library, column, value):
    """TBW.

    :return:
    """
    sorted_list = sorted(data_library[column].unique())
    index_smaller = bisect(sorted_list, value) - 1
    index_larger = bisect(sorted_list, value)

    if index_larger >= len(sorted_list):
        return sorted_list[-1]
    elif (sorted_list[index_larger]-value) < (value-sorted_list[index_smaller]):
        return sorted_list[index_larger]
    else:
        return sorted_list[index_smaller]


def select_stepsize_data(df, p_type, p_energy, p_track_length):
    """TBW.

    :param p_type: str
    :param p_energy: float (MeV)
    :param p_track_length: float (um)
    :return:
    """
    distance = find_larger_neighbor(data_library=df, column='thickness', value=p_track_length)
    energy = find_closest_neighbor(data_library=df, column='energy', value=p_energy)

    path = Path(__file__).parent.joinpath('data', 'inputs')
    file = df[(df.type == p_type) & (df.energy == energy) & (df.thickness == distance)].file.values[0]
    return Path(path, file)
