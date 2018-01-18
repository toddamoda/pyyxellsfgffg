class Geometry:

    def __init__(self, row=0, col=0,
                 depletion_thickness=0.0,
                 field_free_thickness=0.0,
                 substrate_thickness=0.0,
                 pixel_vert_size=0.0,
                 pixel_horz_size=0.0,
                 horz_dimension=1,
                 vert_dimension=1,
                 material_density=1,
                 material_ionization_energy=1,
                 depletion_zone=1,
                 field_free_zone=1,
                 sub_thickness=1,
                 ):
        self.row = row
        self.col = col
        self.depletion_thickness = depletion_thickness          # TODO: add units
        self.field_free_thickness = field_free_thickness
        self.substrate_thickness = substrate_thickness
        self.pixel_vert_size = pixel_vert_size
        self.pixel_horz_size = pixel_horz_size

        # to be implemented
        self.horz_dimension = horz_dimension
        self.vert_dimension = vert_dimension
        self.material_density = material_density
        self.material_ionization_energy = material_ionization_energy
        self.total_thickness = 0.0
        self.depletion_zone = depletion_zone
        self.field_free_zone = field_free_zone
        self.sub_thickness = sub_thickness
