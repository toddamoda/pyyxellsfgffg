#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! TARS model for charge generation by ionization."""

# import logging
# import math

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
# import typing as t   # noqa: F401
from mpl_toolkits.mplot3d import Axes3D     # noqa: F401


class PlottingTARS:
    """
    Plotting class for TARS.

    :return:
    """

    def __init__(self, tars) -> None:
        """
        TBW.

        :param tars:
        """
        self.tars = tars

    def show_plots(self):
        """
        TBW.

        :return:
        """
        plt.show()

    def save_edep(self):
        """
        TBW.

        :return:
        """
        np.save('orig2_edep_per_step_10k', self.tars.sim_obj.edep_per_step)
        np.save('orig2_edep_per_particle_10k', self.tars.sim_obj.total_edep_per_particle)

    def plot_edep_per_step(self):
        """
        TBW.

        :return:
        """
        plt.figure()
        n, bins, patches = plt.hist(self.tars.sim_obj.edep_per_step, 300, facecolor='b')
        plt.xlabel('E_dep (keV)')
        plt.ylabel('Counts')
        plt.title('Histogram of E deposited per step')
        # plt.axis([0, 0.003, 0, 1.05*max(n)])
        plt.grid(True)
        plt.draw()
        return n, bins, patches

    def plot_edep_per_particle(self):
        """
        TBW.

        :return:
        """
        plt.figure()
        n, bins, patches = plt.hist(self.tars.sim_obj.total_edep_per_particle, 200, facecolor='g')
        plt.xlabel('E_dep (keV)')
        plt.ylabel('Counts')
        plt.title('Histogram of total E deposited per particle')
        # plt.axis([0, 0.4, 0, 1.05*max(n)])
        plt.grid(True)
        plt.draw()
        return n, bins, patches

    def plot_spectrum_cdf(self):
        """
        TBW.

        :return:
        """
        lin_energy_range = self.tars.sim_obj.spectrum_cdf[:, 0]
        cum_sum = self.tars.sim_obj.spectrum_cdf[:, 1]
        plt.figure()
        plt.semilogx(lin_energy_range, cum_sum)
        plt.draw()

    def plot_flux_spectrum(self):
        """
        TBW.

        :return:
        """
        lin_energy_range = self.tars.sim_obj.spectrum_cdf[:, 0]
        flux_dist = self.tars.sim_obj.flux_dist
        plt.figure()
        plt.loglog(lin_energy_range, flux_dist)
        plt.draw()

    def plot_charges_3d(self):
        """
        TBW.

        :return:
        """
        geo = self.tars.sim_obj.detector.geometry

        # set up a figure twice as wide as it is tall
        fig = plt.figure(figsize=plt.figaspect(0.5))

        size = self.tars.sim_obj.e_num_lst
        ax = fig.add_subplot(1, 2, 1, projection='3d')
        ax.scatter(self.tars.sim_obj.e_pos0_lst, self.tars.sim_obj.e_pos1_lst, self.tars.sim_obj.e_pos2_lst,
                   c='b', marker='.', s=size)
        # ax.plot(self.tars.sim_obj.particle.trajectory[:, 0],
        #         self.tars.sim_obj.particle.trajectory[:, 1],
        #         self.tars.sim_obj.particle.trajectory[:, 2], 'c-')

        ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        ax2.scatter(self.tars.sim_obj.e_pos0_lst, self.tars.sim_obj.e_pos1_lst, 0,
                    c='r', marker='.', s=size)

        ax.set_xlim(0, geo.vert_dimension)
        ax.set_ylim(0, geo.horz_dimension)
        ax.set_zlim(-1 * geo.total_thickness, 0)
        ax.set_xlabel('vertical ($\mu$m)')
        ax.set_ylabel('horizontal ($\mu$m)')
        ax.set_zlabel('z ($\mu$m)')

        ax2.set_xlim(0, geo.vert_dimension)
        ax2.set_ylim(0, geo.horz_dimension)
        ax2.set_zlim(-1 * geo.total_thickness, 0)
        ax2.set_xlabel('vertical ($\mu$m)')
        ax2.set_ylabel('horizontal ($\mu$m)')
        ax2.set_zlabel('z ($\mu$m)')

    def plot_let_cdf(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.let_cdf[:, 0], self.tars.sim_obj.let_cdf[:, 1], '.')
        plt.draw()

    def plot_step_cdf(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.step_cdf[:, 0], self.tars.sim_obj.step_cdf[:, 1], '.')
        plt.draw()

    def plot_step_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.step_size_dist['step_size'],
                 self.tars.sim_obj.step_size_dist['counts'], '.')
        plt.draw()

    def plot_let_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.let_dist[:, 1], self.tars.sim_obj.let_dist[:, 2], '.')
        plt.draw()

    def plot_trajectory_xy(self):
        """TBW.

        :return:
        """
        plt.figure()
        geo = self.tars.sim_obj.detector.geometry
        # self.trajectory[:, 0] - VERTICAL COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(self.tars.sim_obj.particle.trajectory[:, 1], self.tars.sim_obj.particle.trajectory[:, 0], '.')
        plt.xlabel('horizontal ($\mu$m)')
        plt.ylabel('vertical ($\mu$m)')
        plt.title('p trajectory in CCD')
        plt.axis([0, geo.horz_dimension, 0, geo.vert_dimension])
        plt.grid(True)
        plt.draw()

    def plot_trajectory_xz(self):
        """TBW.

        :return:
        """
        plt.figure()
        geo = self.tars.sim_obj.detector.geometry
        # self.trajectory[:, 2] - Z COORDINATE
        # self.trajectory[:, 1] - HORIZONTAL COORDINATE
        plt.plot(self.tars.sim_obj.particle.trajectory[:, 1], self.tars.sim_obj.particle.trajectory[:, 2], '.')
        plt.xlabel('horizontal ($\mu$m)')
        plt.ylabel('z ($\mu$m)')
        plt.title('p trajectory in CCD')
        plt.axis([0, geo.horz_dimension, -1*geo.total_thickness, 0])
        plt.grid(True)
        plt.draw()

    def plot_step_size_histograms(self, normalize: bool=None):
        """TBW.

        :return:
        """
        energies = ['100MeV', '1GeV']
        thicknesses = ['10um', '50um', '100um', '200um']
        p_types = ['proton']

        path = Path(__file__).parent.joinpath('data', 'inputs')

        # step_rows = 10000

        plt.figure()
        plt.title('Step size')
        for p_type in p_types:
            for energy in energies:
                for thickness in thicknesses:
                    filename = 'stepsize_' + p_type + '_' + energy + '_' + thickness + '_1M.ascii'
                    step_size = pd.read_csv(str(Path(path, filename)),
                                            delimiter="\t", names=["step_size", "counts"], usecols=[1, 2],
                                            skiprows=4, nrows=10000)

                    if normalize:
                        plotted_counts = step_size['counts'] / sum(step_size['counts'])
                    else:
                        plotted_counts = step_size['counts']

                    plt.plot(step_size['step_size'], plotted_counts, '.-',
                             label=p_type + ', ' + energy + ', ' + thickness)

        plt.axis([0, 200, 0, 0.025])
        plt.xlabel('Step size')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        plt.draw()

    def plot_secondary_spectra(self, normalize: bool=None):
        """TBW.

        :return:
        """
        energies = ['100MeV', '1GeV']
        thicknesses = ['10um', '50um', '100um', '200um']
        p_types = ['proton']

        path = Path(__file__).parent.joinpath('data', 'inputs')

        # step_rows = 10000

        plt.figure()
        plt.title('Electron spectrum')
        for p_type in p_types:
            for energy in energies:
                for thickness in thicknesses:
                    filename = 'stepsize_' + p_type + '_' + energy + '_' + thickness + '_1M.ascii'
                    spectrum = pd.read_csv(str(Path(path, filename)),
                                           delimiter="\t", names=["energy", "counts"], usecols=[1, 2],
                                           skiprows=10008, nrows=200)

                    if normalize:
                        plotted_counts = spectrum['counts'] / sum(spectrum['counts'])
                    else:
                        plotted_counts = spectrum['counts']

                    plt.plot(spectrum['energy'], plotted_counts, '.-', label=p_type + ', ' + energy + ', ' + thickness)

        # plt.axis([0, 6.0, 0, 0.12])
        plt.xlabel('Energy')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        plt.draw()
