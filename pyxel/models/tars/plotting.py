#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! TARS model for charge generation by ionization."""

# import logging
# import math

import numpy as np
from matplotlib import pyplot as plt
# import pandas as pd
from pathlib import Path
# import typing as t   # noqa: F401
from mpl_toolkits.mplot3d import Axes3D     # noqa: F401


class PlottingTARS:
    """
    Plotting class for TARS.

    :return:
    """

    def __init__(self, tars,
                 draw_plots: bool=False,
                 save_plots: bool=False,
                 file_format: str='png') -> None:
        """TBW.

        :param tars:
        :param draw_plots:
        :param save_plots:
        :param file_format:
        """
        self.tars = tars

        self.draw_plots = draw_plots
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
        if self.draw_plots:
            plt.draw()

    def show(self):
        """TBW.

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

    # def plot_spectrum_cdf(self):
    #     """
    #     TBW.
    #
    #     :return:
    #     """
    #     lin_energy_range = self.tars.sim_obj.spectrum_cdf[:, 0]
    #     cum_sum = self.tars.sim_obj.spectrum_cdf[:, 1]
    #     plt.figure()
    #     plt.title('Spectrum CDF')
    #     # plt.semilogx(lin_energy_range, cum_sum)
    #     self.save_and_draw('spectrum_cdf')
    #
    def plot_flux_spectrum(self):
        """
        TBW.

        :return:
        """
        lin_energy_range = self.tars.sim_obj.spectrum_cdf[:, 0]
        flux_dist = self.tars.sim_obj.flux_dist
        plt.figure()
        plt.title('Proton flux spectrum (CREME data)')
        plt.xlabel('Energy (MeV)')
        plt.ylabel('Flux (1/(s*MeV))')
        plt.loglog(lin_energy_range, flux_dist)
        self.save_and_draw('flux_spectrum')

    # def plot_spectrum_hist(self, normalize: bool = None):
    #     """
    #     TBW.
    #
    #     :return:
    #     """
    #     plt.figure()
    #     plt.title('Proton flux spectrum sampled by TARS')
    #     plt.xlabel('Energy (MeV)')
    #     plt.ylabel('Counts')
    #     # plt.ylabel('Flux (1/(s*MeV))')
    #     # plt.loglog(lin_energy_range, flux_dist)
    #
    #     hist_bins = 500
    #     hist_range = (1e-1, 1e5)
    #
    #     col = (1, 1, 1, 1)
    #
    #     if normalize:
    #         plt.hist(self.tars.sim_obj.p_energy_lst_per_event, log=True, bins=hist_bins,
    #                  range=hist_range, fc=col, density=True)
    #     else:
    #         plt.hist(self.tars.sim_obj.p_energy_lst_per_event, log=True, bins=hist_bins,
    #                  range=hist_range, fc=col)
    #
    #     # plt.legend(loc='upper right')
    #     self.save_and_draw('tars_spectrum')

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
        plt.title('LET CDF')
        plt.plot(self.tars.sim_obj.let_cdf[:, 0], self.tars.sim_obj.let_cdf[:, 1], '.')
        self.save_and_draw('let_cdf')

    def plot_step_cdf(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.title('Step size CDF')
        plt.plot(self.tars.sim_obj.step_cdf[:, 0], self.tars.sim_obj.step_cdf[:, 1], '.')
        self.save_and_draw('step_cdf')

    def plot_step_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.title('Step size distribution')
        plt.plot(self.tars.sim_obj.step_size_dist['step_size'],
                 self.tars.sim_obj.step_size_dist['counts'], '.')
        self.save_and_draw('step_dist')

    def plot_tertiary_number_cdf(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.title('Tertiary electron number CDF')
        plt.plot(self.tars.sim_obj.elec_number_cdf[:, 0], self.tars.sim_obj.elec_number_cdf[:, 1], '.')
        self.save_and_draw('elec_number_cdf')

    def plot_tertiary_number_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.title('Tertiary electron number distribution')
        plt.plot(self.tars.sim_obj.elec_number_dist['electron'],
                 self.tars.sim_obj.elec_number_dist['counts'], '.')
        self.save_and_draw('elec_number_dist')

    def plot_let_dist(self):
        """TBW.

        :return:
        """
        plt.figure()
        plt.title('LET dist')
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

    def plot_track_histogram(self, histogram_data, normalize: bool = None):
        """TBW.

        :return:
        """
        hist_bins = 500
        hist_range = (0, 200)

        plt.figure()
        plt.title('Proton track length distribution')

        col = (1, 0, 1, 1)

        if normalize:
            plt.hist(histogram_data, bins=hist_bins, range=hist_range, fc=col, density=True)
        else:
            plt.hist(histogram_data, bins=hist_bins, range=hist_range, fc=col)

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel('Track length')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('track_length')

    # def plot_step_size_histograms(self, normalize: bool=None):
    #     """TBW.
    #
    #     :return:
    #     """
    #     energies = ['100MeV', '1GeV']
    #     thicknesses = ['10um', '50um', '100um', '200um']
    #     p_types = ['proton']
    #
    #     path = Path(__file__).parent.joinpath('data', 'inputs')
    #
    #     # step_rows = 10000
    #
    #     plt.figure()
    #     plt.title('Step size')
    #     for p_type in p_types:
    #         for energy in energies:
    #             for thickness in thicknesses:
    #                 filename = 'stepsize_' + p_type + '_' + energy + '_' + thickness + '_1M.ascii'
    #                 step_size = pd.read_csv(str(Path(path, filename)),
    #                                         delimiter="\t", names=["step_size", "counts"], usecols=[1, 2],
    #                                         skiprows=4, nrows=10000)
    #
    #                 if normalize:
    #                     plotted_counts = step_size['counts'] / sum(step_size['counts'])
    #                 else:
    #                     plotted_counts = step_size['counts']
    #
    #                 plt.plot(step_size['step_size'], plotted_counts, '.-',
    #                          label=p_type + ', ' + energy + ', ' + thickness)
    #
    #     plt.axis([0, 200, 0, 0.025])
    #     plt.xlabel('Step size')
    #     plt.ylabel('Counts')
    #     plt.legend(loc='upper right')
    #     self.save_and_draw('step_size_histograms')
    #
    # def plot_secondary_spectra(self, normalize: bool=None):
    #     """TBW.
    #
    #     :return:
    #     """
    #     energies = ['100MeV', '1GeV']
    #     thicknesses = ['10um', '50um', '100um', '200um']
    #     p_types = ['proton']
    #
    #     path = Path(__file__).parent.joinpath('data', 'inputs')
    #
    #     # step_rows = 10000
    #
    #     plt.figure()
    #     plt.title('Electron spectrum')
    #     for p_type in p_types:
    #         for energy in energies:
    #             for thickness in thicknesses:
    #                 filename = 'stepsize_' + p_type + '_' + energy + '_' + thickness + '_1M.ascii'
    #                 spectrum = pd.read_csv(str(Path(path, filename)),
    #                                        delimiter="\t", names=["energy", "counts"], usecols=[1, 2],
    #                                        skiprows=10008, nrows=200)
    #
    #                 if normalize:
    #                     plotted_counts = spectrum['counts'] / sum(spectrum['counts'])
    #                 else:
    #                     plotted_counts = spectrum['counts']
    #
    #                 plt.plot(spectrum['energy'], plotted_counts, '.-',
    #                          label=p_type + ', ' + energy + ', ' + thickness)
    #
    #     # plt.axis([0, 6.0, 0, 0.12])
    #     plt.xlabel('Energy')
    #     plt.ylabel('Counts')
    #     plt.legend(loc='upper right')
    #     self.save_and_draw('secondary_spectra')

    def plot_gaia_vs_geant4_hist(self, normalize: bool=None):
        """TBW.

        :return:
        """
        # Geant4 (GRAS) simulation results (by Giovanni?) + GAIA BAM data - Perfect overlap in case of normalization!
        path = Path(__file__).parent.joinpath('data', 'validation', 'Gaia_CCD_study-20180404T115340Z-001',
                                              'Gaia_CCD_study', 'Data')
        hist_names = [
                      'complete_G4_H_He_GCR_sim_deposition.npy',  # G4, contains a lot of events with ZERO number of e-!
                      'CRs_from_BAM_Gaia_CCDs.npy',               # GAIA BAM data
                      ]
        labels = ['Geant4 data', 'GAIA BAM data']
        i = 0

        hist_bins = 500
        hist_range = (1, 15E3)

        plt.figure()
        plt.title('Number of electrons per event')
        for filename in hist_names:

            histogram = np.load(str(Path(path, filename)))

            if i == 0:
                col = (0, 0, 1, 0.5)
            if i == 1:
                col = (0, 1, 0, 0.5)

            if normalize:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col, density=True)
            else:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col)

            i += 1

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel('')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('gaia_vs_geant4_electron_hist')

    def plot_old_tars_hist(self, normalize: bool=None):
        """TBW.

        :return:
        """
        # earlier TARS results of Lionel
        folder_path = Path(__file__).parent.joinpath('data', 'validation', 'Results-20180404T121902Z-001', 'Results')
        hist_names = [
                       # '10000 events from random protons CREME96 (16um - SM)(22-08-2016_16h36)',  # 16 um SM
                       '10000 events from random protons CREME96 (16um - SM)(22-08-2016_16h41)',    # 16 um SM
                       '10000 events from random protons CREME96 (step=0.5)(16-08-2016_15h56)',     # 40 um BAM
                       ]
        labels = ['TARS data (Lionel), SM (16um)', 'TARS data (Lionel), BAM (40um)']
        i = 0

        hist_bins = 500
        hist_range = (1, 15E3)

        plt.figure()
        plt.title('Number of electrons per event')
        for filename in hist_names:

            histogram = np.load(str(Path(folder_path.joinpath(filename), 'Raw data/Electrons_generated.npy')))

            if i == 0:
                col = (1, 0, 0, 0.5)
            if i == 1:
                col = (0, 1, 0, 0.5)

            if normalize:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col, density=True)
            else:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col)

            i += 1

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel('')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('old_tars_electron_hist')

    def plot_gaia_bam_vs_sm_electron_hist(self, normalize: bool=None):
        """TBW.

        :return:
        """
        path = Path(__file__).parent.joinpath('data', 'validation')
        hist_names = [
                      # 'Gaia_bam_ccd_events(13259).npy', NEM JOOOOO
                      'Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_BAM_Gaia_CCDs.npy',
                      'Gaia_CCD_study-20180404T115340Z-001/Gaia_CCD_study/Data/CRs_from_SM_Gaia_CCDs.npy'
        ]
        labels = ['GAIA SM (16um) data', 'GAIA BAM (40um) data']
        i = 0

        hist_bins = 500
        hist_range = (1, 15E3)

        plt.figure()
        plt.title('Number of electrons per event')
        for filename in hist_names:

            histogram = np.load(str(Path(path, filename)))

            if i == 0:
                col = (1, 0, 0, 0.5)
            if i == 1:
                col = (0, 0, 1, 0.5)

            if normalize:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col, density=True)
            else:
                plt.hist(histogram, bins=hist_bins, range=hist_range, label=labels[i], fc=col)

            i += 1

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel('')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('gaia_BAM_vs_SM_electron_hist')

    def plot_electron_hist(self, data1, data2=None, data3=None, normalize: bool=None):
        """TBW.

        :return:
        """
        labels = [
            'TARS data (David), 40um'
            # 'Geant4 data (David), 40um, 100MeV',
            # 'secondary e-',
            # 'tertiary e-'
        ]
        i = 0

        hist_bins = 500
        # hist_range = (0, 15E3)
        hist_range = (0, 1.5E3)

        plt.figure()
        plt.title('Number of electrons per event')

        if normalize:
            plt.hist(data1, bins=hist_bins, range=hist_range, label=labels[i], fc=(1, 0, 0, 0.5), density=True)
            if data2:
                i += 1
                plt.hist(data2, bins=hist_bins, range=hist_range, label=labels[i], fc=(1, 1, 0, 0.5), density=True)
                if data3:
                    i += 1
                    plt.hist(data3, bins=hist_bins, range=hist_range, label=labels[i], fc=(0, 1, 1, 0.5), density=True)

        else:
            plt.hist(data1, bins=hist_bins, range=hist_range, label=labels[i], fc=(1, 0, 0, 0.5))
            if data2:
                i += 1
                plt.hist(data2, bins=hist_bins, range=hist_range, label=labels[i], fc=(1, 1, 0, 0.5))
                if data3:
                    i += 1
                    plt.hist(data3, bins=hist_bins, range=hist_range, label=labels[i], fc=(0, 1, 1, 0.5))

        # plt.axis([0, 15e3, 0, 0.0001])
        # plt.axis([0, 15e3, 0, 3E3])

        plt.xlabel('')
        plt.ylabel('Counts')
        plt.legend(loc='upper right')
        self.save_and_draw('electron_hist')
