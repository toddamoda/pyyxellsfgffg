"""TBW."""
from ..util import config, validators


@config.detector_class
class Environment:
    """Environmental attributes of the detector."""

    temperature = config.attribute(
        type=float,
        default=273.15,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0, 1000)],
        metadata={'units': 'K'},
        doc='Temperature of the detector'
    )
    total_ionising_dose = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0, 1.e15)],
        metadata={'units': 'MeV/g'},
        doc='Total Ionising Dose (TID) of the detector'
    )
    total_non_ionising_dose = config.attribute(
        type=float,
        default=0.0,
        converter=float,
        validator=[validators.validate_type(float),
                   validators.validate_range(0, 1.e15)],
        metadata={'units': 'MeV/g'},
        doc='Total Non-Ionising Dose (TNID) of the detector'
    )
