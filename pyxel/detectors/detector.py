"""Detector class."""
from math import sqrt
import collections
import typing as t  # noqa: F401
import numpy as np

# from astropy import units as u
from pyxel.detectors.geometry import Geometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.characteristics import Characteristics
from pyxel.data_structure.charge import Charge                          # noqa: F401
from pyxel.data_structure.photon import Photon                          # noqa: F401
from pyxel.data_structure.pixel import Pixel                            # noqa: F401
from pyxel.data_structure.signal import Signal                          # noqa: F401
from pyxel.data_structure.image import Image                            # noqa: F401
from pyxel.detectors.cmos_geometry import CMOSGeometry                  # noqa: F401
from pyxel.detectors.ccd_geometry import CCDGeometry                    # noqa: F401
from pyxel.detectors.cmos_characteristics import CMOSCharacteristics    # noqa: F401
from pyxel.detectors.ccd_characteristics import CCDCharacteristics      # noqa: F401


class Detector:
    """The detector class."""

    def __init__(self,
                 geometry: Geometry,
                 material: Material,
                 environment: Environment,
                 characteristics: Characteristics,
                 photon: Photon = None,
                 charge: Charge = None,
                 pixel: Pixel = None,
                 signal: Signal = None,
                 image: Image = None) -> None:
        """TBW.

        :param geometry:
        :param material:
        :param environment:
        :param characteristics:
        :param photon:
        :param charge:
        :param pixel:
        :param signal:
        :param image:
        """
        self._geometry = geometry                   # type: Geometry
        self._characteristics = characteristics     # type: Characteristics
        self.material = material                    # type: Material
        self.environment = environment              # type: Environment
        self.header = collections.OrderedDict()     # type: t.Dict[str, object]

        if photon:
            self.photon = photon
        else:
            self.photon = Photon(self.geometry)        # type: Photon
        if charge:
            self.charge = charge
        else:
            self.charge = Charge()                     # type: Charge
        if pixel:
            self.pixel = pixel
        else:
            self.pixel = Pixel(self.geometry)          # type: Pixel
        if signal:
            self.signal = signal
        else:
            self.signal = Signal(self.geometry)         # type: Signal
        if image:
            self.image = image
        else:
            self.image = Image(self.geometry)           # type: Image

        self.input_image = None
        self._output_dir = None                         # type: t.Optional[str]

        self.start_time = 0.                            # type: float
        self.end_time = 0.                              # type: float
        self.steps = 0                                  # type: int
        self.time_step = 0.                             # type: float
        self._time = 0.                                  # type: float
        self._all_time_steps = None

        self._dynamic = False                           # type: bool
        self._non_destructive = False                   # type: bool
        self.read_out = True                            # type: bool

    # def __getstate__(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     return {
    #         'geometry': self.geometry,
    #         'material': self.material,
    #         'environment': self.environment,
    #         'characteristics': self.characteristics,
    #         'photon': self.photon,
    #         'charge': self.charge,
    #         'pixel': self.pixel,
    #         'signal': self.signal,
    #         'image': self.image,
    #         'input_image': self.input_image,
    #         '_output_dir': self._output_dir
    #     }

    def initialize(self, reset_all=True):
        """TBW."""
        self.photon = Photon(self.geometry)             # type: Photon
        if reset_all:
            self.charge = Charge()                      # type: Charge
            self.pixel = Pixel(self.geometry)           # type: Pixel
            self.signal = Signal(self.geometry)         # type: Signal
            self.image = Image(self.geometry)           # type: Image

    def set_output_dir(self, path: str):
        """Set output directory path."""
        self._output_dir = path

    @property
    def output_dir(self):
        """Output directory path."""
        return self._output_dir

    def set_dynamic(self, time_step: float, steps: int, ndreadout: bool = False):
        """Switch on dynamic (time dependent) mode."""
        self._dynamic = True                            # type: bool
        self.time_step = time_step                      # type: float
        self.steps = steps                              # type: int
        self._non_destructive = ndreadout               # type: bool
        self.end_time = self.time_step * self.steps     # type: float
        self._all_time_steps = np.nditer(np.round(np.linspace(self.time_step, self.end_time,
                                                              self.steps, endpoint=True), decimals=10))

    @property
    def is_dynamic(self):
        """Return if detector is dynamic (time dependent) or not.

        By default it is not dynamic.
        """
        return self._dynamic

    @property
    def is_non_destructive_readout(self):
        """Return if detector readout mode is destructive or integrating.

        By default it is destructive (non-integrating).
        """
        return self._non_destructive

    @property
    def geometry(self):
        """TBW."""
        if isinstance(self._geometry, CMOSGeometry):
            return t.cast(CMOSGeometry, self._geometry)
        elif isinstance(self._geometry, CCDGeometry):
            return t.cast(CCDGeometry, self._geometry)
        elif isinstance(self._geometry, Geometry):
            return t.cast(Geometry, self._geometry)

    @property
    def characteristics(self):
        """TBW."""
        if isinstance(self._characteristics, CMOSCharacteristics):
            return t.cast(CMOSCharacteristics, self._characteristics)
        elif isinstance(self._characteristics, CCDCharacteristics):
            return t.cast(CCDCharacteristics, self._characteristics)
        elif isinstance(self._characteristics, Characteristics):
            return t.cast(Characteristics, self._characteristics)

    @property
    def e_thermal_velocity(self):
        """TBW.

        :return:
        """
        k_boltzmann = 1.38064852e-23  # J/K
        return sqrt(3 * k_boltzmann * self.environment.temperature / self.material.e_effective_mass)

    @property
    def time(self):     # TODO
        """TBW."""
        return self._time

    def elapse_time(self):
        """TBW."""
        try:
            self._time = float(next(self._all_time_steps))
        except StopIteration:
            self._time = None
        return self._time
