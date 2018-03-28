#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""
from math import sqrt
from collections import OrderedDict
import typing as t  # noqa: F401
import numpy as np

# from astropy import units as u
from pyxel.detectors.characteristics import Characteristics
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry
from pyxel.physics.charge import Charge  # noqa: F401
from pyxel.physics.photon import Photon  # noqa: F401
from pyxel.physics.pixel import Pixel  # noqa: F401
from pyxel import util
# from pyxel.util import objmod as om
import esapy_config as om
# from pyxel.detectors.optics import Optics


class Detector:
    """The CCD detector class."""

    def __init__(self,
                 geometry: Geometry,
                 environment: Environment,
                 characteristics: Characteristics) -> None:
        """TBW.

        :param geometry:
        :param environment:
        :param characteristics:
        """
        self._photons = None  # type: Photon
        self._charges = None  # type: Charge
        self._pixels = None  # type: Pixel
        self._signal = None     # signal read out directly from CCD

        self.geometry = geometry
        self.environment = environment
        self.characteristics = characteristics
        self.header = OrderedDict()  # type: t.Dict[str, object]

    def update_header(self):
        """TBW."""
        for name, obj in self.__getstate__().items():
            for att, value in obj.__getstate__().items():
                util.update_fits_header(self.header, key=[name, att], value=value)

    def to_fits(self, output_file):
        """Save signal to fits format."""
        pass  # TODO

    def copy(self):
        """TBW."""
        kwargs = {
            'geometry': self.geometry.copy(),
            'environment': self.environment.copy(),
            'characteristics': self.characteristics.copy(),
        }
        return Detector(**kwargs)

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW.

        :return:
        """
        return {
            'geometry': self.geometry,
            'environment': self.environment,
            'characteristics': self.characteristics
        }

    # TODO: create unittests for this method
    def __eq__(self, obj) -> bool:
        """TBW.

        :param obj:
        :return:
        """
        assert isinstance(obj, Detector)
        return self.__getstate__() == obj.__getstate__()

    @property
    def e_effective_mass(self):
        """TBW.

        :return:
        """
        return self.geometry.e_effective_mass   # kg

    @property
    def e_thermal_velocity(self):
        """TBW.

        :return:
        """
        k_boltzmann = 1.38064852e-23   # J/K
        return sqrt(3 * k_boltzmann * self.environment.temperature / self.geometry.e_effective_mass)

    @property
    def photons(self):
        """TBW.

        :return:
        """
        return self._photons

    @photons.setter
    def photons(self, new_photon):
        """TBW.

        :param new_photon:
        """
        self._photons = new_photon

    @property
    def charges(self):
        """TBW.

        :return:
        """
        return self._charges

    @charges.setter
    def charges(self, new_charge):
        """TBW.

        :param new_charge:
        """
        self._charges = new_charge

    @property
    def pixels(self):
        """TBW.

        :return:
        """
        return self._pixels

    @pixels.setter
    def pixels(self, new_pixel):
        """TBW.

        :param new_pixel:
        """
        self._pixels = new_pixel

    @property
    def signal(self):
        """TBW.

        :return:
        """
        return self._signal

    @signal.setter
    def signal(self, new_signal: np.ndarray):
        """TBW.

        :param new_signal:
        """
        self._signal = new_signal

    @property
    def image(self):
        """TBW.

        :return:
        """
        return self._signal
