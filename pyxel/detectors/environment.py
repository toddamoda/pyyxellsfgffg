"""TBW."""
import pyxel
import esapy_config as om


@pyxel.detector_class
class Environment:
    """TBW."""

    temperature = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.00, 400.0, 0.01, False),
        metadata={'units': 'K'}
    )

    total_ionising_dose = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        metadata={'units': 'MeV/g'}
    )

    total_non_ionising_dose = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        metadata={'units': 'MeV/g'}
    )
