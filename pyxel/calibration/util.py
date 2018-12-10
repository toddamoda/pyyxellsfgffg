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
