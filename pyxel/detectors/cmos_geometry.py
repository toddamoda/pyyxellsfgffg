"""TBW."""
import pyxel as pyx
from pyxel.detectors.geometry import Geometry


@pyx.detector_class
class CMOSGeometry(Geometry):
    """TBW."""

    n_output = pyx.attribute(
        type=int,
        default=1,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 32)]
    )
    n_row_overhead = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 100)]
    )
    n_frame_overhead = pyx.attribute(
        type=int,
        default=0,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 100)]
    )
    reverse_scan_direction = pyx.attribute(
        type=bool,
        default=False,
        converter=bool,
        validator=[pyx.validate_type(bool)]
    )
    reference_pixel_border_width = pyx.attribute(
        type=int,
        default=4,
        validator=[pyx.validate_type(int),
                   pyx.validate_range(0, 32)]
    )
