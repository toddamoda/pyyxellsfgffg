"""TBW."""
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

    output = []                             # type: list
    for i in range(len(data_path)):
        if '.fits' in data_path[i]:
            data = fits.getdata(data_path[i])
        elif '.npy' in data_path[i]:
            data = np.load(data_path[i])
        else:
            data = np.loadtxt(data_path[i], dtype=float, delimiter='|')     # todo: more general with try-except
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
            raise AttributeError('Fitting range should have 2 or 4 values')
    else:
        return slice(None)


def check_ranges(target_fit_range: t.Optional[t.List[int]],
                 out_fit_range: t.Optional[t.List[int]],
                 rows: int, cols: int):
    """TBW."""
    if target_fit_range:
        if out_fit_range:
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
            if cols is None:
                raise AttributeError('Target data is not a 2 dimensional array')
            if target_fit_range[2] < 0 or target_fit_range[2] > cols:
                raise ValueError('Value of fitting range is wrong')
            if target_fit_range[3] < 0 or target_fit_range[3] > cols:
                raise ValueError('Value of fitting range is wrong')
