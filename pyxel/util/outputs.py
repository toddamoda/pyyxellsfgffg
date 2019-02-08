"""Utility functions for creating outputs."""
import os
import glob
from copy import copy
from shutil import copy2
import numpy as np
import pandas as pd
from PIL import Image
import astropy.io.fits as fits
try:
    import matplotlib.pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')        # todo
    pass


class Outputs:
    """TBW."""

    def __init__(self, output, input):
        """TBW."""
        self.output_dir = apply_run_number(output + '/run_??')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            raise IsADirectoryError('Directory exists.')
        copy2(input, self.output_dir)

        self.default_ax_args = {
            'xlabel': None, 'ylabel': None, 'title': None, 'axis': None, 'grid': False
        }   # type: dict
        self.default_plot_args = {
            'color': None, 'marker': '.', 'linestyle': ''
        }   # type: dict
        self.default_hist_args = {
            'bins': None, 'range': None, 'density': None, 'log': False, 'cumulative': False,
            'histtype': 'step', 'color': None, 'facecolor': None,
        }   # type: dict
        self.default_scatter_args = {
            'size': None, 'cbar_label': None
        }   # type: dict

        self.parameter_values = np.array([])
        self.parameter_keys = []
        self.result_values = np.array([])
        self.result_keys = []
        plt.figure()

    def create_file(self, filename: str = 'calibration.out'):
        """TBW."""
        filename = self.output_dir + '/' + filename
        file = open(filename, 'wb')  # truncate output file
        file.close()
        return filename

    def save_to_bitmap(self, array, filename='image_??'):       # todo: finish, PIL does not work with JPEG !
        """Write array to bitmap PNG image file."""
        filename = self.output_dir + '/' + filename + '.png'
        filename = apply_run_number(filename)
        im = Image.fromarray(array)
        im.save(filename, "PNG")
        # with this, it works: simple_digitization / numpy.uint32
        # with this, it does not work: simple_digitization / numpy.uint16

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
        # todo: append more objects if needed to the same HDF5 file
        # todo: save whole detector object to a HDF5 file?

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

    def get_plotting_arguments(self, plot_type, arg_dict=None):
        """TBW."""
        ax_args = copy(self.default_ax_args)
        if plot_type == 'hist':
            plt_args = copy(self.default_hist_args)
        elif plot_type == 'graph':
            plt_args = copy(self.default_plot_args)
        elif plot_type == 'scatter':
            plt_args = copy(self.default_scatter_args)
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

    def plot_graph(self, x, y, arg_dict=None):
        """TBW."""
        plt_args, ax_args = self.get_plotting_arguments(plot_type='graph', arg_dict=arg_dict)
        plt.plot(x, y,
                 color=plt_args['color'], marker=plt_args['marker'], linestyle=plt_args['linestyle'])
        update_plot(ax_args)
        plt.draw()

    def plot_histogram(self, data, arg_dict=None):
        """TBW."""
        plt_args, ax_args = self.get_plotting_arguments(plot_type='hist', arg_dict=arg_dict)
        if isinstance(data, np.ndarray):
            data = data.flatten()
        plt.hist(x=data,
                 bins=plt_args['bins'], range=plt_args['range'],
                 density=plt_args['density'], log=plt_args['log'], cumulative=plt_args['cumulative'],
                 histtype=plt_args['histtype'], color=plt_args['color'], facecolor=plt_args['facecolor'])
        update_plot(ax_args)
        plt.draw()

    def plot_scatter(self, x, y, color=None, arg_dict=None):
        """TBW."""
        plt_args, ax_args = self.get_plotting_arguments(plot_type='scatter', arg_dict=arg_dict)
        fig = plt.gcf()
        if color is not None:
            sp = plt.scatter(x, y, c=color, s=plt_args['size'])
            cbar = fig.colorbar(sp)
            cbar.set_label(plt_args['cbar_label'])
        else:
            plt.scatter(x, y, s=plt_args['size'])
        update_plot(ax_args)
        plt.draw()

    def single_output(self, detector):
        """TBW."""
        self.save_to_fits(array=detector.image.array)
        # self.save_to_npy(array=detector.image.array)
        plt_args = {'bins': 300, 'xlabel': 'ADU', 'ylabel': 'counts', 'title': 'Image histogram'}
        self.plot_histogram(detector.image.array, arg_dict=plt_args)
        self.save_plot()
        # self.save_to_bitmap(array=detector.image.array)
        # self.save_to_hdf(data=detector.charges.frame, key='charge')
        # self.save_to_csv(dataframe=detector.charges.frame)

    def calibration_output(self, detector, results: dict, files=(None, None), var=(2, 3)):
        """TBW."""
        self.single_output(detector)

        if files[0] is not None:
            data = np.loadtxt(files[0])
            generations = data[:, 0]
            plt_args1 = {'xlabel': 'generation', 'linestyle': '-'}
            title = 'Calibrated parameter: '
            items = list(results.items())
            a = 1
            for item in items:

                key = item[0]
                param_value = item[1]
                param_name = key[key.rfind('.') + 1:]
                plt_args1['ylabel'] = param_name
                if param_name == 'fitness':
                    plt_args1['title'] = 'Champion fitness'
                    plt_args1['color'] = 'red'
                else:
                    if key.rfind('.arguments') == -1:
                        mdn = key[:key.rfind('.' + param_name)]
                    else:
                        mdn = key[:key.rfind('.arguments')]
                    model_name = mdn[mdn.rfind('.') + 1:]
                    plt_args1['title'] = title + model_name + ' / ' + param_name

                b = 1
                if isinstance(param_value, float) or isinstance(param_value, int):
                    column = data[:, a]
                    self.plot_graph(generations, column, arg_dict=plt_args1)
                    self.save_plot()
                elif isinstance(param_value, np.ndarray):
                    b = len(param_value)
                    column = data[:, a:a + b]
                    self.plot_graph(generations, column, arg_dict=plt_args1)
                    plt.legend(range(b))
                    self.save_plot()
                a += b
                if 'color' in plt_args1.keys():
                    plt_args1.pop('color')

        if files[1] is not None:
            data = np.loadtxt(files[1])
            fitnesses = np.log10(data[:, 1])
            x = data[:, var[0]]
            y = data[:, var[1]]
            plt_args2 = {'xlabel': 'x', 'ylabel': 'y', 'title': 'Population of the last generation',
                         'size': 8, 'cbar_label': 'log(fitness)'}
            self.plot_scatter(x, y, color=fitnesses, arg_dict=plt_args2)
            self.save_plot()

    def add_parametric_step(self, parametric, processor, results: list = None):
        """TBW."""
        self.single_output(processor.detector)

        row = np.array([])
        for var in parametric.enabled_steps:
            row = np.append(row, processor.get(var.key))
            if var.key not in self.parameter_keys:
                self.parameter_keys += [var.key]
        
        if self.parameter_values.size == 0:
            self.parameter_values = row 
        else:
            self.parameter_values = np.vstack((self.parameter_values, row))

        if results is not None:
            row_2 = np.array([])
            for key in results:
                row_2 = np.append(row_2, processor.get(key))
                if key not in self.result_keys:
                    self.result_keys += [key]
                
            if self.result_values.size == 0:
                self.result_values = row_2
            else:
                self.result_values = np.vstack((self.result_values, row_2))

    def parametric_output(self, parameter_key, result_key):
        """TBW."""
        x = self.parameter_values[:, self.parameter_keys.index(parameter_key)]
        y = self.result_values[:, self.result_keys.index(result_key)]
        title = 'Parametric analysis'
        par_name = parameter_key[parameter_key.rfind('.') + 1:]
        res_name = result_key[result_key.rfind('.') + 1:]
        plt_args = {'xlabel': par_name, 'ylabel': res_name, 'title': title}
        self.plot_graph(x, y, arg_dict=plt_args)
        self.save_plot()
        

def show_plots():
    """Close last empty canvas Show all the previously created figures."""
    plt.close()
    plt.show()


def update_plot(ax_args):
    """TBW."""
    plt.xlabel(ax_args['xlabel'])
    plt.ylabel(ax_args['ylabel'])
    plt.title(ax_args['title'])
    if ax_args['axis']:
        plt.axis(ax_args['axis'])
    plt.grid(ax_args['grid'])


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
