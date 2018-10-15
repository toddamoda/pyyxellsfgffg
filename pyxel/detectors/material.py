"""Geometry class for detector."""
import esapy_config as om


# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg     # TODO put these global constants to a data file


@om.attr_class
class Material:
    """TBW."""

    # TODO create func for compound materials
    def set_material(self, material):
        """Set material properties.

        :param material:
        """
        # TODO put these constants to a data file
        if material == 'silicon' or 'Si' or 'si':
            self.material_density = 2.328  # TODO add unit (g/cm3)
            self.ionization_energy = 3.6  # TODO add unit (eV)
            self.band_gap = 1.12  # TODO add unit (eV)
            self.e_effective_mass = 0.5 * M_ELECTRON  # TODO add unit (kg)

        else:
            raise NotImplementedError('Given material has not implemented yet')

    def __attrs_post_init__(self):
        """TBW."""
        if self.material:
            self.set_material(self.material)

    n_acceptor = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'cm-3'}
    )
    n_donor = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'cm-3'}
    )
    material = om.attr_def(
        type=str,
        default='',
        validator=om.validate_choices(['', 'silicon', 'hxrg']),
        on_set=set_material,
    )
    material_density = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        metadata={'units': 'g/cm3'}
    )
    ionization_energy = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        metadata={'units': 'eV'}
    )
    band_gap = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        metadata={'units': 'eV'}
    )
    e_effective_mass = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        metadata={'units': 'kg'}
    )

    def copy(self):
        """TBW."""
        return Material(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        return {
            'n_acceptor': self.n_acceptor,
            'n_donor': self.n_donor,
            'material': self.material
        }

    # TODO: create unittests for this method
    def __eq__(self, obj):
        """TBW.

        :param obj:
        :return:
        """
        assert isinstance(obj, Material)
        return self.__getstate__() == obj.__getstate__()

    # @property
    # def horz_dimension(self):
    #     """TBW."""
    #     return self.pixel_horz_size * self.col
