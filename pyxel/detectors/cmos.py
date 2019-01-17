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
                 photons: Photon = None,
                 charges: Charge = None,
                 pixels: Pixel = None,
                 signal: Signal = None,
                 image: Image = None) -> None:
        """TBW.

        :param geometry:
        :param material:
        :param environment:
        :param characteristics:
        """
        super().__init__(geometry=geometry,
                         material=material,
                         environment=environment,
                         characteristics=characteristics,
                         photons=photons,
                         charges=charges,
                         pixels=pixels,
                         signal=signal,
                         image=image)
