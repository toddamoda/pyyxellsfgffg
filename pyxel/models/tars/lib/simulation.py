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
# Fully documented
# Fully Commented

from os import path
from math import sqrt
import numpy as np
from scipy.special import erf
# from pyxel.models.tars.tars import TARS_DIR
from pyxel.models.tars.lib.particle import Particle
from pyxel.models.tars.lib.util import sampling_distribution, read_data
# import matplotlib.pyplot as plt


class Simulation:
    """
    Main class of the program, Simulation contain all the methods to set and run a simulation
    """

    def __init__(self, ccd_sim):
        """
        Initialisation of the simulation

        :param CCD ccd_sim: CCD object(from CCD library) containing all the simulated CCD specs
        """

        self.ccd = ccd_sim

        self.spectrum_cdf = None
        self.let_cdf = np.zeros((1, 2))

        self.processing_time = 0

        self.event_counter = 0
        self.total_charge_array = np.zeros((self.ccd.row, self.ccd.col), int)
        self.ver_limit, self.hor_limit = self.total_charge_array.shape

        #   Here is an image of all the last simulated CRs events on the CCD
        self.pcmap_last = np.zeros((self.ccd.row, self.ccd.col))

        self.particle_type = None
        self.initial_energy = None
        self.position_ver = None
        self.position_hor = None
        self.position_z = None
        self.angle_alpha = None
        self.angle_beta = None
        self.step_length = None
        self.energy_cut = 1.0e-5        # MeV
        
        self.edep_per_step = []
        self.total_edep_per_particle = []

    def parameters(self, part_type, init_energy, pos_ver, pos_hor, pos_z, alpha, beta, step_length):
        self.particle_type = part_type
        self.initial_energy = init_energy
        self.position_ver = pos_ver
        self.position_hor = pos_hor
        self.position_z = pos_z
        self.angle_alpha = alpha
        self.angle_beta = beta
        self.step_length = step_length

################# EXPERIMENTAL - NOT FINSHED YET ###############################
    def set_let_distribution(self):
        '''
        Read/generate a Linear Energy Transport distribution from Geant4 data
        for each new particle based on its initial energy (from input spectrum)
        and track length inside the detector
        :return:
        '''


        TARS_DIR = path.dirname(path.abspath(__file__))
        # particle_let_file = TARS_DIR + '../data/inputs/let_proton_12GeV_100um_geant4.ascii'
        particle_let_file = TARS_DIR + '/../data/inputs/let_proton_1GeV_100um_geant4_HighResHist.ascii'

        let_histo = read_data(particle_let_file)  # counts in function of keV

        ############
        # Todo: THE DATA NEED TO BE EXTRACTED FROM G4: DEPOSITED ENERGY PER UNIT LENGTH (keV/um)
        # THIS 2 LINE IS TEMPORARY, DO NOT USE THIS!
        data_det_thickness = 100.0    #um
        let_histo[:, 1] /= data_det_thickness   # keV/um
        ###########

        self.let_cdf = np.stack((let_histo[:, 1], let_histo[:, 2]), axis=1)
        cum_sum = np.cumsum(self.let_cdf[:, 1])
        # cum_sum = np.cumsum(let_dist_interpol)
        cum_sum /= np.max(cum_sum)
        self.let_cdf = np.stack((self.let_cdf[:, 0], cum_sum), axis=1)
        # self.sim_obj.let_cdf = np.stack((lin_energy_range, cum_sum), axis=1)

        # plt.figure()
        # plt.plot(let_histo[:, 1], let_histo[:, 2], '.')
        # plt.draw()
        #
        # plt.figure()
        # plt.plot(self.sim_obj.let_cdf[:, 0], self.sim_obj.let_cdf[:, 1], '.')
        # plt.draw()
        # plt.show()
################# EXPERIMENTAL - NOT FINSHED YET ###############################

    def event_generation(self):
        """
        Generation of an event on the CCD due to an incident particle taken according to the simulation configuration
        file

        :return:
        """

        # charge_cluster = np.zeros((1, 4))

        self.pcmap_last[:, :] = 0

        track_left = False

        p = Particle(self.ccd,
                     self.particle_type,
                     self.initial_energy, self.spectrum_cdf,
                     self.position_ver, self.position_hor, self.position_z,
                     self.angle_alpha, self.angle_beta)

        self.set_let_distribution()

        # main loop : electrons generation and collection at each step while the particle is in the CCD and
        # have enough energy to spread

        # p.position is inside CCD, ionization can not happen in this first step
        p.position[0] += p.dir_ver * self.step_length * 0.1
        p.position[1] += p.dir_hor * self.step_length * 0.1
        p.position[2] += p.dir_z * self.step_length * 0.1

        while True:
            # check if p is still inside CCD and have enough energy:
            if p.position[0] < 0.0 or p.position[0] > self.ccd.ver_dimension:
                break
            if p.position[1] < 0.0 or p.position[1] > self.ccd.hor_dimension:
                break
            if p.position[2] < -1 * self.ccd.total_thickness or p.position[2] > 0.0:
                break
            if p.energy <= self.energy_cut:
                break

            track_left = True

            # IONIZATION
            self._ionization_(p)

            # DIFFUSION AND COLLECTING ELECTRONS IN PIXELS -> make a Pyxel charge collection model from this
            # sig = self._electron_diffusion_(p)
            # self._electron_collection_(p, sig, sig)
            # self._electron_collection_(p, 1.0, 1.0)         # JUST FOR TESTING

            # UPDATE POSITION OF IONIZING PARTICLES
            p.position[0] += p.dir_ver * self.step_length
            p.position[1] += p.dir_hor * self.step_length
            p.position[2] += p.dir_z * self.step_length

            # save particle trajectory
            p.trajectory = np.vstack((p.trajectory, p.position))
            # (should be changed to np.stack)

            # charge_cluster = np.stack((p.position, p.electrons), axis=??) # NOT GOOOD  YET   # horizontal

            # p.charge_clusters = np.stack((p.charge_clusters, charge_cluster), axis=1)  # vertical

        # END of loop

        if track_left:
            # plot particle trajectory in 2d
            # p.plot_trajectory_xy()
            # p.plot_trajectory_xz()
            # plt.show()

            self.total_edep_per_particle.append(p.total_edep)  # keV

            self.pcmap_last = np.rint(self.pcmap_last).astype(int)

            self.total_charge_array += self.pcmap_last
            self.event_counter += 1

        return p.total_edep

    def _ionization_(self, particle):

        # particle.energy is in MeV !
        # particle.deposited_energy is in keV !
        particle.deposited_energy = sampling_distribution(self.let_cdf) * self.step_length  # keV

        if particle.deposited_energy >= particle.energy * 1e3:
            particle.deposited_energy = particle.energy * 1e3

        particle.electrons = int(particle.deposited_energy * 1e3 / self.ccd.material_ionization_energy)     # eV/eV = 1
        particle.deposited_energy = particle.electrons * self.ccd.material_ionization_energy * 1e-3         # keV
        # else:
        particle.energy -= particle.deposited_energy * 1e-3

        self.edep_per_step.append(particle.deposited_energy)    # keV
        particle.total_edep += particle.deposited_energy        # keV

    # DIFFUSION -> make a Pyxel charge collection model from this
    def _electron_diffusion_(self, particle):
        """
        spread the particle into the material and compute the density and size of the electronic cloud generated
        at each step

        :param Particle particle: particle
        :return: float sigma : diameter of the electronic cloud at the generation point (um)
        """
        #     specify na in /m3 for evaluation of con in SI units
        na = 1e19
        #     specify diffusion length in um (field free region)
        l1 = 1000.
        #     depletion/field free boundary parameter
        bound = 2.
        k_boltzmann = 1.38e-23
        eps_rel = 11.8
        eps_null = 8.85e-12
        q_elec = 1.6e-19

        #     constant includes factor of 1.d6 for conversion of m to um
        self.con = 1e6 * sqrt((2. * k_boltzmann * self.ccd.temperature * eps_rel * eps_null) / (na * q_elec ** 2))
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!! constans not equal with one in ppt
        #     electron velocity saturation parameter
        self.sat = q_elec * na * self.ccd.depletion_zone / eps_rel / eps_null / self.ccd.temperature ** 1.55 / 1.01e8
        #     spreading across entire depletion region
        self.cfr = self.con * sqrt(self.sat + bound)

        #     calculate initial 1 sigma cloud size in um (many refs)
        ci = 0.0044 * ((particle.electrons * self.ccd.material_ionization_energy / 1000.) ** 1.75)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!! constans not equal with one in ppt

        sig = 0

        # if 0.0 <= abs(particle.position[2]) < self.ccd.depletion_zone:
        #
        #     cf = self.con * sqrt(self.sat * abs(particle.position[2]) / self.ccd.depletion_zone + log(self.ccd.depletion_zone / (self.ccd.depletion_zone - abs(particle.position[2]))))
        #
        #     if cf > self.cfr:
        #         cf = self.cfr
        #
        #     sig = sqrt(ci ** 2 + cf ** 2)  # WTF ???????
        #     # hh = 1.0
        #
        # elif self.ccd.depletion_zone <= abs(particle.position[2]) < self.ccd.depletion_zone + self.ccd.field_free_zone:
        #
        #     d = abs(particle.position[2]) - self.ccd.depletion_zone
        #
        #     # hh = (exp(self.ccd.field_free_zone / l1 - d / l1)
        #     #       + exp(d / l1 - self.ccd.field_free_zone / l1)) / (
        #     #     exp(self.ccd.field_free_zone / l1)
        #     #     + exp(-self.ccd.field_free_zone / l1))
        #
        #     cff = self.ccd.field_free_zone / 1.0 * sqrt(1 - ((self.ccd.field_free_zone - d) / self.ccd.field_free_zone) ** 2)
        #
        #     sig = sqrt(ci ** 2 + self.cfr ** 2 + cff ** 2)
        #
        # elif self.ccd.depletion_zone + self.ccd.field_free_zone <= abs(particle.position[2]) <= self.ccd.depletion_zone + self.ccd.field_free_zone + self.ccd.sub_thickness:
        #
        #     d = abs(particle.position[2]) - self.ccd.field_free_zone - self.ccd.depletion_zone
        #
        #     cff = self.ccd.field_free_zone / 1.0
        #
        #     # hhsub = sinh((self.ccd.sub_thickness - d) / 10.) / sinh(self.ccd.sub_thickness / 10.)
        #     # hhff = 2. / (exp(self.ccd.field_free_zone / l1) + exp(-self.ccd.field_free_zone / l1))
        #     # hh = hhsub * hhff
        #
        #     cfsub = 0.5 * self.ccd.sub_thickness * sqrt(1 - ((self.ccd.sub_thickness - d) / self.ccd.sub_thickness) ** 2)
        #
        #     sig = sqrt(ci ** 2 + self.cfr ** 2 + cfsub ** 2 + cff ** 2)

        # else:
        #     hh = 0

        # particle.electrons *= hh  # WTF????

        return sig

    # ELECTRON COLLECTION -> make a Pyxel charge collection model from this
    def _electron_collection_(self, particle, sig_ac, sig_al):
        """
        Compute the charge collection function to determine the number of electron collected by each pixel based on the
        generated electronic cloud shape

        :param Particle particle: particle responsible of the electronic cloud
        :param float sig_ac: diameter of the resulting electronic cloud in the AC (across scan, vertical) dimension
        :param float sig_al: diameter of the resulting electronic cloud in the AL (along scan, horizontal) dimension
        """

        px = []
        py = []

        dx = particle.position[0] - self.ccd.pix_ver_size \
                                               * int(particle.position[0] / self.ccd.pix_ver_size)
        dy = particle.position[1] - self.ccd.pix_hor_size \
                                               * int(particle.position[1] / self.ccd.pix_hor_size)

        try:
            int(4 * sig_ac / self.ccd.pix_ver_size)         # WTF?
        except ValueError:
            print(sig_ac, particle.electrons)

        x_steps = int(4 * sig_ac / self.ccd.pix_ver_size)
        if x_steps > 49:        # WHY????
            x_steps = 49
        if x_steps < 1:
            x_steps = 1

        y_steps = int(4 * sig_al / self.ccd.pix_hor_size)
        if y_steps > 49:
            y_steps = 49
        if y_steps < 1:
            y_steps = 1

        for xi in np.arange(-(x_steps * self.ccd.pix_ver_size + dx),
                            ((x_steps + 1) * self.ccd.pix_ver_size - dx),
                            self.ccd.pix_ver_size):

            if sig_ac != 0:
                case1 = (xi + self.ccd.pix_ver_size) / 1.41 / sig_ac
                case2 = xi / 1.41 / sig_ac
            else:
                case1 = 0
                case2 = 0

            px.append((erf(case1) - erf(case2)) / 2)

        for yi in np.arange(-(y_steps * self.ccd.pix_hor_size + dy),
                            ((y_steps + 1) * self.ccd.pix_hor_size - dy),
                            self.ccd.pix_hor_size):

            if sig_al != 0:
                case1 = (yi + self.ccd.pix_hor_size) / 1.41 / sig_al
                case2 = yi / 1.41 / sig_al
            else:
                case1 = 0
                case2 = 0

            py.append((erf(case1) - erf(case2)) / 2)

        cx = 0

        for ix in range(int(particle.position[0] / self.ccd.pix_ver_size) - x_steps,
                        int(particle.position[0] / self.ccd.pix_ver_size) + x_steps + 1, 1):

            cy = 0

            for iy in range(int(particle.position[1] / self.ccd.pix_hor_size) - y_steps,
                            int(particle.position[1] / self.ccd.pix_hor_size) + y_steps + 1, 1):

                if 0 <= ix < self.ccd.row and 0 <= iy < self.ccd.col:
                    self.pcmap_last[ix, iy] += px[cx] * py[cy] * particle.electrons

                cy += 1

            cx += 1
