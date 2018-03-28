"""TBW."""
import esapy_config as om

from pyxel.detectors.geometry import Geometry


@om.attr_class
class CCDGeometry(Geometry):
    """TBW."""

    def copy(self):
        """TBW."""
        return CCDGeometry(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        states = super().__getstate__()
        ccd_states = {
            # add specific CCD attributes here
        }
        return {**states, **ccd_states}
