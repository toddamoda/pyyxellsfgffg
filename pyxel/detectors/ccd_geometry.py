"""TBW."""
from pyxel.detectors.geometry import Geometry
from ..util import config


@config.detector_class
class CCDGeometry(Geometry):
    """Geometrical attributes of a CCD detector."""
