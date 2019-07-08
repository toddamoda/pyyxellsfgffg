"""Geometry class for detector."""
from ..util import config, validators


@config.detector_class
class Geometry:
    """Geometrical attributes of the detector."""

    row = config.attribute(
        type=int,
        default=0,
        validator=[validators.validate_type(int, is_optional=False),
                   validators.validate_range(0, 10000)],
        doc='Number of pixel rows'
    )
    col = config.attribute(
        type=int,
        default=0,
        validator=[validators.validate_type(int, is_optional=False),
                   validators.validate_range(0, 10000)],
        doc='Number of pixel columns'
    )
    total_thickness = config.attribute(
        type=float,
        default=0.0,
        validator=[validators.validate_type(float, is_optional=True),
                   validators.validate_range(0, 10000)],
        metadata={'units': 'um'},
        doc='Thickness of detector'
    )
    pixel_vert_size = config.attribute(
        type=float,
        default=0.0,
        validator=[validators.validate_type(float, is_optional=False),
                   validators.validate_range(0, 1000)],
        metadata={'units': 'um'},
        doc='Vertical dimension of pixel'
    )
    pixel_horz_size = config.attribute(
        type=float,
        default=0.0,
        validator=[validators.validate_type(float, is_optional=False),
                   validators.validate_range(0, 1000)],
        metadata={'units': 'um'},
        doc='Horizontal dimension of pixel'
    )

    @property
    def horz_dimension(self):
        """Get total horizontal dimension of detector. Calculated automatically.

        :return: horizontal dimension
        """
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self):
        """Get total vertical dimension of detector. Calculated automatically.

        :return: vertical dimension
        """
        return self.pixel_vert_size * self.row
