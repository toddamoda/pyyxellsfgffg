"""TBW."""
import esapy_config as om

from pyxel.detectors.geometry import Geometry


@om.attr_class
class CMOSGeometry(Geometry):
    """TBW."""

    n_output = om.attr_def(
        type=int,
        default=1,
        converter=int,
        validator=om.validate_range(0, 32, 1)
    )

    n_row_overhead = om.attr_def(
        type=int,
        default=0,
        converter=int,
        validator=om.validate_range(0, 100, 1)
    )

    n_frame_overhead = om.attr_def(
        type=int,
        default=0,
        converter=int,
        validator=om.validate_range(0, 100, 1)
    )

    reverse_scan_direction = om.attr_def(
        type=bool,
        default=False,
        converter=bool,
        validator=om.validate_range(0, 1, 1)
    )

    reference_pixel_border_width = om.attr_def(
        type=int,
        default=4,
        converter=int,
        validator=om.validate_range(0, 32, 1)
    )

    # def __init__(self,
    #              n_output: int = None,
    #              n_row_overhead: int = None,
    #              n_frame_overhead: int = None,
    #              reverse_scan_direction: bool = None,
    #              reference_pixel_border_width: int = None,
    #              **kwargs) -> None:
    #     """TBW.
    #
    #     :param n_output:
    #     :param n_row_overhead:
    #     :param n_frame_overhead:
    #     :param reverse_scan_direction:
    #     :param reference_pixel_border_width:
    #     :param kwargs:
    #     """
    #     super().__init__(**kwargs)
    #
    #     # CMOS specific geometry parameters
    #     self.n_row_overhead = n_row_overhead
    #     self.n_frame_overhead = n_frame_overhead
    #     self.n_output = n_output
    #     self.reverse_scan_direction = reverse_scan_direction
    #     self.reference_pixel_border_width = reference_pixel_border_width

    def copy(self):
        """TBW."""
        return CMOSGeometry(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        states = super().__getstate__()
        cmos_states = {
            'n_output': self.n_output,
            'n_row_overhead': self.n_row_overhead,
            'n_frame_overhead': self.n_frame_overhead,
            'reverse_scan_direction': self.reverse_scan_direction,
            'reference_pixel_border_width': self.reference_pixel_border_width
        }
        return {**states, **cmos_states}
