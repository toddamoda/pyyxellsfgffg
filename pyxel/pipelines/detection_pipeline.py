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

    def __init__(self,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_transfer: Models,
                 charge_readout: Models,
                 readout_electronics: Models,
                 doc=None):
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_transfer = charge_transfer
        self.charge_readout = charge_readout
        self.readout_electronics = readout_electronics


class Processor:

    def __init__(self, ccd: CCD, pipeline: DetectionPipeline):
        self.ccd = ccd
        self.pipeline = pipeline


def run_pipeline(detector, pipeline):

    # OPTICS
    # Stage 1: Apply the Optics model(s). only '.photons' is modified
    detector.compute_photons()
    steps = ['shot_noise', 'ray_tracing', 'diffraction']
    for step in steps:
        func = pipeline.optics.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE GENERATION
    # calculate charges per pixel
    detector.compute_charge()
    steps = ['fixed_pattern_noise', 'tars', 'xray', 'snowballs', 'darkcurrent', 'hotpixel', 'particle_number']
    for step in steps:
        func = pipeline.charge_generation.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE COLLECTION
    steps = [] # ['diffusion']
    for step in steps:
        func = pipeline.charge_collection.models.get(step)
        if func:
            detector = func(detector)
    # limiting charges per pixel due to Full Well Capacity
    detector.charge_excess()

    # CHARGE TRANSFER
    steps = []
    for step in steps:
        func = pipeline.charge_transfer.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE READOUT
    detector.compute_signal()
    # TODO: Convert here the charge object list into a 2d signal array

    steps = ['output_node_noise']
    for step in steps:
        func = pipeline.charge_readout.models.get(step)
        if func:
            detector = func(detector)

    # READOUT ELECTRONICS
    detector.compute_readout_signal()
    steps = []
    for step in steps:
        func = pipeline.readout_electronics.models.get(step)
        if func:
            detector = func(detector)

    return detector
