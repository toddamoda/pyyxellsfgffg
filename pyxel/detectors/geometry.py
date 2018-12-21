"""Geometry class for detector."""
import pyxel
import esapy_config as om

# from esapy_sensor.sensor_ccd import CCDSensorGeometry, CCDFrame


@pyxel.detector_class
class Geometry:
    """TBW."""

    row = om.attr_def(
        type=int,       # just for your information
        default=0,
        validator=[om.validate_type(int, is_optional=False),
                   om.validate_range(0, 10000, 1, False)]
    )
    col = om.attr_def(
        type=int,
        default=0,
        validator=[om.validate_type(int, is_optional=False),
                   om.validate_range(0, 10000, 1, False)]
    )
    depletion_thickness = om.attr_def(
        type=float,
        default=0.0,
        validator=[om.validate_type(float, is_optional=True),
                   om.validate_range(0, 10000, 0.001, False)],
        metadata={'units': 'um'}
    )
    field_free_thickness = om.attr_def(
        type=float,
        default=0.0,
        validator=[om.validate_type(float, is_optional=True),
                   om.validate_range(0, 10000, 0.001, False)],
        metadata={'units': 'um'}
    )
    total_thickness = om.attr_def(
        type=float,
        default=0.0,
        validator=[om.validate_type(float, is_optional=True),
                   om.validate_range(0, 10000, 0.001, False)],
        metadata={'units': 'um'}
    )
    pixel_vert_size = om.attr_def(
        type=float,
        default=0.0,
        validator=[om.validate_type(float, is_optional=False),
                   om.validate_range(0., 1000., 0.001, False)],
        metadata={'units': 'um'}
    )
    pixel_horz_size = om.attr_def(
        type=float,
        default=0.0,
        validator=[om.validate_type(float, is_optional=False),
                   om.validate_range(0., 1000., 0.001, False)],
        metadata={'units': 'um'}
    )
    # n_acceptor = om.attr_def(
    #     type=float,
    #     default=0.0,
    #
    #     validator=om.validate_range(0.0, 1000.0, 0.1, False),
    #     metadata={'units': 'cm-3'}
    # )
    # n_donor = om.attr_def(
    #     type=float,
    #     default=0.0,
    #
    #     validator=om.validate_range(0.0, 1000.0, 0.1, False),
    #     metadata={'units': 'cm-3'}
    # )
    # bias_voltage = om.attr_def(
    #     type=float,
    #     default=0.0,
    #
    #     validator=om.validate_range(0.0, 40.0, 0.001, False),
    #     metadata={'units': 'V'}
    # )
    # readout_nodes = om.attr_def(
    #     type=int,
    #     default=1,
    #     # cast=True,
    #     # units='',
    #     # validate=om.validate_range(1, 4, 1, False)
    #     validator=om.validate_range(1, 4, 1, False)
    # )
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

    @property
    def horz_dimension(self):
        """TBW."""
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self):
        """TBW."""
        return self.pixel_vert_size * self.row

    # def calculate_field_free_thickness(self):
    #     """TBW."""
    #     pass
    #
    # def calculate_depletion_thickness(self):
    #     """TBW."""
    #     pass
