#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""
from math import sqrt
import collections
import typing as t  # noqa: F401

# from astropy import units as u
from pyxel.detectors.geometry import Geometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.characteristics import Characteristics
from pyxel.data_structure.charge import Charge  # noqa: F401
from pyxel.data_structure.photon import Photon  # noqa: F401
from pyxel.data_structure.pixel import Pixel    # noqa: F401
from pyxel.data_structure.signal import Signal  # noqa: F401
from pyxel.data_structure.image import Image    # noqa: F401
import esapy_config as om


class Detector:
    """The CCD detector class."""

    def __init__(self,
                 geometry: Geometry,
                 material: Material,
                 environment: Environment,
                 characteristics: Characteristics,
                 photons: Photon = None,
                 charges: Charge = None,
                 pixels: Pixel = None,
                 signal: Signal = None,
                 image: Image = None) -> None:
        """TBW.

        :param geometry:
        :param environment:
        :param characteristics:
        """
        self.geometry = geometry                  # type: Geometry
        self.material = material                  # type: Material
        self.environment = environment            # type: Environment
        self.characteristics = characteristics    # type: Characteristics
        self.header = collections.OrderedDict()   # type: t.Dict[str, object]

        self.photons = Photon(self.geometry)        # type: Photon
        self.charges = Charge()                     # type: Charge
        self.pixels = Pixel(self.geometry)          # type: Pixel
        self.signal = Signal(self.geometry)         # type: Signal
        self.image = Image(self.geometry)           # type: Image

        if photons:
            self.photons = photons
        if charges:
            self.charges = charges
        if pixels:
            self.pixels = pixels
        if signal:
            self.signal = signal
        if image:
            self.image = image

        self.input_image = None

        # ##### experimantal! #######
        # self.geometry.create_sensor()
        ############################

    # def reinitialize(self):
    #     """TBW."""
    #     self.photons = Photon()                 # type: Photon
    #     self.charges = Charge()                 # type: Charge
    #     self.pixels = Pixel(self.geometry)      # type: Pixel
    #     self.signal = Signal(self.geometry)     # type: Signal
    #     self.image = Image(self.geometry)       # type: Image

    ######################################
    # These functions are not called at all:
    #
    # def update_header(self):
    #     """TBW."""
    #     for name, obj in self.__getstate__().items():
    #         for att, value in obj.__getstate__().items():
    #             util.update_fits_header(self.header, key=[name, att], value=value)
    #
    # def to_fits(self, output_file):
    #     """Save signal to fits format."""
    #     pass  # TODO
    #
    # def copy(self):
    #     """TBW."""
    #     kwargs = {
    #         'geometry': self.geometry.copy(),
    #         'material': self.material.copy(),
    #         'environment': self.environment.copy(),
    #         'characteristics': self.characteristics.copy(),
    #     }
    #     return Detector(**kwargs)
    #
    # # TODO: create unittests for this method
    # def __eq__(self, obj) -> bool:
    #     """TBW.
    #
    #     :param obj:
    #     :return:
    #     """
    #     assert isinstance(obj, Detector)
    #     return self.__getstate__() == obj.__getstate__()
    ######################################

    def __getstate__(self):
        """TBW.

        :return:
        """
        return {
            'geometry': self.geometry,
            'material': self.material,
            'environment': self.environment,
            'characteristics': self.characteristics,
            'photons': self.photons,
            'charges': self.charges,
            'pixels': self.pixels,
            'signal': self.signal,
            'image': self.image,
            'input_image': self.input_image
        }

    def get_state_json(self):
        """TBW.

        This function is probably used by the GUI.
        """
        return om.get_state_dict(self)

    @property
    def e_thermal_velocity(self):
        """TBW.

        :return:
        """
        k_boltzmann = 1.38064852e-23  # J/K
        return sqrt(3 * k_boltzmann * self.environment.temperature / self.material.e_effective_mass)
