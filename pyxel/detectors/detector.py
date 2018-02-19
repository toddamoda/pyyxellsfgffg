#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" CCD detector modeling class
"""
from math import sqrt

import numpy as np

# from astropy import units as u
from pyxel.detectors.characteristics import Characteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry
from pyxel.physics.charge import Charge  # noqa: F401
from pyxel.physics.photon import Photon  # noqa: F401
from pyxel.physics.pixel import Pixel  # noqa: F401


# from pyxel.detectors.optics import Optics


class Detector:
    """ The CCD detector class. """

    def __init__(self,
                 geometry: Geometry,
                 environment: Environment,
                 characteristics: Characteristics,
                 photons: int = None,
                 image=None) -> None:

        if photons is not None and image is None:
            self._photon_mean = photons
            self._image = None
            # self._photon_mean = photons * u.ph      # unit: photons
        elif photons is None and image is not None:
            self._photon_mean = None
            self._image = image                    # final signal after processing , unit: ADU
        else:
            raise ValueError("Only image or photon number can be provided as input")

        # self._photon_number_list = None
        self._photons = None  # type: Photon
        self._charges = None  # type: Charge
        self._pixels = None  # type: Pixel
        self._signal = None     # signal read out directly from CCD

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics

    def __getstate__(self):
        return {
            'photons': self._photons,
            'image': self._image,
            'geometry': self.geometry,
            'environment': self.environment,
            'characteristics': self.characteristics
        }

    # TODO: create unittests for this method
    def __eq__(self, obj):
        assert isinstance(obj, Detector)
        return self.__getstate__() == obj.__getstate__()

    def initialize_detector(self):
        """
        Calculate incident photon number per pixel from image or illumination
        :return:
        """
        # TODO: can both image and photons be passed?
        photon_number_list = []
        cht = self.characteristics
        geo = self.geometry

        if self._image is not None and self._photon_mean is None:
            geo.row, geo.col = self._image.shape
            photon_number_list = self._image / (cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2)
            photon_number_list = np.rint(photon_number_list).astype(int).flatten()

        if self._photon_mean is not None and self._image is None:
            # TODO: photon illumination generator to be implemented
            if isinstance(self._photon_mean, int):
                # uniform illumination
                photon_number_list = np.ones(geo.row * geo.col, dtype=int) * self._photon_mean

        photon_energy_list = [0.] * geo.row * geo.col

        return photon_number_list, photon_energy_list

    @property
    def e_effective_mass(self):
        return self.geometry.e_effective_mass   # kg

    @property
    def e_thermal_velocity(self):
        k_boltzmann = 1.38064852e-23   # J/K
        return sqrt(3 * k_boltzmann * self.environment.temperature / self.geometry.e_effective_mass)

    @property
    def photons(self):
        return self._photons

    @photons.setter
    def photons(self, new_photon):
        self._photons = new_photon

    @property
    def charges(self):
        return self._charges

    @charges.setter
    def charges(self, new_charge):
        self._charges = new_charge

    @property
    def pixels(self):
        return self._pixels

    @pixels.setter
    def pixels(self, new_pixel):
        self._pixels = new_pixel

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, new_signal: np.ndarray):
        self._signal = new_signal

    @property
    def image(self):
        return self._image
