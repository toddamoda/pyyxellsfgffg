from astropy import units as u
import typing as t

from pyxel.detectors.ccd import CCD

from pyxel.util import util


class Models:

    def __init__(self, models: dict):

        new_dct = {}
        for key, value in models.items():

            if isinstance(value, str):
                func = util.evaluate_reference(value)  # type: t.Callable

            elif callable(value):
                func = value                        # type: t.Callable

            else:
                raise NotImplementedError

            new_dct[key] = func

        self.models = new_dct                   # type: t.Dict[str, t.Callable]



class DetectionPipeline:

    def __init__(self, ccd: CCD,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_transfer: Models,
                 charge_readout: Models,
                 readout_electronics: Models,
                 doc=None):
        self.ccd = ccd
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_transfer = charge_transfer
        self.charge_readout = charge_readout
        self.readout_electronics = readout_electronics



