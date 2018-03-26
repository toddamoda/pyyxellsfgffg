"""Geometry class for detector."""
import esapy_config as om


# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg


# class Geometry:
#     """TBW."""
#
#     def __init__(self,
#                  row: int = None, col: int = None,
#                  depletion_thickness: float = None,
#                  field_free_thickness: float = None,
#                  total_thickness: float = None,
#                  pixel_vert_size: float = None,
#                  pixel_horz_size: float = None,
#                  material: str = None,
#                  n_acceptor: float = None,
#                  n_donor: float = None,
#                  bias_voltage: float = None) -> None:
#         """Initialize the geometry.
#
#         :param row:
#         :param col:
#         :param depletion_thickness:
#         :param field_free_thickness:
#         :param total_thickness:
#         :param pixel_vert_size:
#         :param pixel_horz_size:
#         :param material:
#         """
#         self.row = row
#         self.col = col
#         self.total_thickness = total_thickness                  # TODO: add units
#         self.depletion_thickness = depletion_thickness          # TODO: calculate this or get from config if defined
#         self.field_free_thickness = field_free_thickness        # TODO: calculate this or get from config if defined
#         self.pixel_vert_size = pixel_vert_size
#         self.pixel_horz_size = pixel_horz_size
#
#         self.n_acceptor = n_acceptor
#         self.n_donor = n_donor
#         self.bias_voltage = bias_voltage
#
#         self._material = material
#         self.material_density = None
#         self.material_ionization_energy = None
#         self.band_gap = None
#         self.e_effective_mass = None
#
#         self.set_material(material)
#
#     def copy(self):
#         """TBW."""
#         return Geometry(**self.__getstate__())
#
#     def __getstate__(self):
#         """TBW."""
#         return {
#             'row': self.row,
#             'col': self.col,
#             'total_thickness': self.total_thickness,
#             'depletion_thickness': self.depletion_thickness,
#             'field_free_thickness': self.field_free_thickness,
#             'pixel_vert_size': self.pixel_vert_size,
#             'pixel_horz_size': self.pixel_horz_size,
#             'n_acceptor': self.n_acceptor,
#             'n_donor': self.n_donor,
#             'bias_voltage': self.bias_voltage,
#             'material': self.material
#         }
#
#     # TODO: create unittests for this method
#     def __eq__(self, obj):
#         """TBW.
#
#         :param obj:
#         :return:
#         """
#         assert isinstance(obj, Geometry)
#         return self.__getstate__() == obj.__getstate__()
#
#     @property
#     def horz_dimension(self):
#         """TBW."""
#         return self.pixel_horz_size * self.col
#
#     @property
#     def vert_dimension(self):
#         """TBW."""
#         return self.pixel_vert_size * self.row
#
#     @property
#     def material(self):
#         """TBW."""
#         return self._material
#
#     @material.setter
#     def material(self, new_material):
#         """TBW.
#
#         :param new_material:
#         :return:
#         """
#         self._material = new_material
#         self.set_material(new_material)
#
#     def set_material(self, material):
#         """Set material properties.
#
#         :param material:
#         """
#         if material == 'silicon' or 'Si' or 'si':
#             self.material_density = 2.328                   # TODO add unit (g/cm3)
#             self.material_ionization_energy = 3.6           # TODO add unit (eV)
#             self.band_gap = 1.12                            # TODO add unit (eV)
#             self.e_effective_mass = 0.5 * M_ELECTRON        # TODO add unit (kg)
#
#         else:
#             raise NotImplementedError('Given material has not implemented yet')
#
#     def calculate_field_free_thickness(self):
#         """TBW."""
#         pass
#
#     def calculate_depletion_thickness(self):
#         """TBW."""
#         pass


@om.attr_class
class Geometry:
    """TBW."""

    def set_material(self, material):
        """Set material properties.

        :param material:
        """
        if material == 'silicon' or 'Si' or 'si':
            self.material_density = 2.328  # TODO add unit (g/cm3)
            self.material_ionization_energy = 3.6  # TODO add unit (eV)
            self.band_gap = 1.12  # TODO add unit (eV)
            self.e_effective_mass = 0.5 * M_ELECTRON  # TODO add unit (kg)

        else:
            raise NotImplementedError('Given material has not implemented yet')

    row = om.attr_def(
        type=int,
        default=0,
        cast=True,
        validate=om.check_range(0, 10000, 1, False)
    )
    col = om.attr_def(
        type=int,
        default=0,
        cast=True,
        validate=om.check_range(0, 10000, 1, False)
    )
    depletion_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    field_free_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    total_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    pixel_vert_size = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    pixel_horz_size = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    material = om.attr_def(
        type=str,
        default=None,
        validate=om.check_choices(['', 'silicon', 'hxrg']),
        on_set=set_material
    )
    n_acceptor = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='cm-3',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    n_donor = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='cm-3',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    bias_voltage = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='V',
        validate=om.check_range(0.0, 40.0, 0.001, False)
    )
    material_density = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        units='g/cm3',
    )
    material_ionization_energy = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        units='eV',
    )
    band_gap = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        units='eV',
    )
    e_effective_mass = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        units='kg',
    )

    def copy(self):
        """TBW."""
        return Geometry(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        return {
            'row': self.row,
            'col': self.col,
            'total_thickness': self.total_thickness,
            'depletion_thickness': self.depletion_thickness,
            'field_free_thickness': self.field_free_thickness,
            'pixel_vert_size': self.pixel_vert_size,
            'pixel_horz_size': self.pixel_horz_size,
            'n_acceptor': self.n_acceptor,
            'n_donor': self.n_donor,
            'bias_voltage': self.bias_voltage,
            'material': self.material
        }

    # TODO: create unittests for this method
    def __eq__(self, obj):
        """TBW.

        :param obj:
        :return:
        """
        assert isinstance(obj, Geometry)
        return self.__getstate__() == obj.__getstate__()

    @property
    def horz_dimension(self):
        """TBW."""
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self):
        """TBW."""
        return self.pixel_vert_size * self.row

    # @property
    # def material(self):
    #     """TBW."""
    #     return self._material
    #
    # @material.setter
    # def material(self, new_material):
    #     """TBW.
    #
    #     :param new_material:
    #     :return:
    #     """
    #     self._material = new_material
    #     self.set_material(new_material)

    def calculate_field_free_thickness(self):
        """TBW."""
        pass

    def calculate_depletion_thickness(self):
        """TBW."""
        pass
