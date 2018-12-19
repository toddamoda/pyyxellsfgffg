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
            data = np.loadtxt(data_path[i], delimiter='|')     # todo: more general with try-except
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


# def check_array_types(a, b):
#     """TBW.
#
#     :param a: np
#     :param b:
#     :return:
#     """
#     if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
#         if a.dtype and b.dtype in [np.int32, np.int64]:
#             pass
#         elif a.dtype and b.dtype in [np.float16, np.float32, np.float64]:
#             pass
#         elif a.dtype and b.dtype in [np.uint16, np.uint32, np.uint64]:
#             pass
#         else:
#             raise TypeError('Numpy.ndarray objects should have the same type.')
#     else:
#         raise TypeError('Arrays should be numpy.ndarray objects.')
