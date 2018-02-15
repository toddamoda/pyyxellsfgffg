"""
Geometry class for detector
"""
# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg


class CCDGeometry:

    def __init__(self,
                 row: int = None, col: int = None,
                 depletion_thickness: float = None,
                 field_free_thickness: float = None,
                 total_thickness: float = None,
                 pixel_vert_size: float = None,
                 pixel_horz_size: float = None,
                 material: str = None,
                 n_acceptor: float = None,
                 n_donor: float = None,
                 bias_voltage: float = None) -> None:
        """
        Initialize the geometry
        :param row:
        :param col:
        :param depletion_thickness:
        :param field_free_thickness:
        :param total_thickness:
        :param pixel_vert_size:
        :param pixel_horz_size:
        :param material:
        """
        self.row = row
        self.col = col
        self.total_thickness = total_thickness                  # TODO: add units
        self.depletion_thickness = depletion_thickness          # TODO: calculate this or get from config if defined
        self.field_free_thickness = field_free_thickness        # TODO: calculate this or get from config if defined
        self.pixel_vert_size = pixel_vert_size
        self.pixel_horz_size = pixel_horz_size

        self.n_acceptor = n_acceptor
        self.n_donor = n_donor
        self.bias_voltage = bias_voltage

        self._material = material
        self.material_density = None
        self.material_ionization_energy = None
        self.band_gap = None
        self.e_effective_mass = None
        self.horz_dimension = None
        self.vert_dimension = None

        self.calculate_geometry_parameters()
        self.set_material(material)

    def __getstate__(self):
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
        assert isinstance(obj, CCDGeometry)
        return self.__getstate__() == obj.__getstate__()

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, new_material):
        self._material = new_material
        self.set_material(new_material)

    def set_material(self, material):
        """
        Set material properties
        :param material:
        :return:
        """

        if material == 'silicon' or 'Si' or 'si':
            self.material_density = 2.328                   # TODO add unit (g/cm3)
            self.material_ionization_energy = 3.6           # TODO add unit (eV)
            self.band_gap = 1.12                            # TODO add unit (eV)
            self.e_effective_mass = 0.5 * M_ELECTRON        # TODO add unit (kg)

        else:
            raise NotImplementedError('Given material has not implemented yet')

    def calculate_geometry_parameters(self):
        """
        Calculate and update missing geometry parameters from other provided by the user
        :return:
        """

        self.horz_dimension = self.pixel_horz_size * self.col
        self.vert_dimension = self.pixel_vert_size * self.row

    def calculate_field_free_thickness(self):
        pass

    def calculate_depletion_thickness(self):
        pass
