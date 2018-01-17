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
# Not fully commented

import math
import random
import numpy as np
# import matplotlib.pyplot as plt
from pyxel.models.tars.lib.util import sampling_distribution


class Particle:
    """
     particle class define a particle together with its characteristics
    """

    def __init__(self,
                 ccd=None,
                 particle_type='proton',
                 input_energy='random', spectrum_cdf=None,
                 starting_pos_ver='random', starting_pos_hor='random', starting_pos_z='random',
                 input_alpha='random', input_beta='random'):
        """
        Creation of a particle according to some parameters

        :param ccd: CCD in which the particle is going to interact
        :param float or 'random' input_energy: initial energy of the incident particle
        :param  float or 'random' input_alpha: alpha incident angle of the particle in the ccd
        :param float or 'random' input_beta: beta incident angle of the particle in the ccd
        """

        self.ccd = ccd

        # self.charge_clusters = np.zeros((1, 4))

        starting_position_vertical = None
        starting_position_horizontal = None
        starting_position_z = None

        if starting_pos_ver == 'random':
            starting_position_vertical = self.ccd.vert_dimension * random.random()
        elif isinstance(starting_pos_ver, int) or isinstance(starting_pos_ver, float):
            starting_position_vertical = starting_pos_ver
        if starting_pos_hor == 'random':
            starting_position_horizontal = self.ccd.horz_dimension * random.random()
        elif isinstance(starting_pos_hor, int) or isinstance(starting_pos_hor, float):
            starting_position_horizontal = starting_pos_hor

        if starting_pos_z == 'random':
            starting_position_z = self.ccd.total_thickness * random.random()
        elif isinstance(starting_pos_z, int) or isinstance(starting_pos_z, float):
            starting_position_z = starting_pos_z

        self.starting_position = np.array([starting_position_vertical,
                                           starting_position_horizontal,
                                           starting_position_z])
        self.position = np.copy(self.starting_position)
        self.trajectory = np.copy(self.starting_position)

        if input_alpha == 'random' and starting_pos_z == 0.:
            alpha = math.pi * random.random()
        elif input_alpha == 'random' and starting_pos_z != 0.:
            alpha = 2 * math.pi * random.random()
        else:
            alpha = input_alpha  # between 0 and pi

        if input_beta == 'random':
            beta = 2. * math.pi * random.random()
        else:
            beta = input_beta
        self.angle = np.array([alpha, beta])

        self.dir_z = -1 * math.sin(alpha)
        self.dir_ver = math.cos(alpha) * math.cos(beta)
        self.dir_hor = math.cos(alpha) * math.sin(beta)

        if input_energy == 'random':
            self.energy = sampling_distribution(spectrum_cdf)
        elif isinstance(input_energy, int) or isinstance(input_energy, float):
            self.energy = input_energy
        else:
            raise ValueError('Given particle energy could not be read')

        self.deposited_energy = 0
        self.electrons = 0
        self.total_edep = 0

        self.particle_type = particle_type
        ionizing_particles = ['proton', 'ion', 'alpha', 'beta', 'electron']
        non_ionizing_particles = ['gamma', 'x-ray', 'photon']

        if self.particle_type in ionizing_particles:
            # call direct ionization func when needed - already implemented in simulation
            pass

        elif self.particle_type in non_ionizing_particles:
            # call NON-direct ionization func when needed - need to be implemented
            raise NotImplementedError('Given particle type simulation is not yet implemented')

        else:
            raise ValueError('Given particle type can not be simulated')

    # def plot_trajectory_xy(self):
    #     plt.figure()
    #     # self.trajectory[:, 0] - VERTICAL COORDINATE
    #     # self.trajectory[:, 1] - HORIZONTAL COORDINATE
    #     plt.plot(self.trajectory[:, 1], self.trajectory[:, 0], '.')
    #     plt.xlabel('horizontal ($\mu$m)')
    #     plt.ylabel('vertical ($\mu$m)')
    #     plt.title('p trajectory in CCD')
    #     plt.axis([0, self.ccd.horz_dimension, 0, self.ccd.vert_dimension])
    #     plt.grid(True)
    #     plt.draw()
    #
    # def plot_trajectory_xz(self):
    #     plt.figure()
    #     # self.trajectory[:, 2] - Z COORDINATE
    #     # self.trajectory[:, 1] - HORIZONTAL COORDINATE
    #     plt.plot(self.trajectory[:, 1], self.trajectory[:, 2], '.')
    #     plt.xlabel('horizontal ($\mu$m)')
    #     plt.ylabel('z ($\mu$m)')
    #     plt.title('p trajectory in CCD')
    #     plt.axis([0, self.ccd.horz_dimension, -1*self.ccd.total_thickness, 0])
    #     plt.grid(True)
    #     plt.draw()