#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Simple model to generate charges due to dark current process."""
import logging
import numpy as np
# import pyxel
from pyxel.detectors.cmos import CMOS


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_generation', name='photoelectrons')
def darkcurrent_rule07(detector: CMOS):
    """Generate charge from dark current process.

    :param detector: Pyxel Detector object
    TODO: investigate on the knee of rule07 for higher 1/le*T values
    """
    logger = logging.getLogger('pyxel')
    logger.info('')

    pitch = 18  # 18 um pitch
    amp_to_eps = 6.242e18  # conversion factor amperes to electro per second

    # Rule 07 empirical model parameters
    j0 = 8367.000019  # A/cm**2
    c = -1.162972237
    q = 1.602176624e-19  # Elementary charge (Coulomb)
    k = 1.38064852e-23  # Boltzmann constant (m2 kg s-2 K-1)
    amp_to_eps = 6.242e18  # conversion factor amperes to electron per second
    cm2_to_um2 = 1e8

    def le(lambda_cutoff: float):
        """Compute lambda_e.

        :param lambda_cutoff: (int) Cut-off wavelength of the detector
        """
        lambda_scale = 0.200847413  # um
        lambda_threshold = 4.635136423  # um
        pwr = 0.544071282

        if lambda_cutoff < lambda_threshold:
            le = lambda_cutoff / (1-((lambda_scale/lambda_cutoff)-(lambda_scale/lambda_threshold))**pwr)
        else:
            le = lambda_cutoff

        return le

    geo = detector.geometry
    ch = detector.characteristics
    # ph = detector.photon
    temperature = detector.environment.temperature
    cutoff = ch.cutoff
    conversion_factor = amp_to_eps*1./cm2_to_um2

    init_ver_position = np.arange(0.0, geo.row, 1.0) * geo.pixel_vert_size
    init_hor_position = np.arange(0.0, geo.col, 1.0) * geo.pixel_horz_size
    init_ver_position = np.repeat(init_ver_position, geo.col)
    init_hor_position = np.tile(init_hor_position, geo.row)

    # Rule07
    j = j0*np.exp(c*(1.24*q/k)*1./(le(cutoff)*temperature))
    dark = j*conversion_factor*pitch
    # print(dark)
    # The number of charges generated using rule07 empiric law
    charge_number = np.random.poisson(dark, size=(detector.geometry.row,
                                                  detector.geometry.col))

    charge_number = charge_number.flatten()
    where_non_zero = np.where(charge_number > 0.)
    # print(np.shape(where_non_zero))
    charge_number = charge_number[where_non_zero]
    init_ver_position = init_ver_position[where_non_zero]
    init_hor_position = init_hor_position[where_non_zero]
    size = charge_number.size
    init_ver_position += np.random.rand(size) * geo.pixel_vert_size
    init_hor_position += np.random.rand(size) * geo.pixel_horz_size

    detector.charge.add_charge(particle_type='e',
                               particles_per_cluster=charge_number,
                               init_energy=[0.] * size,
                               init_ver_position=init_ver_position,
                               init_hor_position=init_hor_position,
                               init_z_position=[0.] * size,
                               init_ver_velocity=[0.] * size,
                               init_hor_velocity=[0.] * size,
                               init_z_velocity=[0.] * size)
