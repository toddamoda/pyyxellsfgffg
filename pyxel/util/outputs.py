"""Utility functions for creating outputs."""
import glob
import numpy as np
import astropy.io.fits as fits
try:
    import matplotlib.pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')        # TODO
    pass


def output_numpy_array(array, filename):
    """TBW."""
    np.save(file=filename, arr=array)


def show_plots():
    """TBW."""
    plt.show()


def output_graph_plot(data, name, output_dir):
    """TBW."""
    pass


def output_hist_plot(data, name, output_dir):
    """TBW."""
    plt.figure()
    xlabel = None
    ylabel = None
    title = None
    # axis = None
    # bins = None
    # density = None
    # histtype = 'bar'
    # facecolor = 'b'

    if isinstance(data, np.ndarray):
        data = data.flatten()
    n, bins, patches = plt.hist(x=data,
                                # bins=bins, range=range,
                                # density=density, histtype=histtype, facecolor=facecolor
                                )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # plt.axis(axis)
    # plt.grid(True)
    plt.savefig(output_dir + '/' + name)
    plt.draw()


def output_image(array, name, output_dir):
    """TBW."""
    filename_image = output_dir + '/' + name + '_??.fits'
    filename_image = apply_run_number(filename_image)
    hdu = fits.PrimaryHDU(array)
    if filename_image is not None:
        hdu.writeto(filename_image, overwrite=False, output_verify='exception')


def update_fits_header(header, key, value):
    """TBW.

    :param header:
    :param key:
    :param value:
    :return:
    """
    if not isinstance(value, (str, int, float)):
        value = '%r' % value
    if isinstance(value, str):
        value = value[0:24]
    if isinstance(key, (list, tuple)):
        key = '/'.join(key)
    key = key.replace('.', '/')[0:36]
    header[key] = value


def apply_run_number(path):
    """Convert the file name numeric placeholder to a unique number.

    :param path:
    :return:
    """
    path_str = str(path)
    if '?' in path_str:
        dir_list = sorted(glob.glob(path_str))
        p_0 = path_str.find('?')
        p_1 = path_str.rfind('?')
        template = path_str[p_0: p_1 + 1]
        path_str = path_str.replace(template, '{:0%dd}' % len(template))
        last_num = 0
        if len(dir_list):
            path_last = dir_list[-1]
            last_num = int(path_last[p_0: p_1 + 1])
        last_num += 1
        path_str = path_str.format(last_num)
    return type(path)(path_str)
