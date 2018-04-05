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

    def __init__(self, tars,
                 show_plots: bool=False,
                 save_plots: bool=False,
                 file_format: str='png') -> None:
        """TBW.

        :param tars:
        :param show_plots:
        :param save_plots:
        :param file_format:
        """
        self.tars = tars

        self.show_plots = show_plots
        self.save_plots = save_plots
        self.file_format = file_format

    def save_and_draw(self, fig_name: str):
        """TBW.

        :param fig_name:
        :return:
        """
        file_name = fig_name + '.' + self.file_format
        if self.save_plots:
            plt.savefig(file_name)
        if self.show_plots:
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
        self.save_and_draw('edep_per_step')
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
        self.save_and_draw('edep_per_particle')
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
        self.save_and_draw('spectrum_cdf')

    def plot_flux_spectrum(self):
        """
        TBW.

        :return:
        """
        lin_energy_range = self.tars.sim_obj.spectrum_cdf[:, 0]
        flux_dist = self.tars.sim_obj.flux_dist
        plt.figure()
        plt.loglog(lin_energy_range, flux_dist)
        self.save_and_draw('flux_spectrum')

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
        self.save_and_draw('let_cdf')

    def plot_step_cdf(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.step_cdf[:, 0], self.tars.sim_obj.step_cdf[:, 1], '.')
        self.save_and_draw('step_cdf')

    def plot_step_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.step_size_dist['step_size'],
                 self.tars.sim_obj.step_size_dist['counts'], '.')
        self.save_and_draw('step_dist')

    def plot_let_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.plot(self.tars.sim_obj.let_dist[:, 1], self.tars.sim_obj.let_dist[:, 2], '.')
        self.save_and_draw('let_dist')

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
        self.save_and_draw('trajectory_xy')

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
        self.save_and_draw('trajectory_xz')

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
        self.save_and_draw('step_size_histograms')

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
        self.save_and_draw('secondary_spectra')

    def plot_electron_number_histos(self, normalize: bool=None):
        """TBW.

        :return:
        """

        path = Path(__file__).parent.joinpath('data', 'validation')
        hist_names = ['Gaia_bam_ccd_events(13259).npy',
                      # 'Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/complete_G4_H_He_GCR_sim_deposition.npy',
                      'Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_BAM_Gaia_CCDs.npy',
                      'Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_SM_Gaia_CCDs.npy',
                      ]

        plt.figure()
        plt.title('Number of electrons per event')
        for filename in hist_names:

            histogram = np.load(str(Path(path, filename)))

            if normalize:
                plt.hist(histogram, bins=2000, density=True)
            else:
                plt.hist(histogram, bins=2000)

        # plt.axis([0, 15e3, 0, 0.0001])
        plt.axis([0, 15e3, 0, 1E3])

        plt.xlabel('')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('gaia')
