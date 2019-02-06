"""TBW."""
import os
import typing as t
import numpy as np
from astropy.io import fits


def read_data(data_path: t.Union[str, list]):
    """TBW.

    :param data_path:
    :return:
    """
    if isinstance(data_path, str):
        data_path = [data_path]
    elif isinstance(data_path, list) and all(isinstance(item, str) for item in data_path):
        pass
    else:
        raise TypeError

    output = []                                     # type: list
    for i, path in enumerate(data_path):
        if not os.path.exists(path):
            raise FileNotFoundError('Input file %s can not be found.' % str(path))

        data = None
        if '.fits' in path:
            data = fits.getdata(path)
        elif '.npy' in path:
            data = np.load(path)
        else:
            sep = [' ', ',', '|', ';']
            ii, jj = 0, 1
            while jj:
                try:
                    jj -= 1
                    data = np.loadtxt(path, delimiter=sep[ii])
                except ValueError:
                    ii += 1
                    jj += 1
                    if ii >= len(sep):
                        break

        if data is None:
            raise IOError('Input file %s can not be read by Pyxel.' % str(path))
        else:
            output += [data]

    return output


def list_to_slice(input_list: t.Optional[t.List[int]]):
    """TBW.

    :return:
    """
    if input_list:
        if len(input_list) == 2:
            return slice(input_list[0], input_list[1])
        elif len(input_list) == 4:
            return slice(input_list[0], input_list[1]), slice(input_list[2], input_list[3])
        else:
            raise ValueError('Fitting range should have 2 or 4 values')
    else:
        return slice(None)


def check_ranges(target_fit_range: t.Optional[t.List[int]],
                 out_fit_range: t.Optional[t.List[int]],
                 rows: int, cols: int):
    """TBW."""
    if target_fit_range:
        if len(target_fit_range) != 4 and len(target_fit_range) != 2:
            raise ValueError
        if out_fit_range:
            if len(out_fit_range) != 4 and len(out_fit_range) != 2:
                raise ValueError
            if (target_fit_range[1] - target_fit_range[0]) != (out_fit_range[1] - out_fit_range[0]):
                raise ValueError('Fitting ranges have different lengths in 1st dimension')
            if len(target_fit_range) == 4 and len(out_fit_range) == 4:
                if (target_fit_range[3] - target_fit_range[2]) != (out_fit_range[3] - out_fit_range[2]):
                    raise ValueError('Fitting ranges have different lengths in 2nd dimension')
        for i in [0, 1]:
            if target_fit_range[i] < 0 or target_fit_range[i] > rows:
                raise ValueError('Value of target fit range is wrong')
        if len(target_fit_range) == 4:
            if cols is None:
                raise ValueError('Target data is not a 2 dimensional array')
            for i in [2, 3]:
                if target_fit_range[i] < 0 or target_fit_range[i] > cols:
                    raise ValueError('Value of target fit range is wrong')
