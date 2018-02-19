#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.detector import Detector
from pyxel.detectors.environment import Environment


class CCD(Detector):
    """TBW."""

    def __init__(self,
                 geometry: CCDGeometry,
                 environment: Environment,
                 characteristics: CCDCharacteristics,
                 **kwargs) -> None:
        """TBW.

        :param geometry:
        :param environment:
        :param characteristics:
        :param kwargs:
        """
        super().__init__(geometry=geometry,
                         environment=environment,
                         characteristics=characteristics,
                         **kwargs)
