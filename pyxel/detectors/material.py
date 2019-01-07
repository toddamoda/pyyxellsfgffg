"""Geometry class for detector."""
import pyxel as pyx

# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg     # TODO put these global constants to a data file


@pyx.detector_class
class Material:
    """TBW."""

    # TODO create func for compound materials
    # def set_material(self, material):
    #     """Set material properties.
    #
    #     :param material:
    #     """
    #     # TODO put these constants to a data file
    #     if material == 'silicon' or 'Si' or 'si':
    #         self.material_density = 2.328                 # (g/cm3)
    #         self.ionization_energy = 3.6                  # (eV)
    #         self.band_gap = 1.12                          # (eV)
    #         self.e_effective_mass = 0.5 * M_ELECTRON      # (kg)
    #
    #     else:
    #         raise NotImplementedError('Given material has not implemented yet')

    # def __attrs_post_init__(self):
    #     """TBW."""
    #     if self.material:
    #         self.set_material(self.material)

    n_acceptor = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1000.)],
        metadata={'units': 'cm-3'}
    )
    n_donor = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1000.)],
        metadata={'units': 'cm-3'}
    )
    material = pyx.attribute(
        type=str,
        default='silicon',
        validator=[pyx.validate_type(str),
                   pyx.validate_choices(['silicon', 'hxrg'])],
        # on_set=set_material,
    )
    material_density = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=2.328,                      # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10000.)],
        metadata={'units': 'g/cm3'}
    )
    ionization_energy = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=3.6,                        # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        metadata={'units': 'eV'}
    )
    band_gap = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=1.12,                       # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        metadata={'units': 'eV'}
    )
    e_effective_mass = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=0.5 * M_ELECTRON,           # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.e-10)],
        metadata={'units': 'kg'}
    )
