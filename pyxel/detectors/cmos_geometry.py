"""TBW."""
import pyxel
import esapy_config as om

from pyxel.detectors.geometry import Geometry


@pyxel.detector_class
class CMOSGeometry(Geometry):
    """TBW."""

    n_output = om.attr_def(
        type=int,
        default=1,
        # converter=int,
        validator=om.validate_range(0, 32, 1)
    )

    n_row_overhead = om.attr_def(
        type=int,
        default=0,
        # converter=int,
        validator=om.validate_range(0, 100, 1)
    )

    n_frame_overhead = om.attr_def(
        type=int,
        default=0,
        # converter=int,
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
        # converter=int,
        validator=om.validate_range(0, 32, 1)
    )
