"""
Geometry class for detector
"""


class Geometry:

    def __init__(self, row=0, col=0,
                 depletion_thickness=0.0,
                 field_free_thickness=0.0,
                 total_thickness=0.0,
                 pixel_vert_size=0.0,
                 pixel_horz_size=0.0,
                 material='',
                 n_acceptor=0.0,
                 n_donor=0.0,
                 bias_voltage=0.0,
                 ):
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

        self.material_density = None
        self.material_ionization_energy = None
        self.band_gap = None
        self.horz_dimension = None
        self.vert_dimension = None

        self.calculate_geometry_parameters()
        self.set_material(material)

    def set_material(self, material):
        """
        Set material properties
        :param material:
        :return:
        """

        if material == 'silicon' or 'Si' or 'si':
            self.material_density = 2.328               # TODO add unit (g/cm3)
            self.material_ionization_energy = 3.6       # TODO add unit (eV)
            self.band_gap = 1.12                        # TODO add unit (eV)

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
