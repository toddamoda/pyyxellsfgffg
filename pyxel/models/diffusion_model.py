#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! Charge diffusion and collection model extracted from TARS
"""

import copy
from math import sqrt
import numpy as np
from scipy.special import erf
from pyxel.models.tars.lib.particle import Particle
from pyxel.detectors.ccd import CCDDetector


def diffusion(ccd: CCDDetector,
              variable: float = 1.0) -> CCDDetector:

    new_ccd = copy.deepcopy(ccd)

    diff = Diffusion(new_ccd)

    # Modifying the positions and shapes of charge clusters in list of Charge class instances
    # sigma = diff.electron_diffusion()

    # sigma = 1.0     # temporarily
    # collected_charge_list = diff.electron_collection(sigma, sigma)

    # Overwrite the list of charge clusters in the new_ccd object because Charge attributes have changed
    # new_ccd.charge_list = collected_charge_list

    return new_ccd


class Diffusion:

    def __init__(self, ccd):

        self.ccd = ccd
        self.ccd.charges = ccd.charge_list

    # DIFFUSION -> make a Pyxel charge collection model from this
    def electron_diffusion(self):
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
    def electron_collection(self, sig_ac, sig_al):
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
            int(4 * sig_ac / self.ccd.pix_ver_size)  # WTF?
        except ValueError:
            print(sig_ac, particle.electrons)

        x_steps = int(4 * sig_ac / self.ccd.pix_ver_size)
        if x_steps > 49:  # WHY????
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

        return pcmap_last