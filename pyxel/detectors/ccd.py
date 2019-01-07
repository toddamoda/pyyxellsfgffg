#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""

from pyxel.detectors.detector import Detector
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.physics.charge import Charge  # noqa: F401
from pyxel.physics.photon import Photon  # noqa: F401
from pyxel.physics.pixel import Pixel    # noqa: F401
from pyxel.physics.signal import Signal  # noqa: F401
from pyxel.physics.image import Image    # noqa: F401
import typing as t  # noqa: F401


class CCD(Detector):
    """TBW."""

    def __init__(self,
                 geometry: CCDGeometry,
                 material: Material,
                 environment: Environment,
                 characteristics: CCDCharacteristics,
                 charge_injection_profile: t.List = None,
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

        self._charge_injection_profile = None
        if charge_injection_profile:
            self._charge_injection_profile = charge_injection_profile

    @property
    def charge_injection_profile(self):
        """TBW.

        :return:
        """
        return self._charge_injection_profile

    @charge_injection_profile.setter
    def charge_injection_profile(self, new_chg_inj_profile):
        """TBW.

        :param new_chg_inj_profile:
        """
        self._charge_injection_profile = new_chg_inj_profile
