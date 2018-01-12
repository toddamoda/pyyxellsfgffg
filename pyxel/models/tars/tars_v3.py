#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Lionel Garcia <lionel_garcia@live.fr>
#
#   This is restricted software and is only to be used with permission
#   from the author, or from ESA.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#   --------------------------------------------------------------------------
#
# Not fully commented

from os import path
import math
import numpy as np
import time
from tqdm import tqdm
from scipy import interpolate
import matplotlib.pyplot as plt

from pyxel.models.tars.lib.simulation import Simulation

TARS_DIR = path.dirname(path.abspath(__file__))


def read_data(file_name):
    data = np.loadtxt(file_name, 'float', '#')
    return data


def interpolate_data(data):
    data_function = interpolate.interp1d(data[:, 0], data[:, 1], kind='linear')
    return data_function


class TARS:
    
    def __init__(self, pyxel_ccd_obj=None):

        self.ccd = pyxel_ccd_obj

        self.init_energy = 0
        self.particle_number = 0
        self.angle_alpha = 0
        self.angle_beta = 0
        self.position_ver = 0
        self.position_hor = 0
        self.position_z = 0
        self.step_length = 0

        self.data_folder = TARS_DIR + r'\data'
        self.results_folder = self.data_folder + r'\results'

        self.sim_obj = Simulation(self.ccd)

    def set_initial_energy(self, energy):
        self.init_energy = energy

    def set_particle_number(self, number):
        self.particle_number = number

    def set_incident_angles(self, alpha, beta):
        self.angle_alpha = alpha
        self.angle_beta = beta

    def set_starting_position(self, position_vertical, position_horizontal, position_z):
        self.position_ver = position_vertical
        self.position_hor = position_horizontal
        self.position_z = position_z

    def set_stepping_length(self, stepping):
        self.step_length = stepping  # micrometer

    def get_deposited_charge(self):
        # print('counter:', self.sim_obj.counter)
        return self.sim_obj.total_charge_array

    def run(self):
        start_time = time.time()
        print("TARS - simulation processing...\n")

        self.sim_obj.parameters(self.init_energy,
                                self.position_ver, self.position_hor, self.position_z,
                                self.angle_alpha, self.angle_beta,
                                self.step_length)

        for i in tqdm(range(0, self.particle_number)):
            dep = 0
            while dep == 0:
                dep = self.sim_obj.event_generation()
            # print('total deposited E: {0:4.2f} keV'.format(dep))


        # np.save('orig2_edep_per_step_10k', self.sim_obj.edep_per_step)
        # np.save('orig2_edep_per_particle_10k', self.sim_obj.total_edep_per_particle)

        self.plot_edep_per_step()
        self.plot_edep_per_particle()
        plt.show()

        self.sim_obj.processing_time = time.time() - start_time

    def plot_edep_per_step(self):
        plt.figure()
        n, bins, patches = plt.hist(self.sim_obj.edep_per_step, 500, facecolor='b')
        plt.xlabel('E_dep (keV)')
        plt.ylabel('Counts')
        plt.title('Histogram of E deposited per step')
        # plt.axis([0, 0.003, 0, 1.05*max(n)])
        plt.grid(True)
        plt.draw()
        return n, bins, patches

    def plot_edep_per_particle(self):
        plt.figure()
        n, bins, patches = plt.hist(self.sim_obj.total_edep_per_particle, 500, facecolor='g')
        plt.xlabel('E_dep (keV)')
        plt.ylabel('Counts')
        plt.title('Histogram of total E deposited per particle')
        # plt.axis([0, 0.4, 0, 1.05*max(n)])
        plt.grid(True)
        plt.draw()
        return n, bins, patches

    # def set_stopping_power(self, stopping_file):
    #     self.sim_obj.stopping_power_function = read_data(stopping_file)
    #     self.sim_obj.energy_max_limit = self.sim_obj.stopping_power_function[-1, 0]

    def set_particle_spectrum(self, file_name):
        """
        Setting up the particle specs according to a spectrum

        :param string file_name: path of the file containing the spectrum
        """
        self.sim_obj.spectrum = read_data(file_name)  # nuc/m2*s*sr*MeV

        ccd_area = self.ccd.ver_dimension * self.ccd.hor_dimension * 1.0e-8     # cm2

        self.sim_obj.spectrum[:, 1] *= 4 * math.pi * 1.0e-4 * ccd_area     # nuc/s*MeV

        self.sim_obj.spectrum_function = interpolate_data(self.sim_obj.spectrum)

        lin_energy_range = np.arange(np.min(self.sim_obj.spectrum[:, 0]), np.max(self.sim_obj.spectrum[:, 0]), 0.01)
        flux_dist = self.sim_obj.spectrum_function(lin_energy_range)

        # plt.figure()
        # plt.loglog(lin_energy_range, flux_dist)
        # plt.draw()

        cum_sum = np.cumsum(flux_dist)
        cum_sum /= np.max(cum_sum)
        self.sim_obj.CDF = (lin_energy_range, cum_sum)

        # plt.figure()
        # plt.semilogx(lin_energy_range, cum_sum)
        # plt.draw()

        # plt.show()

    def set_let_distribution(self, data_filename):

        let_histo = read_data(data_filename)    # counts in function of keV

        ############
        # WE NEED THE DATA PER UNIT LENGTH (keV/um) BUT DO NOT DO THIS !
        ##### data_det_thickness = 100    #um
        ##### let_histo[:, 1] /= data_det_thickness   # keV/um
        ###########

        self.sim_obj.let_cdf = np.stack((let_histo[:, 1], let_histo[:, 2]), axis=1)
        cum_sum = np.cumsum(self.sim_obj.let_cdf[:, 1])
        # cum_sum = np.cumsum(let_dist_interpol)
        cum_sum /= np.max(cum_sum)
        self.sim_obj.let_cdf = np.stack((self.sim_obj.let_cdf[:, 0], cum_sum), axis=1)
        # self.sim_obj.let_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

        plt.figure()
        plt.plot(let_histo[:, 1], let_histo[:, 2], '.')
        plt.draw()

        plt.figure()
        plt.plot(self.sim_obj.let_cdf[:, 0], self.sim_obj.let_cdf[:, 1], '.')
        plt.draw()
        # plt.show()