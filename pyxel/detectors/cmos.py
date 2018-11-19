#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CMOS detector modeling class."""

from pyxel.detectors.detector import Detector
from pyxel.detectors.cmos_geometry import CMOSGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.cmos_characteristics import CMOSCharacteristics
from pyxel.physics.charge import Charge  # noqa: F401
from pyxel.physics.photon import Photon  # noqa: F401
from pyxel.physics.pixel import Pixel    # noqa: F401
from pyxel.physics.signal import Signal  # noqa: F401
from pyxel.physics.image import Image    # noqa: F401


class CMOS(Detector):
    """TBW."""

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

    # def copy(self):
    #     """TBW."""
    #     cpy = super().copy()
    #     kwargs = {
    #         'geometry': cpy.geometry,
    #         'material': cpy.material,
    #         'environment': cpy.environment,
    #         'characteristics': cpy.characteristics,
    #     }
    #     return CMOS(**kwargs)
