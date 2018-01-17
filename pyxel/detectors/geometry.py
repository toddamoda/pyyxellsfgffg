class Geometry:

    def __init__(self, row=0, col=0,
                 depletion_thickness=0.0,
                 field_free_thickness=0.0,
                 substrate_thickness=0.0,
                 pixel_vert_size=0.0,
                 pixel_horz_size=0.0,
                 ):
        self.row = row
        self.col = col
        self.depletion_thickness = depletion_thickness          # TODO: add units
        self.field_free_thickness = field_free_thickness
        self.substrate_thickness = substrate_thickness
        self.pixel_vert_size = pixel_vert_size
        self.pixel_horz_size = pixel_horz_size

        # to be implemented
        # horz_dimension
        # vert_dimension
        # material_density
        # material_ionization_energy
        # total_thickness
        # depletion_zone
        # field_free_zone
        # sub_thickness

