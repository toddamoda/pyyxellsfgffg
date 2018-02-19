"""TBW."""

from pyxel.detectors.characteristics import Characteristics


class CMOSCharacteristics(Characteristics):
    """TBW."""
    pass


# class CMOSCharacteristics:
#
#     def __init__(self,
#                  qe: float = None,
#                  eta: float = None,
#                  sv: float = None,
#                  amp: float = None,
#                  a1: float = None,
#                  a2: float = None,
#                  fwc: int = None
#                  ) -> None:
#         """
#         :param qe:
#         :param eta:
#         :param sv:
#         :param amp:
#         :param a1:
#         :param a2:
#         """
#
#         self.qe = qe                            # quantum efficiency
#         self.eta = eta                          # * u.electron / u.ph       # quantum yield
#         self.sv = sv                            # * u.V / u.electron        # sensitivity of output amplifier [V/-e]
#         self.amp = amp                          # * u.V / u.V               # output amplifier gain
#         self.a1 = a1                            # * u.V / u.V               # gain of the signal processor
#         self.a2 = a2                            # * u.adu / u.V             # gain of the ADC
#         self.fwc = fwc        # * u.electrons             # full well capacity (parallel)
#
#     def __getstate__(self):
#         return {'qe': self.qe,
#                 'eta': self.eta,
#                 'sv': self.sv,
#                 'amp': self.amp,
#                 'a1': self.a1,
#                 'a2': self.a2,
#                 'fwc_parallel': self.fwc,
#                 }
#
#     # TODO: create unittests for this method
#     def __eq__(self, obj):
#         assert isinstance(obj, CMOSCharacteristics)
#         return self.__getstate__() == obj.__getstate__()
