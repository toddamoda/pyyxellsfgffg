#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""CCD detector modeling class."""

from pyxel.detectors.detector import Detector
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.data_structure.charge import Charge  # noqa: F401
from pyxel.data_structure.photon import Photon  # noqa: F401
from pyxel.data_structure.pixel import Pixel    # noqa: F401
from pyxel.data_structure.signal import Signal  # noqa: F401
from pyxel.data_structure.image import Image    # noqa: F401
# import typing as t  # noqa: F401


class CCD(Detector):
    """Charge-Coupled Device class containing all detector attributes and data."""

    def __init__(self,
                 geometry: CCDGeometry,
                 material: Material,
                 environment: Environment,
                 characteristics: CCDCharacteristics,
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

        # self._charge_injection_profile = None
        # if charge_injection_profile:
        #     self._charge_injection_profile = charge_injection_profile

    # @property
    # def charge_injection_profile(self):
    #     """TBW.
    #
    #     :return:
    #     """
    #     return self._charge_injection_profile
    #
    # @charge_injection_profile.setter
    # def charge_injection_profile(self, new_chg_inj_profile):
    #     """TBW.
    #
    #     :param new_chg_inj_profile:
    #     """
    #     self._charge_injection_profile = new_chg_inj_profile
