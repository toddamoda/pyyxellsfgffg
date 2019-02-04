"""Utility functions for creating outputs."""
import glob
from copy import copy
import numpy as np
import pandas as pd
from PIL import Image
import astropy.io.fits as fits
try:
    import matplotlib.pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')        # TODO
    pass


class Outputs:
    """TBW."""

    def __init__(self, output_dir):
        """TBW."""
        self.output_dir = output_dir
        self.default_ax_args = {
            'xlabel': None, 'ylabel': None, 'title': None, 'axis': None, 'grid': False
        }
        self.default_plot_args = {
            'color': None, 'marker': '.', 'linestyle': '', 'label': None
        }
        self.default_hist_args = {
            'bins': None, 'range': None, 'density': None, 'log': False, 'cumulative': False,
            'histtype': 'step', 'color': None, 'facecolor': None, 'label': None
        }
        plt.figure()

    def save_to_bitmap(self, array, filename='image_??'):       # TODO finish, PIL does not work with JPEG !
        """Write array to bitmap PNG image file."""
        filename = self.output_dir + '/' + filename + '.png'
        filename = apply_run_number(filename)
        im = Image.fromarray(array)
        im.save(filename, "PNG")

    def save_to_fits(self, array, filename='image_??'):
        """Write array to FITS file."""
        filename = self.output_dir + '/' + filename + '.fits'
        filename = apply_run_number(filename)
        hdu = fits.PrimaryHDU(array)
        if filename is not None:
            hdu.writeto(filename, overwrite=False, output_verify='exception')

    def save_to_hdf(self, data, key='data', filename='store_??'):
        """Write object to HDF5 file."""
        filename = self.output_dir + '/' + filename + '.h5'
        filename = apply_run_number(filename)
        with pd.HDFStore(filename) as store:
            store[key] = data
        # TODO: append more objects if needed to the same HDF5 file
        # TODO: save whole detector object to a HDF5 file?

    def save_to_csv(self, dataframe: pd.DataFrame, filename='dataframe_??'):
        """Write pandas Dataframe to CSV file."""
        filename = self.output_dir + '/' + filename + '.csv'
        filename = apply_run_number(filename)
        dataframe.to_csv(filename, float_format='%g')

    def save_to_npy(self, array, filename='array_??'):
        """Write array to Numpy binary npy file."""
        filename = self.output_dir + '/' + filename + '.npy'
        filename = apply_run_number(filename)
        np.save(file=filename, arr=array)

    def save_plot(self, filename='figure_??'):
        """Save plot figure in PNG format and create new figure canvas for next plot."""
        filename = self.output_dir + '/' + filename + '.png'
        filename = apply_run_number(filename)
        plt.savefig(filename)
        plt.figure()

    def show_plots(self):
        """Show all the previously created figures."""
        plt.show()

    def get_plotting_arguments(self, plot_type, arg_dict=None):
        """TBW."""
        ax_args = copy(self.default_ax_args)
        if plot_type == 'hist':
            plt_args = copy(self.default_hist_args)
        elif plot_type == 'graph':
            plt_args = copy(self.default_plot_args)
        else:
            raise ValueError
        if arg_dict:
            for key in arg_dict.keys():
                if key in plt_args.keys():
                    plt_args[key] = arg_dict[key]
                elif key in ax_args.keys():
                    ax_args[key] = arg_dict[key]
                else:
                    raise KeyError
        return plt_args, ax_args

    def update_plot(self, ax_args):
        """TBW."""
        plt.xlabel(ax_args['xlabel'])
        plt.ylabel(ax_args['ylabel'])
        plt.title(ax_args['title'])
        if ax_args['axis']:
            plt.axis(ax_args['axis'])
        plt.grid(ax_args['grid'])
        plt.legend()

    def plot_graph(self, x, y, name, arg_dict=None):
        """TBW."""
        plt_args, ax_args = self.get_plotting_arguments(plot_type='graph', arg_dict=arg_dict)
        if isinstance(x, np.ndarray):
            x = x.flatten()
        if isinstance(y, np.ndarray):
            y = y.flatten()
        plt.plot(x, y, label=name,
                 color=plt_args['color'], marker=plt_args['marker'], linestyle=plt_args['linestyle'])
        self.update_plot(ax_args)
        plt.draw()

    def plot_histogram(self, data, name, arg_dict=None):
        """TBW."""
        plt_args, ax_args = self.get_plotting_arguments(plot_type='hist', arg_dict=arg_dict)
        if isinstance(data, np.ndarray):
            data = data.flatten()
        plt.hist(x=data, label=name,
                 bins=plt_args['bins'], range=plt_args['range'],
                 density=plt_args['density'], log=plt_args['log'], cumulative=plt_args['cumulative'],
                 histtype=plt_args['histtype'], color=plt_args['color'], facecolor=plt_args['facecolor'])
        self.update_plot(ax_args)
        plt.draw()


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
