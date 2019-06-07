#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CMOS detector modeling class."""

from pyxel.detectors.detector import Detector
from pyxel.detectors.cmos_geometry import CMOSGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.cmos_characteristics import CMOSCharacteristics
from pyxel.data_structure.charge import Charge  # noqa: F401
from pyxel.data_structure.photon import Photon  # noqa: F401
from pyxel.data_structure.pixel import Pixel    # noqa: F401
from pyxel.data_structure.signal import Signal  # noqa: F401
from pyxel.data_structure.image import Image    # noqa: F401


class CMOS(Detector):
    """CMOS-based detector class containing all detector attributes and data."""

    def __init__(self,
                 geometry: CMOSGeometry,
                 material: Material,
                 environment: Environment,
                 characteristics: CMOSCharacteristics,
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
        super().__init__(geometry=geometry,
                         material=material,
                         environment=environment,
                         characteristics=characteristics,
                         photon=photon,
                         charge=charge,
                         pixel=pixel,
                         signal=signal,
                         image=image)

        self.start_time = 0.                        # type: float
        self.end_time = 0.                          # type: float
        self.steps = 0                              # type: int
        self.last_time_step = 0.                    # type: float
        self.time = 0.                              # type: float

        self._dynamic = False                       # type: bool
        self._non_destructive = False               # type: bool

    def set_dynamic(self, start_time: float, end_time: float, steps: int, ndreadout=False):
        """Switch on dynamic (time dependent) mode."""
        self._dynamic = True                        # type: bool
        self.start_time = start_time                # type: float
        self.end_time = end_time                    # type: float
        self.steps = steps                          # type: int
        self._non_destructive = ndreadout           # type: bool

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
