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

    # def __hdimension__(self):
    #     """Total horizontal dimension of detector."""
    #     return self.pixel_horz_size * self.col
    #
    # def __vdimension__(self):
    #     """Total vertical dimension of detector."""
    #     return self.pixel_vert_size * self.row

    # horz_dimension = pyx.attribute(
    #     default=0.0,
    #     metadata={'units': 'um'},
    #     doc='Total horizontal dimension of detector; Calculated automatically, do not define in yaml!',
    #     on_get=__hdimension__,
    #     on_get_update=True
    # )
    # vert_dimension = pyx.attribute(
    #     default=0.0,
    #     metadata={'units': 'um'},
    #     doc='Total vertical dimension of detector; Calculated automatically, do not define in yaml!',
    #     on_get=__vdimension__,
    #     on_get_update=True
    # )

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
