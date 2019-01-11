"""Geometry class for detector."""
import pyxel as pyx


@pyx.detector_class
class Geometry:
    """Geometrical attributes of the detector."""

    row = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int, is_optional=False),
                   pyx.validate_range(0, 10000)],
        doc='Number of pixel rows'
    )
    col = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int, is_optional=False),
                   pyx.validate_range(0, 10000)],
        doc='Number of pixel columns'
    )
    # depletion_thickness = pyx.attribute(
    #     type=float,
    #     default=0.0,
    #     validator=[pyx.validate_type(float, is_optional=True),
    #                pyx.validate_range(0, 10000)],
    #     metadata={'units': 'um'},
    #     doc='Thickness of charge depleted semiconductor'
    # )
    # field_free_thickness = pyx.attribute(
    #     type=float,
    #     default=0.0,
    #     validator=[pyx.validate_type(float, is_optional=True),
    #                pyx.validate_range(0, 10000)],
    #     metadata={'units': 'um'},
    #     doc='Thickness of field free region in semiconductor'
    # )
    total_thickness = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=True),
                   pyx.validate_range(0, 10000)],
        metadata={'units': 'um'},
        doc='Thickness of detector'
    )
    pixel_vert_size = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=False),
                   pyx.validate_range(0, 1000)],
        metadata={'units': 'um'},
        doc='Vertical dimension of pixels'
    )
    pixel_horz_size = pyx.attribute(
        type=float,
        default=0.0,
        validator=[pyx.validate_type(float, is_optional=False),
                   pyx.validate_range(0, 1000)],
        metadata={'units': 'um'},
        doc='Horizontal dimension of pixels'
    )

    @property
    def horz_dimension(self):
        """Total horizontal dimension of detector."""
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self):
        """Total vertical dimension of detector."""
        return self.pixel_vert_size * self.row
