"""Geometry class for detector."""
import pyxel as pyx
# from esapy_sensor.sensor_ccd import CCDSensorGeometry, CCDFrame


@pyx.detector_class
class Geometry:
    """TBW."""

    row = pyx.attribute(
        type=int,       # just for your information
        default=0,
        validator=[pyx.validate_type(int, is_optional=False),
                   pyx.validate_range(0, 10000)]
    )
    col = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int, is_optional=False),
                   pyx.validate_range(0, 10000)]
    )
    depletion_thickness = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=True),
                   pyx.validate_range(0, 10000)],
        metadata={'units': 'um'}
    )
    field_free_thickness = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=True),
                   pyx.validate_range(0, 10000)],
        metadata={'units': 'um'}
    )
    total_thickness = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=True),
                   pyx.validate_range(0, 10000)],
        metadata={'units': 'um'}
    )
    pixel_vert_size = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=False),
                   pyx.validate_range(0, 1000)],
        metadata={'units': 'um'}
    )
    pixel_horz_size = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=False),
                   pyx.validate_range(0, 1000)],
        metadata={'units': 'um'}
    )
    # n_acceptor = pyx.attribute(
    #     type=float,
    #     default=0.0,
    #     validator=pyx.validate_range(0.0, 1000.0, 0.1, False),
    #     metadata={'units': 'cm-3'}
    # )
    # n_donor = pyx.attribute(
    #     type=float,
    #     default=0.0,
    #     validator=pyx.validate_range(0.0, 1000.0, 0.1, False),
    #     metadata={'units': 'cm-3'}
    # )
    # bias_voltage = pyx.attribute(
    #     type=float,
    #     default=0.0,
    #     validator=pyx.validate_range(0.0, 40.0, 0.001, False),
    #     metadata={'units': 'V'}
    # )
    # readout_nodes = pyx.attribute(
    #     type=int,
    #     default=1,
    #     validator=pyx.validate_range(1, 4, 1, False)
    # )
    # sensor_geometry = pyx.attribute(
    #     type=CCDSensorGeometry,
    #     default=None,
    # )
    # frame = pyx.attribute(
    #     type=CCDFrame,
    #     default=None,
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
