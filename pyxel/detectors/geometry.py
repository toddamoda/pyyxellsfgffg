"""Geometry class for detector."""
import esapy_config as om

# from esapy_sensor.sensor_ccd import CCDSensorGeometry, CCDFrame
# Universal global constants
M_ELECTRON = 9.10938356e-31    # kg


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

    # def __attrs_post_init__(self):
    #     """TBW."""
    #     if self.material:
    #         self.set_material(self.material)

    row = om.attr_def(
        type=int,
        default=0,
        converter=int,
        validator=om.validate_range(0, 10000, 1, False)
    )
    col = om.attr_def(
        type=int,
        default=0,
        converter=int,
        validator=om.validate_range(0, 10000, 1, False)
    )
    depletion_thickness = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'um'}
    )
    field_free_thickness = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'um'}
    )
    total_thickness = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'um'}
    )
    pixel_vert_size = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'um'}
    )
    pixel_horz_size = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 1000.0, 0.1, False),
        metadata={'units': 'um'}
    )
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
    bias_voltage = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 40.0, 0.001, False),
        metadata={'units': 'V'}
    )
    material = om.attr_def(
        type=str,
        default='silicon',
        validator=om.validate_choices(['', 'silicon', 'hxrg']),
        on_set=set_material
    )
    material_density = om.attr_def(
        init=False,
        type=float,
        default=0.0,
        metadata={'units': 'g/cm3'}
    )
    material_ionization_energy = om.attr_def(
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
    readout_nodes = om.attr_def(
        type=int,
        default=1,
        # cast=True,
        # units='',
        # validate=om.validate_range(1, 4, 1, False)
        validator=om.validate_range(1, 4, 1, False)
    )
    # sensor_geometry = om.attr_def(
    #     type=CCDSensorGeometry,
    #     default=None,
    #     cast=True
    # )
    # frame = om.attr_def(
    #     type=CCDFrame,
    #     default=None,
    #     cast=True
    # )

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

    def calculate_field_free_thickness(self):
        """TBW."""
        pass

    def calculate_depletion_thickness(self):
        """TBW."""
        pass
