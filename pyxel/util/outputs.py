"""Utility functions for creating outputs."""
import os
import glob
from copy import copy
from shutil import copy2
import typing as t          # noqa: F401
import numpy as np
import astropy.io.fits as fits
import h5py as h5
from time import strftime
from pyxel import __version__ as version
try:
    import matplotlib.pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')        # todo
    pass


class Outputs:
    """TBW."""

    def __init__(self,
                 output_folder: str,
                 save_data_to_file: list = None,
                 save_parameter_to_file: dict = None,
                 parametric_plot: dict = None,
                 calibration_plot: dict = None,
                 single_plot: dict = None):
        """TBW."""
        self.input_file = None                                                  # type: t.Optional[str]
        self.champions_file = None                                              # type: t.Optional[str]
        self.population_file = None                                             # type: t.Optional[str]
        self.parametric_plot = parametric_plot                                  # type: t.Optional[dict]
        self.calibration_plot = calibration_plot                                # type: t.Optional[dict]
        self.single_plot = single_plot                                          # type: t.Optional[dict]
        self.user_plt_args = None                                               # type: t.Optional[dict]
        self.save_parameter_to_file = save_parameter_to_file                    # type: t.Optional[dict]
        self.output_dir = output_folder + '/run_' + strftime("%Y%m%d_%H%M%S")   # type: str
        if save_data_to_file is None:
            self.save_data_to_file = [{'detector.image.array': ['fits']}]       # type: list
        else:
            self.save_data_to_file = save_data_to_file

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            raise IsADirectoryError('Directory exists.')

        self.default_ax_args = {
            'xlabel': None, 'ylabel': None, 'title': None, 'axis': None, 'grid': False,
            'xscale': 'linear', 'yscale': 'linear', 'xticks': None, 'yticks': None,
            'xlim': [None, None], 'ylim': [None, None],
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

        self.plt_args = None                    # type: t.Optional[dict]
        self.parameter_keys = []                # type: list
        plt.figure()

    def set_input_file(self, filename: str):
        """TBW."""
        self.input_file = filename
        copy2(self.input_file, self.output_dir)
        copied_input_file = glob.glob(self.output_dir + '/*.yaml')[0]
        with open(copied_input_file, 'a') as file:
            file.write("\n#########")
            file.write("\n# Pyxel version: " + str(version))
            file.write("\n#########")

    def save_log_file(self):
        """Move log file to the output directory of the simulation."""
        log_file = glob.glob('./pyxel.log')[0]
        os.rename(log_file, self.output_dir + '/' + os.path.basename(log_file))

    def create_champion_file(self):
        """TBW."""
        self.champions_file = self.new_file('champions.out')
        return self.champions_file

    def create_population_file(self):
        """TBW."""
        self.population_file = self.new_file('population.out')
        return self.population_file

    def new_file(self, filename: str):
        """TBW."""
        filename = self.output_dir + '/' + filename
        file = open(filename, 'wb')  # truncate output file
        file.close()
        return filename

    def save_to_png(self, data, name: str):
        """Write array to bitmap PNG image file."""
        row, col = data.shape
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.png')
        fig = plt.figure()
        dpi = 300
        fig.set_size_inches(min(col/dpi, 10.), min(row/dpi, 10.))
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        plt.imshow(data, cmap='gray', extent=[0, col, 0, row])
        plt.savefig(filename, dpi=dpi)
        return filename

    def save_to_fits(self, data, name: str):
        """Write array to FITS file."""
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.fits')
        hdu = fits.PrimaryHDU(data)
        hdu.header['PYXEL_V'] = str(version)
        hdu.writeto(filename, overwrite=False, output_verify='exception')
        return filename

    def save_to_hdf(self, data, name: str):
        """Write detector object to HDF5 file."""
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.h5')
        with h5.File(filename, 'w') as h5file:
            h5file.attrs['pyxel-version'] = str(version)
            if name == 'detector':
                detector_grp = h5file.create_group('detector')
                for array, name in zip([data.signal.array,
                                        data.image.array,
                                        data.photon.array,
                                        data.pixel.array,
                                        data.charge.frame],
                                       ['Signal',
                                        'Image',
                                        'Photon',
                                        'Pixel',
                                        'Charge']):
                    dataset = detector_grp.create_dataset(name, np.shape(array))
                    dataset[:] = array
            else:
                detector_grp = h5file.create_group('data')
                dataset = detector_grp.create_dataset(name, np.shape(data))
                dataset[:] = data
        return filename

    def save_to_txt(self, data, name: str):
        """Write data to txt file."""
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.txt')
        np.savetxt(filename, data, delimiter=' | ', fmt='%.8e')
        return filename

    def save_to_csv(self, data, name: str):
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.csv')
        try:
            data.to_csv(filename, float_format='%g')
        except AttributeError:
            np.savetxt(filename, data, delimiter=',', fmt='%.8e')
        return filename

    def save_to_npy(self, data, name: str):
        """Write Numpy array to Numpy binary npy file."""
        name = str(name).replace('.', '_')
        filename = apply_run_number(self.output_dir + '/' + name + '_??.npy')
        np.save(file=filename, arr=data)
        return filename

    def save_plot(self, filename='figure_??'):
        """Save plot figure in PNG format, close figure and create new canvas for next plot."""
        filename = self.output_dir + '/' + filename + '.png'
        filename = apply_run_number(filename)
        plt.savefig(filename)
        plt.close('all')
        plt.figure()

    def plot_graph(self, x, y, args: dict = None):
        """TBW."""
        arg_tpl = self.update_args(plot_type='graph', new_args=args)
        ax_args, plt_args = self.update_args(plot_type='graph', new_args=self.user_plt_args, def_args=arg_tpl)
        plt.plot(x, y, color=plt_args['color'], marker=plt_args['marker'], linestyle=plt_args['linestyle'])
        update_plot(ax_args)
        plt.draw()

    def plot_histogram(self, data, args: dict = None):
        """TBW."""
        arg_tpl = self.update_args(plot_type='hist', new_args=args)
        ax_args, plt_args = self.update_args(plot_type='hist', new_args=self.user_plt_args, def_args=arg_tpl)
        if isinstance(data, np.ndarray):
            data = data.flatten()
        plt.hist(x=data,
                 bins=plt_args['bins'], range=plt_args['range'],
                 density=plt_args['density'], log=plt_args['log'], cumulative=plt_args['cumulative'],
                 histtype=plt_args['histtype'], color=plt_args['color'], facecolor=plt_args['facecolor'])
        update_plot(ax_args)
        plt.draw()

    def plot_scatter(self, x, y, color=None, args: dict = None):
        """TBW."""
        arg_tpl = self.update_args(plot_type='scatter', new_args=args)
        ax_args, plt_args = self.update_args(plot_type='scatter', new_args=self.user_plt_args, def_args=arg_tpl)
        fig = plt.gcf()
        if color is not None:
            sp = plt.scatter(x, y, c=color, s=plt_args['size'])
            cbar = fig.colorbar(sp)
            cbar.set_label(plt_args['cbar_label'])
        else:
            plt.scatter(x, y, s=plt_args['size'])
        update_plot(ax_args)
        plt.draw()

    def single_output(self, processor):
        """TBW."""
        save_methods = {'fits': self.save_to_fits,
                        'hdf': self.save_to_hdf,
                        'npy': self.save_to_npy,
                        'txt': self.save_to_txt,
                        'csv': self.save_to_csv,
                        'png': self.save_to_png}
        for item in self.save_data_to_file:
            obj = next(iter(item.keys()))
            format_list = next(iter(item.values()))
            data = processor.get(obj)
            if format_list is not None:
                [save_methods[out_format](data=data, name=obj) for out_format in format_list]

        self.user_plt_args = None
        x = processor.detector.photon.array                    # todo: default plots with plot_args?
        y = processor.detector.image.array
        color = None
        if self.single_plot:
            if 'plot_args' in self.single_plot:
                self.user_plt_args = self.single_plot['plot_args']
            if 'x' in self.single_plot:
                x = processor.get(self.single_plot['x'])
            if 'y' in self.single_plot:
                y = processor.get(self.single_plot['y'])
            if 'plot_type' in self.single_plot:
                if isinstance(x, np.ndarray):
                    x = x.flatten()
                if isinstance(y, np.ndarray):
                    y = y.flatten()

                if self.single_plot['plot_type'] == 'graph':
                    self.plot_graph(x, y)
                    fname = 'graph_??'
                elif self.single_plot['plot_type'] == 'histogram':
                    self.plot_histogram(y)
                    fname = 'histogram_??'
                elif self.single_plot['plot_type'] == 'scatter':
                    self.plot_scatter(x, y, color)
                    fname = 'scatter_??'
                else:
                    raise KeyError()
                self.save_plot(fname)

    def champions_plot(self, results):
        """TBW."""
        data = np.loadtxt(self.champions_file)
        generations = data[:, 0].astype(int)
        title = 'Calibrated parameter: '
        items = list(results.items())
        a = 1
        for item in items:
            plt_args = {'xlabel': 'generation', 'linestyle': '-'}
            key = item[0]
            param_value = item[1]
            param_name = key[key.rfind('.') + 1:]
            plt_args['ylabel'] = param_name
            if param_name == 'fitness':
                plt_args['title'] = 'Champion fitness'
                plt_args['color'] = 'red'
            else:
                if key.rfind('.arguments') == -1:
                    mdn = key[:key.rfind('.' + param_name)]
                else:
                    mdn = key[:key.rfind('.arguments')]
                model_name = mdn[mdn.rfind('.') + 1:]
                plt_args['title'] = title + model_name + ' / ' + param_name

            b = 1
            if isinstance(param_value, float) or isinstance(param_value, int):
                column = data[:, a]
                self.plot_graph(generations, column, args=plt_args)
            elif isinstance(param_value, np.ndarray):
                b = len(param_value)
                column = data[:, a:a + b]
                self.plot_graph(generations, column, args=plt_args)
                plt.legend(range(b))

            self.save_plot('calibrated_parameter_??')
            a += b

    def population_plot(self):
        """TBW."""
        data = np.loadtxt(self.population_file)
        fitnesses = np.log10(data[:, 1])
        a, b = 2, 1                             # 1st parameter and fitness
        if self.calibration_plot['population_plot']:
            if 'columns' in self.calibration_plot['population_plot']:
                col = self.calibration_plot['population_plot']['columns']
                a, b = col[0], col[1]
        x = data[:, a]
        y = data[:, b]
        plt_args = {'xlabel': 'calibrated parameter', 'ylabel': 'fitness',
                    'title': 'Population of the last generation',
                    'size': 8, 'cbar_label': 'log(fitness)'}
        if a == 1 or b == 1:
            self.plot_scatter(x, y, args=plt_args)
        else:
            self.plot_scatter(x, y, color=fitnesses, args=plt_args)
        self.save_plot('population_??')

    def calibration_output(self, processor_list, results: dict):
        """TBW."""
        for processor in processor_list:
            self.single_output(processor)

        if self.calibration_plot:
            if 'champions_plot' in self.calibration_plot:
                self.user_plt_args = None
                if self.calibration_plot['champions_plot']:
                    if 'plot_args' in self.calibration_plot['champions_plot']:
                        self.user_plt_args = self.calibration_plot['champions_plot']['plot_args']
                self.champions_plot(results)
            if 'population_plot' in self.calibration_plot:
                self.user_plt_args = None
                if self.calibration_plot['population_plot']:
                    if 'plot_args' in self.calibration_plot['population_plot']:
                        self.user_plt_args = self.calibration_plot['population_plot']['plot_args']
                self.population_plot()

    def params_func(self, param):
        """TBW."""
        for var in param.enabled_steps:
            if var.key not in self.parameter_keys:
                self.parameter_keys += [var.key]
        if self.save_parameter_to_file:
            if self.save_parameter_to_file['parameter']:
                for par in self.save_parameter_to_file['parameter']:
                    if par is not None and par not in self.parameter_keys:
                        self.parameter_keys += [par]

    def extract_func(self, proc):
        """TBW."""
        # self.single_output(processor.detector)    # TODO: extract other things (optional)
        res_row = np.array([])
        for key in self.parameter_keys:
            res_row = np.append(res_row, proc.get(key))
        plt_row = np.array([])
        if self.parametric_plot:
            for key in [self.parametric_plot['x'], self.parametric_plot['y']]:
                if key is not None:
                    plt_row = np.append(plt_row, proc.get(key))
        return {'result': res_row, 'plot': plt_row}

    def merge_func(self, result_list):
        """TBW."""
        result_array = np.array([k['result'] for k in result_list])
        save_methods = {'npy': self.save_to_npy,
                        'txt': self.save_to_txt,
                        'csv': self.save_to_csv}
        if self.save_parameter_to_file:
            for out_format in self.save_parameter_to_file['file_format']:
                file = save_methods[out_format](data=result_array, name='parameters')
                if file.endswith('.txt') or file.endswith('.csv'):
                    with open(file, 'r+') as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write('# ' + ''.join([pp + ' // ' for pp in self.parameter_keys]) + '\n' + content)
        plot_array = np.array([k['plot'] for k in result_list])
        return plot_array

    def plotting_func(self, plot_array):
        """TBW."""
        self.user_plt_args = None
        if self.parametric_plot:
            if 'x' in self.parametric_plot:
                x_key = self.parametric_plot['x']
            else:
                raise KeyError()
            if 'y' in self.parametric_plot:
                y_key = self.parametric_plot['y']
            else:
                raise KeyError()
            if 'plot_args' in self.parametric_plot:
                self.user_plt_args = self.parametric_plot['plot_args']
        else:
            raise KeyError()
        x = plot_array[:, 0]
        y = plot_array[:, 1]
        par_name = x_key[x_key[:x_key[:x_key.rfind('.')].rfind('.')].rfind('.')+1:]
        res_name = y_key[y_key[:y_key[:y_key.rfind('.')].rfind('.')].rfind('.')+1:]
        args = {'xlabel': par_name, 'ylabel': res_name}
        if isinstance(x, np.ndarray):
            x = x.flatten()
        if isinstance(y, np.ndarray):
            y = y.flatten()
        self.plot_graph(x, y, args=args)
        self.save_plot('parametric_??')

    def update_args(self, plot_type: str, new_args: dict = None, def_args: tuple = (None, None)):
        """TBW."""
        ax_args, plt_args = def_args[0], def_args[1]
        if ax_args is None:
            ax_args = copy(self.default_ax_args)
        if plt_args is None:
            if plot_type == 'hist':
                plt_args = copy(self.default_hist_args)
            elif plot_type == 'graph':
                plt_args = copy(self.default_plot_args)
            elif plot_type == 'scatter':
                plt_args = copy(self.default_scatter_args)
            else:
                raise ValueError

        if new_args:
            for key in new_args:
                if key in plt_args.keys():
                    plt_args[key] = new_args[key]
                elif key in ax_args.keys():
                    ax_args[key] = new_args[key]
                else:
                    raise KeyError('Not valid plotting key in "plot_args": "%s"' % key)

        return ax_args, plt_args


def show_plots():
    """Close last empty canvas and show all the previously created figures."""
    plt.close()
    plt.show()


def update_plot(ax_args):
    """TBW."""
    plt.xlabel(ax_args['xlabel'])
    plt.ylabel(ax_args['ylabel'])
    plt.xscale(ax_args['xscale'])
    plt.yscale(ax_args['yscale'])
    plt.xlim(ax_args['xlim'][0], ax_args['xlim'][1])
    plt.ylim(ax_args['ylim'][0], ax_args['ylim'][1])
    plt.title(ax_args['title'])
    if ax_args['axis']:
        plt.axis(ax_args['axis'])
    if ax_args['xticks']:
        plt.xticks(ax_args['xticks'])
    if ax_args['yticks']:
        plt.yticks(ax_args['yticks'])
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
