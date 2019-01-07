"""TBW."""
import pyxel as pyx


@pyx.detector_class
class Environment:
    """TBW."""

    temperature = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0, 1000)],
        metadata={'units': 'K'},
        doc='TBW'
    )
    total_ionising_dose = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0, 1.e15)],
        metadata={'units': 'MeV/g'},
        doc='TBW'
    )
    total_non_ionising_dose = pyx.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[pyx.validate_type(float),
                   pyx.validate_range(0, 1.e15)],
        metadata={'units': 'MeV/g'},
        doc='TBW'
    )
