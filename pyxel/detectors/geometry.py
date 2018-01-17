class Geometry:

    def __init__(self, row=0, col=0,
                 depletion_thickness=0.0,
                 field_free_thickness=0.0,
                 substrate_thickness=0.0,
                 pixel_ver_size=0.0,
                 pixel_hor_size=0.0,
                 ):
        self.row = row
        self.col = col
        self.depletion_thickness = depletion_thickness          # TODO: add units
        self.field_free_thickness = field_free_thickness
        self.substrate_thickness = substrate_thickness
        self.pixel_ver_size = pixel_ver_size
        self.pixel_hor_size = pixel_hor_size
