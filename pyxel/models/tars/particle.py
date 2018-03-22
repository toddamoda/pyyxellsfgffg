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

"""TBW."""

import math
import numpy as np
from pyxel.models.tars.util import sampling_distribution
from pyxel.detectors.detector import Detector


class Particle:
    """Particle class define a particle together with its characteristics."""

    def __init__(self,
                 detector: Detector,
                 particle_type='proton',
                 input_energy='random', spectrum_cdf=None,
                 starting_pos_ver='random', starting_pos_hor='random', starting_pos_z='random',
                 input_alpha='random', input_beta='random') -> None:
        """Creation of a particle according to some parameters.

        :param detector: Detector in which the particle is going to interact
        :param float or 'random' input_energy: initial energy of the incident particle
        :param float or 'random' input_alpha: alpha incident angle of the particle in the ccd
        :param float or 'random' input_beta: beta incident angle of the particle in the ccd
        """
        self.detector = detector
        geo = self.detector.geometry

        starting_position_vertical = None
        starting_position_horizontal = None
        starting_position_z = None

        if starting_pos_ver == 'random':
            starting_position_vertical = geo.vert_dimension * np.random.random()
        elif isinstance(starting_pos_ver, int) or isinstance(starting_pos_ver, float):
            starting_position_vertical = starting_pos_ver
        if starting_pos_hor == 'random':
            starting_position_horizontal = geo.horz_dimension * np.random.random()
        elif isinstance(starting_pos_hor, int) or isinstance(starting_pos_hor, float):
            starting_position_horizontal = starting_pos_hor

        if starting_pos_z == 'random':
            starting_position_z = geo.total_thickness * np.random.random()
        elif isinstance(starting_pos_z, int) or isinstance(starting_pos_z, float):
            starting_position_z = starting_pos_z

        self.starting_position = np.array([starting_position_vertical,
                                           starting_position_horizontal,
                                           starting_position_z])
        self.position = np.copy(self.starting_position)
        self.trajectory = np.copy(self.starting_position)

        if input_alpha == 'random' and starting_pos_z == 0.:
            alpha = math.pi * np.random.random()
        elif input_alpha == 'random' and starting_pos_z != 0.:
            alpha = 2 * math.pi * np.random.random()
        else:
            alpha = input_alpha  # between 0 and pi
        if input_beta == 'random':
            beta = 2. * math.pi * np.random.random()
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

    def track_length(self):
        """TBW.

        :return:
        """
        geo = self.detector.geometry

        norm_vectors = [np.array([0., 0., -1.]),    # top plane (usually particle enters vol. via this)
                        np.array([0., 0., 1.]),     # bottom plane (usually particle leaves vol. via this)
                        np.array([0., 1., 0.]),
                        np.array([-1., 0., 0.]),
                        np.array([0., -1., 0.]),
                        np.array([1., 0., 0.])]

        points = [np.array([0., 0., 0.]),                        # top plane (usually particle enters vol. via this)
                  np.array([0., 0., -1 * geo.total_thickness]),  # bottom plane (usually particle leaves vol. via this)
                  np.array([0., 0., 0.]),
                  np.array([geo.vert_dimension, 0., 0.]),
                  np.array([geo.vert_dimension, geo.horz_dimension, 0.]),
                  np.array([0., geo.horz_dimension, 0.])]

        track_length = np.inf
        intersect_points = np.zeros((6, 3))
        for i in range(6):
            intersect_points[i, :] = self.find_intersection(norm_vectors[i], points[i])
            track_length_new = np.linalg.norm(intersect_points[i, :] - self.starting_position)
            if track_length_new < track_length and track_length_new != 0.:
                track_length = track_length_new

        return track_length

    def find_intersection(self, n, p0):
        """TBW.

        https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
        :param n: normal vector of the plane
        :param p0: point of the plane
        :return:
        """
        ls = self.starting_position
        lv = np.array([self.dir_ver,
                       self.dir_hor,
                       self.dir_z])

        if np.dot(lv, n) == 0:   # No intersection of track and detector plane
            return None
        else:
            d = np.dot((p0 - ls), n) / np.dot(lv, n)
            p = d * lv + ls
            return p
