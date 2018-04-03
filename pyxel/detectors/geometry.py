"""Geometry class for detector."""
import esapy_config as om


@om.attr_class
class Geometry:
    """TBW."""

    row = om.attr_def(
        type=int,
        default=0,
        cast=True,
        validate=om.check_range(0, 10000, 1, False)
    )
    col = om.attr_def(
        type=int,
        default=0,
        cast=True,
        validate=om.check_range(0, 10000, 1, False)
    )
    depletion_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    field_free_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    total_thickness = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    pixel_vert_size = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )
    pixel_horz_size = om.attr_def(
        type=float,
        default=0.0,
        cast=True,
        units='um',
        validate=om.check_range(0.0, 1000.0, 0.1, False)
    )

    # bias_voltage = om.attr_def(
    #     type=float,
    #     default=0.0,
    #     cast=True,
    #     units='V',
    #     validate=om.check_range(0.0, 40.0, 0.001, False)
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
