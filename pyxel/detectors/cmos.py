#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
CMOS detector modeling class
"""
from pyxel.detectors.detector import Detector


class CMOS(Detector):
    """TBW."""
    pass

#
# import numpy as np
# from math import sqrt
#
# from pyxel.detectors.cmos_characteristics import CMOSCharacteristics
# from pyxel.detectors.cmos_geometry import CMOSGeometry
# from pyxel.detectors.environment import Environment
# # from pyxel.detectors.optics import Optics
#
#
# class CMOS:
#     """ The CMOS detector class. """
#
#     def __init__(self,
#                  geometry: CMOSGeometry = None,
#                  environment: Environment = None,
#                  characteristics: CMOSCharacteristics = None,
#                  photons: int = None,
#                  image=None,
#                  ) -> None:
#
#         if photons is not None and image is None:
#             self._photon_mean = photons
#             self._image = None
#             # self._photon_mean = photons * u.ph      # unit: photons
#         elif photons is None and image is not None:
#             self._photon_mean = None
#             self._image = image                    # final signal after processing , unit: ADU
#         else:
#             raise ValueError("Only image or photon number can be provided as input")
#
#         # self._photon_number_list = None
#         self._photons = None
#         self._charges = None
#         self._pixels = None
#         self._signal = None     # signal read out directly from CCD
#
#         self.geometry = geometry
#         self.environment = environment
#         self.characteristics = characteristics
#
#     def initialize_detector(self):
#         """
#         Calculate incident photon number per pixel from image or illumination
#         :return:
#         """
#         # TODO: can both image and photons be passed?
#         photon_number_list = []
#
#         if self._image is not None and self._photon_mean is None:
#             self.row, self.col = self._image.shape
#             photon_number_list = self._image / (self.qe * self.eta * self.sv * self.amp * self.a1 * self.a2)
#             photon_number_list = np.rint(photon_number_list).astype(int).flatten()
#
#         if self._photon_mean is not None and self._image is None:
#             # TODO: photon illumination generator to be implemented
#             if isinstance(self._photon_mean, int):
#                 # uniform illumination
#                 photon_number_list = np.ones(self.row * self.col, dtype=int) * self._photon_mean
#
#         photon_energy_list = [0.] * self.row * self.col
#
#         return photon_number_list, photon_energy_list
#
#     @property
#     def e_effective_mass(self):
#         return self.geometry.e_effective_mass   # kg
#
#     @property
#     def e_thermal_velocity(self):
#         k_boltzmann = 1.38064852e-23   # J/K
#         return sqrt(3 * k_boltzmann * self.temperature / self.e_effective_mass)
#
#     @property
#     def row(self):
#         return self.geometry.row
#
#     @row.setter
#     def row(self, new_row):
#         self.geometry.row = new_row
#
#     @property
#     def col(self):
#         return self.geometry.col
#
#     @col.setter
#     def col(self, new_col):
#         self.geometry.col = new_col
#
#     @property
#     def photons(self):
#         return self._photons
#
#     @photons.setter
#     def photons(self, new_photon):
#         self._photons = new_photon
#
#     @property
#     def charges(self):
#         return self._charges
#
#     @charges.setter
#     def charges(self, new_charge):
#         self._charges = new_charge
#
#     @property
#     def pixels(self):
#         return self._pixels
#
#     @pixels.setter
#     def pixels(self, new_pixel):
#         self._pixels = new_pixel
#
#     @property
#     def signal(self):
#         return self._signal
#
#     @signal.setter
#     def signal(self, new_signal: np.ndarray):
#         self._signal = new_signal
#
#     @property
#     def image(self):
#         return self._image
#
#     @property
#     def qe(self):
#         return self.characteristics.qe
#
#     # @qe.setter
#     # def qe(self, newqe):
#     #     self.qe = newqe
#
#     @property
#     def eta(self):
#         return self.characteristics.eta
#
#     # @eta.setter
#     # def eta(self, neweta):
#     #     self.eta = neweta
#
#     @property
#     def sv(self):
#         return self.characteristics.sv
#
#     # @sv.setter
#     # def sv(self, newsv):
#     #     self.sv = newsv
#
#     @property
#     def amp(self):
#         return self.characteristics.amp
#
#     @property
#     def a1(self):
#         return self.characteristics.a1
#
#     # @a1.setter
#     # def a1(self, newa1):
#     #     self.a1 = newa1
#
#     @property
#     def a2(self):
#         return self.characteristics.a2
#
#     @property
#     def fwc(self):
#         return self.characteristics.fwc
#
#     @property
#     def temperature(self):
#         return self.environment.temperature
#
#     @property
#     def depletion_zone(self):
#         return self.geometry.depletion_thickness
#
#     @property
#     def field_free_zone(self):
#         return self.geometry.field_free_thickness
#
#     @property
#     def pix_vert_size(self):
#         return self.geometry.pixel_vert_size
#
#     @property
#     def pix_horz_size(self):
#         return self.geometry.pixel_horz_size
#
#     @property
#     def total_thickness(self):
#         return self.geometry.total_thickness
#
#     @property
#     def vert_dimension(self):
#         return self.geometry.vert_dimension
#
#     @property
#     def horz_dimension(self):
#         return self.geometry.horz_dimension
#
#     @property
#     def material_density(self):
#         return self.geometry.material_density
#
#     @property
#     def material_ionization_energy(self):
#         return self.geometry.material_ionization_energy
#
#     @property
#     def n_output(self):
#         return self.geometry.n_output
#
#     @property
#     def n_row_overhead(self):
#         return self.geometry.n_row_overhead
#
#     @property
#     def n_frame_overhead(self):
#         return self.geometry.n_frame_overhead
#
#     @property
#     def reverse_scan_direction(self):
#         return self.geometry.reverse_scan_direction
#
#     @property
#     def reference_pixel_border_width(self):
#         return self.geometry.reference_pixel_border_width
