#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""

from pyxel.detectors.detector import Detector
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.ccd_characteristics import CCDCharacteristics


class CCD(Detector):
    """TBW."""

    def __init__(self,
                 geometry: CCDGeometry,
                 material: Material,
                 environment: Environment,
                 characteristics: CCDCharacteristics) -> None:
        """TBW.

        :param geometry:
        :param material:
        :param environment:
        :param characteristics:
        """
        super().__init__(geometry=geometry,
                         material=material,
                         environment=environment,
                         characteristics=characteristics)

    def copy(self):
        """TBW."""
        cpy = super().copy()
        kwargs = {
            'geometry': cpy.geometry,
            'material': cpy.material,
            'environment': cpy.environment,
            'characteristics': cpy.characteristics,
        }
        return CCD(**kwargs)
