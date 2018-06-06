"""TBW."""
import esapy_config as om


@om.attr_class
class Characteristics:
    """TBW."""

    qe = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='quantum efficiency'
    )

    eta = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='quantum yield'
    )

    sv = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='sensitivity of CCD amplifier',
        metadata={'units': 'V/-e'}
    )

    amp = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 0.01, False),
        doc='output amplifier gain',
    )

    a1 = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 100.0, 1.0, False),
        doc='gain of the signal processor',
    )

    a2 = om.attr_def(
        type=float,
        default=0.0,
        converter=float,
        validator=om.validate_range(0.0, 65536.0, 1.0, False),
        # validate=om.check_range(0.0, 10.0, 0.01, False),
        doc='gain of the ADC',
    )

    fwc = om.attr_def(
        type=int,
        default=0,
        converter=int,
        validator=om.validate_range(0, 1000000, 1, False),
        doc='full well capacity (parallel)',
        metadata={'units': 'electrons'}
    )
    #
    # def __init__(self,
    #              qe: float = None,
    #              eta: float = None,
    #              sv: float = None,
    #              amp: float = None,
    #              a1: float = None,
    #              a2: float = None,
    #              fwc: int = None,
    #              **invalid_kwargs) -> None:  # TODO: should we allow bad arguments to be passed??
    #     """TBW.
    #
    #     :param qe:
    #     :param eta:
    #     :param sv:
    #     :param amp:
    #     :param a1:
    #     :param a2:
    #     :param fwc:
    #     """
    #     self.qe = qe                            # quantum efficiency
    #     self.eta = eta                          # * u.electron / u.ph       # quantum yield
    #     self.sv = sv                            # * u.V / u.electron        # sensitivity of CCD amplifier [V/-e]
    #     self.amp = amp                          # * u.V / u.V               # output amplifier gain
    #     self.a1 = a1                            # * u.V / u.V               # gain of the signal processor
    #     self.a2 = a2                            # * u.adu / u.V             # gain of the ADC
    #     self.fwc = fwc                          # * u.electrons             # full well capacity (parallel)

    def copy(self):
        """TBW."""
        return Characteristics(**self.__getstate__())

    def __getstate__(self):
        """TBW."""
        return {'qe': self.qe,
                'eta': self.eta,
                'sv': self.sv,
                'amp': self.amp,
                'a1': self.a1,
                'a2': self.a2,
                'fwc': self.fwc}

    # TODO: create unittests for this method
    def __eq__(self, obj):
        """TBW."""
        assert isinstance(obj, Characteristics)
        return self.__getstate__() == obj.__getstate__()
