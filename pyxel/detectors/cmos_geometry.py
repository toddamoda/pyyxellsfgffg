"""TBW."""


from pyxel.detectors.geometry import Geometry


class CMOSGeometry(Geometry):
    """TBW."""

    def __init__(self,
                 n_output: int = None,
                 n_row_overhead: int = None,
                 n_frame_overhead: int = None,
                 reverse_scan_direction: bool = None,
                 reference_pixel_border_width: int = None,
                 **kwargs) -> None:
        """TBW.

        :param n_output:
        :param n_row_overhead:
        :param n_frame_overhead:
        :param reverse_scan_direction:
        :param reference_pixel_border_width:
        :param kwargs:
        """
        super().__init__(**kwargs)

        # CMOS specific geometry parameters
        self.n_row_overhead = n_row_overhead
        self.n_frame_overhead = n_frame_overhead
        self.n_output = n_output
        self.reverse_scan_direction = reverse_scan_direction
        self.reference_pixel_border_width = reference_pixel_border_width

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
