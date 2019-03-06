"""Geometry class for detector."""
import numpy as np
import pyxel as pyx

# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg     # TODO put these global constants to a data file


@pyx.detector_class
class Material:
    """Material attributes of the detector."""

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
    #     """Setting material."""
    #     if self.material:
    #         self.set_material(self.material)

    def load_numpy_array(self, attr=None, path=None):
        """Create Numpy array storing data temporarily."""
        if isinstance(path, str):
            if pyx.check_path(path):
                if path.endswith('.npy'):
                    setattr(self, '_' + attr, np.load(path))

    trap_density = pyx.attribute(
        type=str,
        default=None,
        on_change=load_numpy_array,
        # validator=[(pyx.validate_type(str) or pyx.validate_type(np.ndarray))], <<< this does not work
        doc='Numpy array storing the trap density temporarily'
    )

    n_acceptor = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1000.)],
        metadata={'units': 'cm-3'},
        doc='Density of acceptors in the lattice'
    )
    n_donor = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1000.)],
        metadata={'units': 'cm-3'},
        doc='Density of donors in the lattice'
    )
    material = pyx.attribute(
        type=str,
        default='silicon',
        validator=[pyx.validate_type(str),
                   pyx.validate_choices(['silicon', 'hxrg'])],
        # on_set=set_material,
        doc='Semiconductor material of the detector'
    )
    material_density = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=2.328,                      # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10000.)],
        metadata={'units': 'g/cm3'},
        doc='Material density'
    )
    ionization_energy = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=3.6,                        # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 100.)],
        metadata={'units': 'eV'},
        doc='Mean ionization energy of the semiconductor lattice'
    )
    band_gap = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=1.12,                       # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 10.)],
        metadata={'units': 'eV'},
        doc='Band gap of the semiconductor lattice'
    )
    e_effective_mass = pyx.attribute(       # todo: set automatically depending on the material
        # init=False,
        type=float,
        default=0.5 * M_ELECTRON,           # Silicon
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0., 1.e-10)],
        metadata={'units': 'kg'},
        doc='Electron effective mass in the semiconductor lattice'
    )
